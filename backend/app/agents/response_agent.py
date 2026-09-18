import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.models.response_action import ResponseAction

logger = logging.getLogger(__name__)


class ResponseAgent:
    """
    Containment & Remediation Playbook Agent.
    Synthesizes targeted containment and mitigation actions tailored to the attack vector,
    target assets, and severity. Strictly enforces Human-in-the-Loop approval (PRD FR-10).
    Actions are generated in 'Pending' status.
    """

    NAME = "Sentriq-Response-Agent"
    ROLE = "Containment Playbook & Human-in-the-Loop Remediation Specialist"

    @classmethod
    def generate_actions(
        cls,
        incident: Incident,
        events: List[SecurityEvent],
        investigation_findings: Dict[str, Any],
        correlation_findings: Dict[str, Any],
    ) -> List[ResponseAction]:
        """
        Formulates structured containment actions. All actions are initialized with status='Pending'.
        """
        actions: List[ResponseAction] = []
        cat = incident.attack_category
        src_ips = investigation_findings.get("observed_src_ips", [])
        dst_ips = investigation_findings.get("observed_dst_ips", [])
        dst_ports = investigation_findings.get("observed_dst_ports", [])
        users = investigation_findings.get("observed_users", [])

        primary_src = src_ips[0] if src_ips else incident.source_ip or "0.0.0.0"
        primary_dst = dst_ips[0] if dst_ips else incident.target_asset or "127.0.0.1"
        primary_port = dst_ports[0] if dst_ports else 80

        # Action 1: Network Ingress Containment (Firewall Rule)
        if primary_src and primary_src != "127.0.0.1":
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="firewall_block",
                    title=f"Perimeter Ingress Block for Malicious Origin {primary_src}",
                    description=(
                        f"Instantly drop all incoming TCP/UDP traffic from adversary host {primary_src} "
                        f"at border ingress firewalls to sever active connections."
                    ),
                    command=f"iptables -I INPUT 1 -s {primary_src} -j DROP && ufw insert 1 deny from {primary_src} to any",
                    target_entity=primary_src,
                    risk_level="Low",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

        # Action 2: Attack-Specific Countermeasures
        if cat == "Brute Force":
            # Targeted Account Lock / Session Revocation
            target_user = users[0] if users else "root"
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="account_lock",
                    title=f"Lock Targeted Account '{target_user}' & Terminate Active Sessions",
                    description=(
                        f"Temporarily lock authentication profile for '{target_user}' to prevent credential compromise "
                        f"and forcibly terminate active SSH/PAM sessions."
                    ),
                    command=f"passwd -l {target_user} && pkill -u {target_user} -9 && loginctl terminate-user {target_user}",
                    target_entity=target_user,
                    risk_level="Medium",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

            # SSH Fail2Ban Rate Limit Jail
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="service_hardening",
                    title="Enforce Aggressive SSH Jail & Rate-Limiting Policy",
                    description=(
                        "Update Fail2ban jail threshold: ban source IPs after 3 consecutive authentication failures "
                        "for 24 hours on port 22."
                    ),
                    command="fail2ban-client set sshd maxretry 3 && fail2ban-client set sshd bantime 86400",
                    target_entity="sshd.service",
                    risk_level="Low",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

        elif cat == "DoS":
            # Ingress Rate Limiting
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="rate_limit",
                    title=f"Enforce SYN Flood Ingress Rate Limiting on {primary_dst}:{primary_port}",
                    description=(
                        f"Deploy iptables hashlimit filter capping connection attempts to {primary_dst}:{primary_port} "
                        f"at 25 conn/sec with burst ceiling of 50."
                    ),
                    command=(
                        f"iptables -A INPUT -p tcp --dport {primary_port} -m conntrack --ctstate NEW "
                        f"-m limit --limit 25/s --limit-burst 50 -j ACCEPT && "
                        f"iptables -A INPUT -p tcp --dport {primary_port} -m conntrack --ctstate NEW -j DROP"
                    ),
                    target_entity=f"{primary_dst}:{primary_port}",
                    risk_level="Medium",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

            # Kernel TCP SYN Cookies
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="kernel_hardening",
                    title=f"Enable TCP SYN Cookies on Host {primary_dst}",
                    description=(
                        "Activate kernel-level SYN cookie defense to protect memory backlog queue against "
                        "SYN flood exhaustion attacks."
                    ),
                    command="sysctl -w net.ipv4.tcp_syncookies=1 && sysctl -w net.ipv4.tcp_max_syn_backlog=2048",
                    target_entity=primary_dst,
                    risk_level="Low",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

        elif cat == "Port Scan":
            # Port Scanning Blacklist
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="perimeter_blackhole",
                    title=f"Route Adversary Reconnaissance Traffic from {primary_src} to Null Route",
                    description=(
                        f"Deploy kernel null-route (blackhole) for scanner IP {primary_src} to prevent further "
                        f"topology enumeration without leaking TCP RST packets."
                    ),
                    command=f"ip route add blackhole {primary_src}/32",
                    target_entity=primary_src,
                    risk_level="Low",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

        elif cat in ["Exploitation", "Web Attack"]:
            # WAF Rule or Virtual Patch
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="waf_rule",
                    title=f"Apply ModSecurity Virtual Patching for {primary_dst}",
                    description=(
                        "Enforce strict OWASP Core Rule Set (CRS) anomaly score threshold to intercept command injection "
                        "and arbitrary code execution payloads."
                    ),
                    command=f"nginx -s reload && modsec-rules-check --enforce-paranoia 2 --target {primary_dst}",
                    target_entity=primary_dst,
                    risk_level="Medium",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

        # Action 3: Deep Containment for High / Critical Risk (Host Isolation & Forensic Dump)
        if incident.severity in ["High", "Critical"] or incident.risk_score >= 70.0:
            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="host_isolation",
                    title=f"Isolate Targeted Asset {primary_dst} into Quarantine VLAN",
                    description=(
                        f"Sever host {primary_dst} from enterprise production LAN and reassign interface to "
                        f"isolated Quarantine VLAN 999 to halt potential lateral spread. Retains SOC management tunnel."
                    ),
                    command=f"sentriq-agent isolate --host {primary_dst} --vlan 999 --allow-soc-mgmt 10.0.0.1",
                    target_entity=primary_dst,
                    risk_level="High",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

            actions.append(
                ResponseAction(
                    id=str(uuid.uuid4()),
                    incident_id=incident.id,
                    action_type="forensic_capture",
                    title=f"Acquire Volatile Memory Snapshot & Process Tree from {primary_dst}",
                    description=(
                        f"Capture uncorrupted physical memory dump and active socket handles from {primary_dst} "
                        f"for digital forensics and post-mortem analysis."
                    ),
                    command=(
                        f"sentriq-agent forensic dump --host {primary_dst} "
                        f"--out /var/sentriq/forensics/{incident.incident_code}.lime"
                    ),
                    target_entity=primary_dst,
                    risk_level="Low",
                    status="Pending",
                    created_at=datetime.now(timezone.utc),
                )
            )

        return actions


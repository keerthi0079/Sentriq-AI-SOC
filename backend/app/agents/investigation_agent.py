import logging
import re
from datetime import datetime
from typing import Any, Dict, List
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.schemas.investigation import IOCDetail

logger = logging.getLogger(__name__)


class InvestigationAgent:
    """
    AI SOC Triage & IOC Extraction Agent.
    Inspects security event telemetry to extract Indicators of Compromise (IOCs),
    characterize network flows, and identify the attack entry vector.
    """

    NAME = "Sentriq-Triage-Agent"
    ROLE = "IOC & Attack Vector Identification Specialist"

    @classmethod
    def analyze(cls, incident: Incident, events: List[SecurityEvent]) -> Dict[str, Any]:
        """
        Performs deep triage on incident events and extracts structured IOCs and entry vector.
        """
        iocs: List[IOCDetail] = []
        observed_src_ips = set()
        observed_dst_ips = set()
        observed_dst_ports = set()
        observed_protocols = set()
        observed_users = set()

        first_seen = incident.created_at
        last_seen = incident.created_at

        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: e.timestamp or datetime.min)
        if sorted_events:
            first_seen = sorted_events[0].timestamp
            last_seen = sorted_events[-1].timestamp

        # 1. Source IP IOCs
        for ev in sorted_events:
            if ev.source_ip and ev.source_ip not in observed_src_ips:
                observed_src_ips.add(ev.source_ip)
                is_internal = ev.source_ip.startswith(("10.", "172.16.", "192.168."))
                reputation = "Suspicious" if is_internal else "Malicious"
                iocs.append(
                    IOCDetail(
                        type="ip_source",
                        value=ev.source_ip,
                        reputation=reputation,
                        description=f"Adversary origin IP generating {ev.attack_type} telemetry",
                        first_seen=first_seen,
                        last_seen=last_seen,
                    )
                )

            # 2. Target IP IOCs
            if ev.destination_ip and ev.destination_ip not in observed_dst_ips:
                observed_dst_ips.add(ev.destination_ip)
                iocs.append(
                    IOCDetail(
                        type="ip_target",
                        value=ev.destination_ip,
                        reputation="Internal Asset",
                        description=f"Target network host/service receiving hostile traffic",
                        first_seen=first_seen,
                        last_seen=last_seen,
                    )
                )

            # 3. Destination Ports
            if ev.destination_port and ev.destination_port not in observed_dst_ports:
                observed_dst_ports.add(ev.destination_port)
                port_service = cls._lookup_port_service(ev.destination_port)
                iocs.append(
                    IOCDetail(
                        type="port",
                        value=str(ev.destination_port),
                        reputation="Targeted Service",
                        description=f"{port_service} service targeted during attack sequence",
                        first_seen=first_seen,
                        last_seen=last_seen,
                    )
                )

            # 4. Protocols
            if ev.protocol:
                observed_protocols.add(ev.protocol.upper())

            # 5. User accounts from explicit field or event messages
            user = ev.user_identity
            if not user and ev.message:
                match = re.search(r"user\s+([a-zA-Z0-9_\-]+)", ev.message, re.IGNORECASE)
                if match:
                    user = match.group(1)

            if user and user not in observed_users:
                observed_users.add(user)
                iocs.append(
                    IOCDetail(
                        type="identity",
                        value=user,
                        reputation="Compromised Account" if "admin" in user.lower() or "root" in user.lower() else "Targeted Account",
                        description=f"User identity targeted during authentication abuse sequence",
                        first_seen=first_seen,
                        last_seen=last_seen,
                    )
                )

        # Determine Attack Entry Vector
        entry_vector = cls._determine_entry_vector(
            incident=incident,
            src_ips=observed_src_ips,
            dst_ports=observed_dst_ports,
            protocols=observed_protocols,
            users=observed_users,
        )

        summary = (
            f"Triaged {len(sorted_events)} events across {len(observed_src_ips)} source(s) "
            f"and {len(observed_dst_ips)} target asset(s). Identified entry vector: {entry_vector}."
        )

        return {
            "agent_name": cls.NAME,
            "role": cls.ROLE,
            "summary": summary,
            "confidence": 0.94,
            "attack_entry_vector": entry_vector,
            "iocs": iocs,
            "observed_src_ips": list(observed_src_ips),
            "observed_dst_ips": list(observed_dst_ips),
            "observed_dst_ports": list(observed_dst_ports),
            "observed_protocols": list(observed_protocols),
            "observed_users": list(observed_users),
            "first_seen": first_seen.isoformat() if first_seen else None,
            "last_seen": last_seen.isoformat() if last_seen else None,
        }

    @staticmethod
    def _lookup_port_service(port: int) -> str:
        common_ports = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            445: "SMB",
            1433: "MSSQL",
            1521: "Oracle",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            6379: "Redis",
            8080: "HTTP-Proxy/Web",
            8443: "HTTPS-Alt",
        }
        return common_ports.get(port, f"Port {port}")

    @staticmethod
    def _determine_entry_vector(
        incident: Incident,
        src_ips: set,
        dst_ports: set,
        protocols: set,
        users: set,
    ) -> str:
        cat = incident.attack_category.lower()
        ports_str = ", ".join(str(p) for p in sorted(dst_ports)) if dst_ports else "unspecified ports"
        src_str = next(iter(src_ips)) if src_ips else incident.source_ip or "external IP"

        if "brute" in cat or 22 in dst_ports or 3389 in dst_ports:
            targeted = f"identity '{next(iter(users))}'" if users else "privileged service"
            return f"Remote Credential Brute-Force against {targeted} on port(s) {ports_str} originating from {src_str}"
        elif "dos" in cat or "ddos" in cat:
            proto = next(iter(protocols)) if protocols else "TCP"
            return f"Volumetric {proto} Flooding / Service Starvation against {incident.target_asset or 'gateway'} targeting port(s) {ports_str}"
        elif "scan" in cat or "recon" in cat:
            return f"Sequential Perimeter Probe & Port Discovery from {src_str} sweeping ports {ports_str}"
        elif "exploit" in cat:
            return f"Remote Code Execution / Vulnerability Exploitation targeting port(s) {ports_str} on {incident.target_asset or 'internal host'}"
        elif "web" in cat:
            return f"Application Layer Web Injection (OWASP Top 10 vector) against HTTP/S services on port(s) {ports_str}"
        else:
            return f"Anomalous {incident.attack_category} ingress activity originating from {src_str}"


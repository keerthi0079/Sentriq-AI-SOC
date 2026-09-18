import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from app.models.event import SecurityEvent


class SecurityDataGenerator:
    """
    Generates realistic benign traffic and simulated attack scenarios,
    including the PRD Section 12 Brute Force Scenario.
    All generated events are explicitly marked with `is_simulated=True`.
    """

    BENIGN_USERS = ["alice", "bob", "carol", "david", "svc-payment", "dev-operator"]
    ATTACKER_IPS = ["198.51.100.45", "203.0.113.88", "192.0.2.144", "198.51.100.201"]
    INTERNAL_IPS = ["10.0.1.10", "10.0.1.25", "10.0.1.50", "10.0.2.100", "10.0.3.15"]

    @classmethod
    def generate_benign_event(cls, timestamp: Optional[datetime] = None) -> SecurityEvent:
        """Generates a routine, benign network/security event."""
        ts = timestamp or datetime.now(timezone.utc)
        user = random.choice(cls.BENIGN_USERS)
        src_ip = f"10.0.{random.randint(1, 4)}.{random.randint(10, 250)}"
        dst_ip = random.choice(cls.INTERNAL_IPS)
        event_types = [
            ("web_request", "web_server", "HTTP", 443, "GET /api/v1/user/profile - 200 OK"),
            ("api_call", "api_gateway", "TCP", 8000, "POST /api/v1/telemetry/heartbeat - 200 OK"),
            ("auth_success", "auth_service", "TCP", 443, f"Successful SSO authentication for user '{user}'"),
            ("dns_query", "dns_resolver", "UDP", 53, f"Standard DNS query A sentriq.internal from {src_ip}"),
            ("db_query", "database", "TCP", 5432, "Executed read transaction on core_telemetry"),
        ]
        ev_type, source, proto, port, msg = random.choice(event_types)

        return SecurityEvent(
            id=str(uuid.uuid4()),
            timestamp=ts,
            source=source,
            event_type=ev_type,
            source_ip=src_ip,
            destination_ip=dst_ip,
            source_port=random.randint(30000, 65000),
            destination_port=port,
            protocol=proto,
            user_identity=user if "auth" in ev_type else None,
            attack_type="Normal",
            severity="Low",
            message=f"[SIMULATED DEMO DATA] {msg}",
            raw_features={
                "dur": round(random.uniform(0.01, 0.5), 4),
                "spkts": random.randint(4, 20),
                "dpkts": random.randint(4, 30),
                "sbytes": random.randint(200, 2500),
                "dbytes": random.randint(200, 15000),
                "rate": round(random.uniform(50.0, 500.0), 2),
                "sttl": 62,
                "dttl": 252,
            },
            is_attack=False,
            is_simulated=True,
        )

    @classmethod
    def generate_brute_force_scenario(
        cls,
        attacker_ip: str = "198.51.100.45",
        target_ip: str = "10.0.1.50",
        target_user: str = "admin",
        fail_count: int = 8,
        base_time: Optional[datetime] = None,
    ) -> List[SecurityEvent]:
        """
        PRD Section 12: Account-compromise sequence.
        Repeated failed authentication attempts followed by a successful login
        and suspicious privilege escalation.
        """
        start = base_time or (datetime.now(timezone.utc) - timedelta(minutes=15))
        events: List[SecurityEvent] = []

        # Step 1: Rapid sequence of failed logins
        for i in range(fail_count):
            event_time = start + timedelta(seconds=i * random.randint(8, 20))
            events.append(
                SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=event_time,
                    source="auth_service",
                    event_type="failed_login",
                    source_ip=attacker_ip,
                    destination_ip=target_ip,
                    source_port=49152 + i,
                    destination_port=22,
                    protocol="TCP",
                    user_identity=target_user,
                    attack_type="Brute Force",
                    severity="High" if i >= 3 else "Medium",
                    message=f"[SIMULATED DEMO DATA] Authentication failure #{i+1} for user '{target_user}' from {attacker_ip} (invalid credentials)",
                    raw_features={
                        "dur": round(random.uniform(0.8, 1.5), 3),
                        "spkts": random.randint(12, 22),
                        "dpkts": random.randint(10, 20),
                        "sbytes": random.randint(1200, 2200),
                        "dbytes": random.randint(1500, 2500),
                        "rate": round(random.uniform(25.0, 45.0), 2),
                        "sttl": 62,
                        "dttl": 252,
                        "ct_dst_sport_ltm": i + 1,
                        "ct_src_dport_ltm": i + 1,
                    },
                    is_attack=True,
                    is_simulated=True,
                )
            )

        # Step 2: Successful authentication from the attacker IP
        success_time = start + timedelta(seconds=fail_count * 15 + 10)
        events.append(
            SecurityEvent(
                id=str(uuid.uuid4()),
                timestamp=success_time,
                source="auth_service",
                event_type="suspicious_login_success",
                source_ip=attacker_ip,
                destination_ip=target_ip,
                source_port=49152 + fail_count,
                destination_port=22,
                protocol="TCP",
                user_identity=target_user,
                attack_type="Brute Force",
                severity="Critical",
                message=f"[SIMULATED DEMO DATA] Successful authentication for '{target_user}' from {attacker_ip} immediately following {fail_count} failures",
                raw_features={
                    "dur": 2.45,
                    "spkts": 35,
                    "dpkts": 42,
                    "sbytes": 3800,
                    "dbytes": 6200,
                    "rate": 31.4,
                    "sttl": 62,
                    "dttl": 252,
                    "ct_dst_sport_ltm": fail_count + 1,
                    "ct_src_dport_ltm": fail_count + 1,
                },
                is_attack=True,
                is_simulated=True,
            )
        )

        # Step 3: Privilege change / sudo execution
        priv_time = success_time + timedelta(seconds=25)
        events.append(
            SecurityEvent(
                id=str(uuid.uuid4()),
                timestamp=priv_time,
                source="endpoint_audit",
                event_type="privilege_escalation",
                source_ip=attacker_ip,
                destination_ip=target_ip,
                source_port=49152 + fail_count + 1,
                destination_port=22,
                protocol="TCP",
                user_identity=target_user,
                attack_type="Exploitation",
                severity="Critical",
                message=f"[SIMULATED DEMO DATA] Elevated privilege execution: 'sudo -i' invoked by user '{target_user}' session from {attacker_ip}",
                raw_features={
                    "dur": 0.55,
                    "spkts": 14,
                    "dpkts": 16,
                    "sbytes": 1420,
                    "dbytes": 2100,
                    "rate": 54.5,
                    "sttl": 62,
                    "dttl": 252,
                },
                is_attack=True,
                is_simulated=True,
            )
        )

        return events

    @classmethod
    def generate_dos_scenario(
        cls,
        attacker_ip: str = "203.0.113.88",
        target_ip: str = "10.0.1.10",
        packet_burst: int = 6,
    ) -> List[SecurityEvent]:
        """Generates volumetric DoS flood burst events."""
        events: List[SecurityEvent] = []
        now = datetime.now(timezone.utc)
        for i in range(packet_burst):
            events.append(
                SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(seconds=(packet_burst - i) * 3),
                    source="perimeter_firewall",
                    event_type="syn_flood_burst",
                    source_ip=attacker_ip,
                    destination_ip=target_ip,
                    source_port=random.randint(1024, 65000),
                    destination_port=443,
                    protocol="TCP",
                    user_identity=None,
                    attack_type="DoS",
                    severity="High" if i < packet_burst - 1 else "Critical",
                    message=f"[SIMULATED DEMO DATA] Inbound SYN flood burst #{i+1} from {attacker_ip} targeting port 443 at 450,000 pps",
                    raw_features={
                        "dur": 0.05,
                        "spkts": 12000,
                        "dpkts": 0,
                        "sbytes": 720000,
                        "dbytes": 0,
                        "rate": 240000.0,
                        "sttl": 254,
                        "dttl": 0,
                        "ct_dst_ltm": 45,
                        "ct_srv_dst": 45,
                    },
                    is_attack=True,
                    is_simulated=True,
                )
            )
        return events

    @classmethod
    def generate_port_scan_scenario(
        cls,
        attacker_ip: str = "192.0.2.144",
        target_ip: str = "10.0.1.25",
    ) -> List[SecurityEvent]:
        """Generates rapid port reconnaissance probe across common services."""
        ports = [21, 22, 23, 25, 53, 80, 110, 443, 3389, 8080]
        events: List[SecurityEvent] = []
        now = datetime.now(timezone.utc)
        for idx, port in enumerate(ports):
            events.append(
                SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(seconds=(len(ports) - idx) * 2),
                    source="ids_sensor",
                    event_type="port_scan_probe",
                    source_ip=attacker_ip,
                    destination_ip=target_ip,
                    source_port=55000 + idx,
                    destination_port=port,
                    protocol="TCP",
                    user_identity=None,
                    attack_type="Port Scan",
                    severity="Medium",
                    message=f"[SIMULATED DEMO DATA] TCP SYN port probe to {target_ip}:{port} from reconnaissance scanner {attacker_ip}",
                    raw_features={
                        "dur": 0.001,
                        "spkts": 2,
                        "dpkts": 0,
                        "sbytes": 120,
                        "dbytes": 0,
                        "rate": 2000.0,
                        "sttl": 254,
                        "dttl": 0,
                        "ct_dst_sport_ltm": idx + 1,
                        "ct_src_dport_ltm": idx + 1,
                    },
                    is_attack=True,
                    is_simulated=True,
                )
            )
        return events


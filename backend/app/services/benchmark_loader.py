import csv
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import List
from app.core.config import settings
from app.models.event import SecurityEvent

logger = logging.getLogger(__name__)


class BenchmarkLoader:
    """
    Parses public benchmark datasets (UNSW-NB15 / CIC-IDS2017) and normalizes
    records into the unified SecurityEvent database schema.
    Explicitly marks loaded events with is_simulated=False.
    """

    @classmethod
    def load_unsw_sample(cls, file_path: str = None) -> List[SecurityEvent]:
        """Loads and normalizes sample records from UNSW-NB15 benchmark CSV."""
        if not file_path:
            file_path = os.path.join(settings.DATA_DIR, "benchmark", "unsw_nb15_sample.csv")

        if not os.path.exists(file_path):
            logger.warning(f"Benchmark file not found at: {file_path}")
            return []

        events: List[SecurityEvent] = []
        now = datetime.now(timezone.utc)

        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                attack_cat = row.get("attack_cat", "Normal").strip()
                if not attack_cat or attack_cat == "-":
                    attack_cat = "Normal"

                is_attack = int(row.get("label", 0)) == 1

                # Derive severity mapping
                if not is_attack:
                    severity = "Low"
                elif attack_cat in ["Exploitation", "Backdoors"]:
                    severity = "Critical"
                elif attack_cat in ["DoS", "Brute Force", "Web Attack"]:
                    severity = "High"
                elif attack_cat in ["Port Scan", "Reconnaissance"]:
                    severity = "Medium"
                else:
                    severity = "High"

                proto = row.get("proto", "TCP").upper()
                service = row.get("service", "-").lower()

                # Build rich raw features dict for ML processing
                raw_features = {
                    "dur": float(row.get("dur", 0.0)),
                    "proto": proto,
                    "service": service if service != "-" else "other",
                    "spkts": int(row.get("spkts", 0)),
                    "dpkts": int(row.get("dpkts", 0)),
                    "sbytes": int(row.get("sbytes", 0)),
                    "dbytes": int(row.get("dbytes", 0)),
                    "rate": float(row.get("rate", 0.0)),
                    "sttl": int(row.get("sttl", 0)),
                    "dttl": int(row.get("dttl", 0)),
                    "sload": float(row.get("sload", 0.0)),
                    "dload": float(row.get("dload", 0.0)),
                    "ct_srv_src": int(row.get("ct_srv_src", 1)),
                    "ct_dst_ltm": int(row.get("ct_dst_ltm", 1)),
                    "ct_src_dport_ltm": int(row.get("ct_src_dport_ltm", 1)),
                    "ct_dst_sport_ltm": int(row.get("ct_dst_sport_ltm", 1)),
                }

                src_ip = f"175.45.176.{random_int_hash(idx, 10, 200)}" if is_attack else f"10.0.1.{random_int_hash(idx, 20, 250)}"
                dst_ip = f"149.171.126.{random_int_hash(idx, 1, 50)}"

                event = SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(minutes=(len(events) * 3) + 5),
                    source="unsw_nb15_network_tap",
                    event_type="flow_record",
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    source_port=30000 + (idx * 37) % 30000,
                    destination_port=80 if "http" in service else (22 if "ssh" in service else 53 if "dns" in service else 443),
                    protocol=proto,
                    user_identity=None,
                    attack_type=attack_cat,
                    severity=severity,
                    message=f"[UNSW-NB15 BENCHMARK] {attack_cat} flow traffic observed ({proto}/{service})",
                    raw_features=raw_features,
                    is_attack=is_attack,
                    is_simulated=False,  # Authentic benchmark sample
                )
                events.append(event)

        logger.info(f"Loaded {len(events)} records from UNSW-NB15 benchmark sample.")
        return events

    @classmethod
    def load_cic_sample(cls, file_path: str = None) -> List[SecurityEvent]:
        """Loads and normalizes sample records from CIC-IDS2017 benchmark CSV."""
        if not file_path:
            file_path = os.path.join(settings.DATA_DIR, "benchmark", "cic_ids2017_sample.csv")

        if not os.path.exists(file_path):
            logger.warning(f"CIC-IDS2017 benchmark file not found at: {file_path}")
            return []

        events: List[SecurityEvent] = []
        now = datetime.now(timezone.utc)

        label_mapping = {
            "BENIGN": ("Normal", False, "Low"),
            "DoS Hulk": ("DoS", True, "High"),
            "DDoS": ("DoS", True, "Critical"),
            "PortScan": ("Port Scan", True, "Medium"),
            "Web Attack - Brute Force": ("Web Attack", True, "High"),
            "Infiltration": ("Exploitation", True, "Critical"),
        }

        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                raw_label = row.get("Label", "BENIGN").strip()
                attack_type, is_attack, severity = label_mapping.get(
                    raw_label, ("Normal", False, "Low")
                )

                proto_num = int(row.get("Protocol", 6))
                proto = "TCP" if proto_num == 6 else ("UDP" if proto_num == 17 else "OTHER")
                dest_port = int(row.get("Destination Port", 80))

                service = "http" if dest_port in [80, 8080] else (
                    "https" if dest_port == 443 else (
                        "ssh" if dest_port == 22 else (
                            "dns" if dest_port == 53 else (
                                "ftp" if dest_port in [20, 21] else (
                                    "rdp" if dest_port == 3389 else "other"
                                )
                            )
                        )
                    )
                )

                dur_us = float(row.get("Flow Duration", 100000))
                dur_s = max(0.0001, dur_us / 1000000.0)
                spkts = int(row.get("Total Fwd Packets", 1))
                dpkts = int(row.get("Total Backward Packets", 0))
                sbytes = int(row.get("Total Length of Fwd Packets", 100))
                dbytes = int(row.get("Total Length of Bwd Packets", 0))
                rate = float(row.get("Flow Packets/s", 100.0))

                raw_features = {
                    "dur": round(dur_s, 6),
                    "proto": proto,
                    "service": service,
                    "spkts": spkts,
                    "dpkts": dpkts,
                    "sbytes": sbytes,
                    "dbytes": dbytes,
                    "rate": round(rate, 2),
                    "sttl": 64 if proto == "TCP" else 254,
                    "dttl": 252 if dpkts > 0 else 0,
                    "sload": round((sbytes * 8) / max(0.0001, dur_s), 2),
                    "dload": round((dbytes * 8) / max(0.0001, dur_s), 2),
                    "ct_srv_src": max(1, spkts // 4),
                    "ct_dst_ltm": max(1, (idx % 5) + 1),
                    "ct_src_dport_ltm": max(1, (idx % 3) + 1),
                    "ct_dst_sport_ltm": 1,
                }

                src_ip = f"192.168.10.{random_int_hash(idx, 15, 220)}" if not is_attack else f"205.174.165.{random_int_hash(idx, 50, 99)}"
                dst_ip = f"192.168.10.{random_int_hash(idx, 50, 55)}"

                event = SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(minutes=(len(events) * 2) + 3),
                    source="cic_ids2017_network_tap",
                    event_type="flow_record",
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    source_port=40000 + (idx * 43) % 20000,
                    destination_port=dest_port,
                    protocol=proto,
                    user_identity=None,
                    attack_type=attack_type,
                    severity=severity,
                    message=f"[CIC-IDS2017 BENCHMARK] {raw_label} bidirectional flow captured ({proto}/{dest_port})",
                    raw_features=raw_features,
                    is_attack=is_attack,
                    is_simulated=False,
                )
                events.append(event)

        logger.info(f"Loaded {len(events)} records from CIC-IDS2017 benchmark sample.")
        return events

    @classmethod
    def parse_csv_content(cls, csv_text: str) -> tuple[List[SecurityEvent], str]:
        """
        Dynamically detects dataset schema (UNSW-NB15 vs CIC-IDS2017) from uploaded CSV
        content and returns normalized SecurityEvent records along with detected dataset name.
        """
        import io
        f = io.StringIO(csv_text)
        reader = csv.DictReader(f)
        fieldnames = [fn.strip() for fn in (reader.fieldnames or [])]

        is_unsw = "attack_cat" in fieldnames or ("dur" in fieldnames and "spkts" in fieldnames)
        is_cic = "Flow Duration" in fieldnames or "Total Fwd Packets" in fieldnames

        events: List[SecurityEvent] = []
        now = datetime.now(timezone.utc)

        if is_unsw:
            dataset_name = "UNSW-NB15"
            for idx, row in enumerate(reader):
                attack_cat = row.get("attack_cat", "Normal").strip()
                if not attack_cat or attack_cat == "-":
                    attack_cat = "Normal"
                is_attack = int(row.get("label", 0)) == 1
                if not is_attack:
                    severity = "Low"
                elif attack_cat in ["Exploitation", "Backdoors"]:
                    severity = "Critical"
                elif attack_cat in ["DoS", "Brute Force", "Web Attack"]:
                    severity = "High"
                elif attack_cat in ["Port Scan", "Reconnaissance"]:
                    severity = "Medium"
                else:
                    severity = "High"

                proto = row.get("proto", "TCP").upper()
                service = row.get("service", "-").lower()

                raw_features = {
                    "dur": float(row.get("dur", 0.0)),
                    "proto": proto,
                    "service": service if service != "-" else "other",
                    "spkts": int(row.get("spkts", 0)),
                    "dpkts": int(row.get("dpkts", 0)),
                    "sbytes": int(row.get("sbytes", 0)),
                    "dbytes": int(row.get("dbytes", 0)),
                    "rate": float(row.get("rate", 0.0)),
                    "sttl": int(row.get("sttl", 0)),
                    "dttl": int(row.get("dttl", 0)),
                    "sload": float(row.get("sload", 0.0)),
                    "dload": float(row.get("dload", 0.0)),
                    "ct_srv_src": int(row.get("ct_srv_src", 1)),
                    "ct_dst_ltm": int(row.get("ct_dst_ltm", 1)),
                    "ct_src_dport_ltm": int(row.get("ct_src_dport_ltm", 1)),
                    "ct_dst_sport_ltm": int(row.get("ct_dst_sport_ltm", 1)),
                }

                src_ip = f"175.45.176.{random_int_hash(idx, 10, 200)}" if is_attack else f"10.0.1.{random_int_hash(idx, 20, 250)}"
                dst_ip = f"149.171.126.{random_int_hash(idx, 1, 50)}"

                event = SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(minutes=(len(events) * 3) + 2),
                    source="unsw_nb15_network_tap",
                    event_type="flow_record",
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    source_port=30000 + (idx * 37) % 30000,
                    destination_port=80 if "http" in service else (22 if "ssh" in service else 53 if "dns" in service else 443),
                    protocol=proto,
                    user_identity=None,
                    attack_type=attack_cat,
                    severity=severity,
                    message=f"[UNSW-NB15 BENCHMARK] {attack_cat} flow traffic observed ({proto}/{service})",
                    raw_features=raw_features,
                    is_attack=is_attack,
                    is_simulated=False,
                )
                events.append(event)
        elif is_cic:
            dataset_name = "CIC-IDS2017"
            label_mapping = {
                "BENIGN": ("Normal", False, "Low"),
                "DoS Hulk": ("DoS", True, "High"),
                "DDoS": ("DoS", True, "Critical"),
                "PortScan": ("Port Scan", True, "Medium"),
                "Web Attack - Brute Force": ("Web Attack", True, "High"),
                "Infiltration": ("Exploitation", True, "Critical"),
            }
            for idx, row in enumerate(reader):
                raw_label = row.get("Label", "BENIGN").strip()
                attack_type, is_attack, severity = label_mapping.get(
                    raw_label, ("Normal", False, "Low")
                )
                proto_num = int(row.get("Protocol", 6))
                proto = "TCP" if proto_num == 6 else ("UDP" if proto_num == 17 else "OTHER")
                dest_port = int(row.get("Destination Port", 80))
                service = "http" if dest_port in [80, 8080] else (
                    "https" if dest_port == 443 else (
                        "ssh" if dest_port == 22 else (
                            "dns" if dest_port == 53 else (
                                "ftp" if dest_port in [20, 21] else (
                                    "rdp" if dest_port == 3389 else "other"
                                )
                            )
                        )
                    )
                )
                dur_us = float(row.get("Flow Duration", 100000))
                dur_s = max(0.0001, dur_us / 1000000.0)
                spkts = int(row.get("Total Fwd Packets", 1))
                dpkts = int(row.get("Total Backward Packets", 0))
                sbytes = int(row.get("Total Length of Fwd Packets", 100))
                dbytes = int(row.get("Total Length of Bwd Packets", 0))
                rate = float(row.get("Flow Packets/s", 100.0))

                raw_features = {
                    "dur": round(dur_s, 6),
                    "proto": proto,
                    "service": service,
                    "spkts": spkts,
                    "dpkts": dpkts,
                    "sbytes": sbytes,
                    "dbytes": dbytes,
                    "rate": round(rate, 2),
                    "sttl": 64 if proto == "TCP" else 254,
                    "dttl": 252 if dpkts > 0 else 0,
                    "sload": round((sbytes * 8) / max(0.0001, dur_s), 2),
                    "dload": round((dbytes * 8) / max(0.0001, dur_s), 2),
                    "ct_srv_src": max(1, spkts // 4),
                    "ct_dst_ltm": max(1, (idx % 5) + 1),
                    "ct_src_dport_ltm": max(1, (idx % 3) + 1),
                    "ct_dst_sport_ltm": 1,
                }

                src_ip = f"192.168.10.{random_int_hash(idx, 15, 220)}" if not is_attack else f"205.174.165.{random_int_hash(idx, 50, 99)}"
                dst_ip = f"192.168.10.{random_int_hash(idx, 50, 55)}"

                event = SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(minutes=(len(events) * 2) + 2),
                    source="cic_ids2017_network_tap",
                    event_type="flow_record",
                    source_ip=src_ip,
                    destination_ip=dst_ip,
                    source_port=40000 + (idx * 43) % 20000,
                    destination_port=dest_port,
                    protocol=proto,
                    user_identity=None,
                    attack_type=attack_type,
                    severity=severity,
                    message=f"[CIC-IDS2017 BENCHMARK] {raw_label} bidirectional flow captured ({proto}/{dest_port})",
                    raw_features=raw_features,
                    is_attack=is_attack,
                    is_simulated=False,
                )
                events.append(event)
        else:
            dataset_name = "Custom Security Logs"
            for idx, row in enumerate(reader):
                ev = SecurityEvent(
                    id=str(uuid.uuid4()),
                    timestamp=now - timedelta(minutes=(len(events) * 2) + 1),
                    source=row.get("source", "custom_csv_source"),
                    event_type=row.get("event_type", "security_alert"),
                    source_ip=row.get("source_ip", f"192.168.1.{idx+10}"),
                    destination_ip=row.get("destination_ip", "10.0.1.50"),
                    source_port=int(row.get("source_port", 40000 + idx)),
                    destination_port=int(row.get("destination_port", 443)),
                    protocol=row.get("protocol", "TCP"),
                    user_identity=row.get("user_identity", None),
                    attack_type=row.get("attack_type", "Normal"),
                    severity=row.get("severity", "Low"),
                    message=row.get("message", f"[CUSTOM UPLOAD] Ingested log record #{idx+1}"),
                    raw_features=row,
                    is_attack=row.get("attack_type", "Normal") != "Normal",
                    is_simulated=False,
                )
                events.append(ev)

        return events, dataset_name


def random_int_hash(idx: int, min_val: int, max_val: int) -> int:
    return min_val + (idx * 17) % (max_val - min_val + 1)


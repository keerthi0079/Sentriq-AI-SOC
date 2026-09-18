import argparse
import asyncio
from sqlalchemy import func, select
from app.core.database import AsyncSessionLocal, init_db
from app.models.event import SecurityEvent
from app.services.benchmark_loader import BenchmarkLoader
from app.services.data_generator import SecurityDataGenerator


async def main():
    parser = argparse.ArgumentParser(description="Sentriq Security Event Ingestion & Simulation CLI")
    parser.add_argument(
        "--scenario",
        choices=["brute_force", "dos", "port_scan", "benign"],
        help="Simulate a specific attack scenario",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=8,
        help="Number of events/bursts for the scenario (default: 8)",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Ingest UNSW-NB15 benchmark dataset records",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print database security event counts",
    )

    args = parser.parse_args()

    await init_db()

    async with AsyncSessionLocal() as session:
        if args.scenario:
            print(f"[*] Generating '{args.scenario}' scenario with count={args.count}...")
            if args.scenario == "brute_force":
                events = SecurityDataGenerator.generate_brute_force_scenario(fail_count=args.count)
            elif args.scenario == "dos":
                events = SecurityDataGenerator.generate_dos_scenario(packet_burst=args.count)
            elif args.scenario == "port_scan":
                events = SecurityDataGenerator.generate_port_scan_scenario()
            else:
                events = [SecurityDataGenerator.generate_benign_event() for _ in range(args.count)]

            session.add_all(events)
            await session.commit()
            print(f"[+] Ingested {len(events)} events for scenario '{args.scenario}'.")

        if args.benchmark:
            print("[*] Ingesting UNSW-NB15 benchmark sample...")
            benchmark_events = BenchmarkLoader.load_unsw_sample()
            if benchmark_events:
                session.add_all(benchmark_events)
                await session.commit()
                print(f"[+] Ingested {len(benchmark_events)} benchmark events.")
            else:
                print("[-] No benchmark events found.")

        # Always display summary if requested or after operation
        if args.summary or args.scenario or args.benchmark:
            total_q = await session.execute(select(func.count(SecurityEvent.id)))
            threat_q = await session.execute(select(func.count(SecurityEvent.id)).where(SecurityEvent.is_attack == True))
            bench_q = await session.execute(select(func.count(SecurityEvent.id)).where(SecurityEvent.is_simulated == False))

            total = total_q.scalar() or 0
            threats = threat_q.scalar() or 0
            benchmark_count = bench_q.scalar() or 0

            print("\n==========================================")
            print("  SENTRIQ SECURITY EVENT TELEMETRY STATS  ")
            print("==========================================")
            print(f"Total Security Events:     {total}")
            print(f"Threat / Malicious Events: {threats}")
            print(f"Benign Network Events:     {total - threats}")
            print(f"Authentic Benchmark Flow:  {benchmark_count}")
            print(f"Simulated Scenario Events: {total - benchmark_count}")
            print("==========================================")


if __name__ == "__main__":
    asyncio.run(main())


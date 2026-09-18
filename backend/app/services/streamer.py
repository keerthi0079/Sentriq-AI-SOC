import asyncio
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.core.database import AsyncSessionLocal
from app.core.websocket_hub import MessageType, websocket_hub
from app.ml.inference import ThreatInferenceService
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.services.correlation_engine import EventCorrelationEngine
from app.services.data_generator import SecurityDataGenerator

logger = logging.getLogger("sentriq.streamer")


class BackgroundStreamer:
    """
    Background worker simulating a near-real-time event stream.
    Generates baseline and attack traffic, performs on-the-fly ML threat detection,
    triggers deterministic risk scoring & correlation, and broadcasts live WebSocket telemetry.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackgroundStreamer, cls).__new__(cls)
            cls._instance._init_streamer()
        return cls._instance

    def _init_streamer(self):
        self.is_running: bool = False
        self.speed: int = 1  # 1x, 2x, 5x speed multiplier
        self.events_generated: int = 0
        self.threats_detected: int = 0
        self.incidents_triggered: int = 0
        self.start_time: Optional[datetime] = None
        self._task: Optional[asyncio.Task] = None
        self._scenario_queue: List[SecurityEvent] = []
        self._ml_service = ThreatInferenceService()
        self._lock = asyncio.Lock()

    async def start(self) -> Dict[str, Any]:
        """Starts the background event streaming loop if not already running."""
        async with self._lock:
            if self.is_running:
                return self.get_status()

            self.is_running = True
            self.start_time = datetime.now(timezone.utc)
            self._task = asyncio.create_task(self._stream_loop())
            logger.info(f"Background SOC telemetry stream started (speed={self.speed}x).")

        await websocket_hub.broadcast_typed(MessageType.STREAM_STATUS, self.get_status())
        return self.get_status()

    async def stop(self) -> Dict[str, Any]:
        """Stops the background event streaming loop."""
        async with self._lock:
            if not self.is_running:
                return self.get_status()

            self.is_running = False
            if self._task and not self._task.done():
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            self._task = None
            logger.info("Background SOC telemetry stream stopped.")

        await websocket_hub.broadcast_typed(MessageType.STREAM_STATUS, self.get_status())
        return self.get_status()

    async def set_speed(self, speed: int) -> Dict[str, Any]:
        """Sets the event generation speed multiplier (1x, 2x, 5x, up to 10x)."""
        valid_speed = max(1, min(10, speed))
        self.speed = valid_speed
        logger.info(f"Stream speed set to {self.speed}x")
        await websocket_hub.broadcast_typed(MessageType.STREAM_STATUS, self.get_status())
        return self.get_status()

    async def inject_scenario(self, scenario_name: str) -> Dict[str, Any]:
        """Enqueues an immediate scenario burst into the stream queue."""
        s_lower = scenario_name.lower().strip()
        now = datetime.now(timezone.utc)
        events: List[SecurityEvent] = []

        if "brute" in s_lower:
            events = SecurityDataGenerator.generate_brute_force_scenario(base_time=now)
        elif "dos" in s_lower or "flood" in s_lower:
            events = SecurityDataGenerator.generate_dos_scenario(count=15, base_time=now)
        elif "port" in s_lower or "scan" in s_lower or "recon" in s_lower:
            events = SecurityDataGenerator.generate_port_scan_scenario(base_time=now)
        else:
            # Fallback to single benign event
            events = [SecurityDataGenerator.generate_benign_event(timestamp=now)]

        async with self._lock:
            self._scenario_queue.extend(events)

        logger.info(f"Injected {len(events)} events for scenario '{scenario_name}' into stream queue.")
        await websocket_hub.broadcast_typed(
            MessageType.SYSTEM_MESSAGE,
            {
                "message": f"Scenario '{scenario_name}' queued ({len(events)} events).",
                "queue_size": len(self._scenario_queue),
            },
        )
        return {
            "status": "queued",
            "scenario": scenario_name,
            "events_queued": len(events),
            "total_queue_size": len(self._scenario_queue),
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns the current runtime telemetry state and metrics."""
        uptime_seconds = (
            (datetime.now(timezone.utc) - self.start_time).total_seconds()
            if self.start_time and self.is_running
            else 0.0
        )
        return {
            "is_running": self.is_running,
            "speed": self.speed,
            "events_generated": self.events_generated,
            "threats_detected": self.threats_detected,
            "incidents_triggered": self.incidents_triggered,
            "queue_size": len(self._scenario_queue),
            "active_clients": websocket_hub.connection_count,
            "uptime_seconds": round(uptime_seconds, 1),
        }

    async def process_event(self, event: SecurityEvent) -> Tuple[SecurityEvent, Optional[Incident]]:
        """
        Executes the full automated SOC pipeline for a single event:
        1. Persists to PostgreSQL.
        2. Performs ML threat inference.
        3. Correlates event if threat detected.
        4. Broadcasts WebSocket notifications.
        """
        # 1. Run ML inference on feature vector
        features = {
            "source": event.source,
            "event_type": event.event_type,
            "protocol": event.protocol,
            "destination_port": event.destination_port or 80,
            "source_port": event.source_port or 40000,
            **(event.raw_features or {}),
        }

        try:
            prediction = self._ml_service.predict(features)
            # If ML strongly predicts threat or event is already labeled attack
            if prediction.is_threat or event.is_attack:
                event.is_attack = True
                if prediction.is_threat and prediction.predicted_category != "Normal":
                    event.attack_type = prediction.predicted_category
        except Exception as e:
            logger.debug(f"ML inference skipped/fallback for event {event.id}: {e}")
            prediction = None

        # 2. Persist event & run correlation in database session
        incident: Optional[Incident] = None
        is_new_incident: bool = False

        async with AsyncSessionLocal() as session:
            try:
                session.add(event)
                await session.flush()

                if event.is_attack and event.attack_type != "Normal":
                    self.threats_detected += 1
                    incident = await EventCorrelationEngine.correlate_event(event, session)
                    if incident:
                        is_new_incident = (incident.event_count == 1)
                        if is_new_incident:
                            self.incidents_triggered += 1

                await session.commit()
                await session.refresh(event)
                if incident:
                    await session.refresh(incident)
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to persist streamed event: {e}")
                raise

        self.events_generated += 1

        # 3. Broadcast WebSocket Messages
        # A. Always broadcast the ingested event
        await websocket_hub.broadcast_typed(
            MessageType.EVENT_INGESTED,
            {
                "id": event.id,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
                "event_type": event.event_type,
                "source_ip": event.source_ip,
                "destination_ip": event.destination_ip,
                "destination_port": event.destination_port,
                "protocol": event.protocol,
                "attack_type": event.attack_type,
                "severity": event.severity,
                "message": event.message,
                "is_attack": event.is_attack,
                "is_simulated": event.is_simulated,
            },
        )

        # B. If it is a threat, broadcast detection alert
        if event.is_attack and event.attack_type != "Normal":
            await websocket_hub.broadcast_typed(
                MessageType.DETECTION_ALERT,
                {
                    "event_id": event.id,
                    "timestamp": event.timestamp.isoformat(),
                    "attack_category": event.attack_type,
                    "severity": event.severity,
                    "confidence": round(prediction.category_confidence, 3) if prediction else 0.94,
                    "source_ip": event.source_ip,
                    "target_asset": event.destination_ip,
                    "message": event.message,
                    "detection_reasons": prediction.detection_reasons if prediction else ["Anomalous security alert"],
                },
            )

        # C. If correlated to an incident, broadcast incident created/updated
        if incident:
            inc_payload = {
                "id": incident.id,
                "incident_code": incident.incident_code,
                "title": incident.title,
                "attack_category": incident.attack_category,
                "severity": incident.severity,
                "risk_score": round(incident.risk_score, 1),
                "risk_level": incident.risk_level,
                "status": incident.status,
                "source_ip": incident.source_ip,
                "target_asset": incident.target_asset,
                "event_count": incident.event_count,
                "created_at": incident.created_at.isoformat(),
            }
            if is_new_incident:
                await websocket_hub.broadcast_typed(MessageType.INCIDENT_CREATED, inc_payload)
            else:
                await websocket_hub.broadcast_typed(MessageType.INCIDENT_UPDATED, inc_payload)

        # D. Periodically broadcast metrics update (every 5 events)
        if self.events_generated % 5 == 0:
            await websocket_hub.broadcast_typed(
                MessageType.METRICS_UPDATE,
                {
                    "total_events": self.events_generated,
                    "threats_detected": self.threats_detected,
                    "incidents_triggered": self.incidents_triggered,
                    "stream_speed": self.speed,
                    "is_running": self.is_running,
                },
            )

        return event, incident

    async def _stream_loop(self):
        """Continuous event generation loop with variable interval based on speed."""
        logger.info("Entering background stream loop...")
        try:
            while self.is_running:
                # Determine sleep duration based on speed
                # 1x -> 1.0s, 2x -> 0.5s, 5x -> 0.2s, 10x -> 0.1s
                interval = max(0.1, 1.0 / float(self.speed))

                event_to_process: SecurityEvent
                async with self._lock:
                    if self._scenario_queue:
                        event_to_process = self._scenario_queue.pop(0)
                        # Refresh timestamp to now for queued events so they appear current
                        event_to_process.timestamp = datetime.now(timezone.utc)
                    else:
                        # 85% Benign, 15% Intermittent attack
                        if random.random() < 0.85:
                            event_to_process = SecurityDataGenerator.generate_benign_event()
                        else:
                            # Generate a single attack probe
                            attack_choice = random.choice(["brute", "dos", "scan"])
                            if attack_choice == "brute":
                                evs = SecurityDataGenerator.generate_brute_force_scenario(fail_count=1)
                                event_to_process = evs[0]
                            elif attack_choice == "dos":
                                evs = SecurityDataGenerator.generate_dos_scenario(count=1)
                                event_to_process = evs[0]
                            else:
                                evs = SecurityDataGenerator.generate_port_scan_scenario()
                                event_to_process = random.choice(evs)
                            event_to_process.timestamp = datetime.now(timezone.utc)

                # Process the event through the pipeline
                try:
                    await self.process_event(event_to_process)
                except Exception as e:
                    logger.error(f"Error during streamed event processing: {e}")

                await asyncio.sleep(interval)

        except asyncio.CancelledError:
            logger.info("Stream loop cancelled gracefully.")
        except Exception as e:
            logger.error(f"Stream loop terminated with error: {e}", exc_info=True)
            self.is_running = False


# Global singleton instance
background_streamer = BackgroundStreamer()


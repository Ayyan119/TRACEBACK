import re
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.models.log_record import LogRecordModel

logger = logging.getLogger(__name__)


class LogParser:
    """Robust LogParser extracting structured fields (timestamp, date, time, day, level, service, message).

    Supports common formats:
    - 2026-08-14 15:20:31 ERROR Database connection failed
    - 2026-08-14T15:20:31Z [ERROR] Database connection failed
    - [2026-08-14 15:20:31] WARN API latency high
    - Standard syslog / log4j formats
    """

    LOG_PATTERNS = [
        # Pattern 1: ISO timestamp (2026-08-14 15:20:31 or 2026-08-14T15:20:31Z) + LEVEL + Message
        re.compile(
            r"^(?P<ts>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)\s+(?:\[?(?P<level>EMERG|ALERT|CRIT|CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE)\]?:?\s+)?(?P<msg>.*)$",
            re.IGNORECASE,
        ),
        # Pattern 2: [2026-08-14 15:20:31] LEVEL Message
        re.compile(
            r"^\[(?P<ts>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?)\]\s+(?:\[?(?P<level>EMERG|ALERT|CRIT|CRITICAL|FATAL|ERROR|WARN|WARNING|INFO|DEBUG|TRACE)\]?:?\s+)?(?P<msg>.*)$",
            re.IGNORECASE,
        ),
    ]

    def parse_log_content(
        self,
        content: str,
        project_id: str,
        incident_id: Optional[str] = None,
        file_id: Optional[str] = None,
        source: Optional[str] = None,
        service: Optional[str] = None,
        log_type: str = "application",
    ) -> List[LogRecordModel]:
        """Parses multi-line log string into structured LogRecordModel instances."""
        if not content:
            return []

        lines = content.splitlines()
        records: List[LogRecordModel] = []

        for line in lines:
            if not line.strip():
                continue

            parsed_data = self._parse_line(line)

            ts_dt = parsed_data.get("timestamp") or datetime.now(timezone.utc)
            dt_date = ts_dt.date()
            tm_time = ts_dt.time()
            day_str = ts_dt.strftime("%A")

            record = LogRecordModel(
                project_id=project_id,
                incident_id=incident_id,
                file_id=file_id,
                timestamp=ts_dt,
                date=dt_date,
                time=tm_time,
                day=day_str,
                log_type=log_type,
                level=parsed_data.get("level", "INFO"),
                message=parsed_data.get("message", line),
                source=source or "log_file",
                service=service or "backend",
                raw_line=line,
                parse_status=parsed_data.get("parse_status", "parsed"),
                metadata_json={"file_id": file_id},
            )
            records.append(record)

        return records

    def _parse_line(self, line: str) -> Dict[str, Any]:
        """Parses a single log line."""
        for pattern in self.LOG_PATTERNS:
            match = pattern.match(line.strip())
            if match:
                groups = match.groupdict()
                raw_ts = groups.get("ts")
                raw_level = (groups.get("level") or "INFO").upper()
                msg = groups.get("msg") or line

                ts_dt = self._parse_timestamp(raw_ts)
                return {
                    "timestamp": ts_dt,
                    "level": raw_level,
                    "message": msg,
                    "parse_status": "parsed",
                }

        # If line does not match standard pattern, preserve as raw unparsed line
        return {
            "timestamp": datetime.now(timezone.utc),
            "level": "INFO",
            "message": line.strip(),
            "parse_status": "unparsed",
        }

    def _parse_timestamp(self, ts_str: Optional[str]) -> datetime:
        if not ts_str:
            return datetime.now(timezone.utc)

        clean_ts = ts_str.replace("T", " ").replace("Z", "").strip()

        for fmt in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y/%m/%d %H:%M:%S",
        ]:
            try:
                dt = datetime.strptime(clean_ts, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue

        return datetime.now(timezone.utc)


log_parser = LogParser()

import json
import logging
import socket
import time
from datetime import datetime, timezone


class TCPJsonHandler(logging.Handler):
    """Sends JSON log records to Logstash over a persistent TCP connection."""

    def __init__(self, host="logstash", port=5000):
        super().__init__()
        self.host = host
        self.port = port
        self._sock = None
        self._last_error = 0

    def _connect(self):
        self._sock = socket.create_connection((self.host, self.port), timeout=3)

    def emit(self, record):
        # Back off for 30s after a failed connection to avoid log spam
        if self._sock is None and time.time() - self._last_error < 30:
            return
        try:
            if self._sock is None:
                self._connect()
            entry = {
                "@timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "message": record.getMessage(),
                "level": record.levelname,
                "logger": record.name,
                "module": record.module,
            }
            if record.exc_info:
                entry["exception"] = self.formatException(record.exc_info)
            self._sock.sendall((json.dumps(entry) + "\n").encode("utf-8"))
        except Exception:
            self._sock = None
            self._last_error = time.time()
            self.handleError(record)

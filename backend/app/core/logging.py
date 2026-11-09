import json
import logging


class JSONFormatter(logging.Formatter):
    """JSON 格式日志"""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "froge-api",
            "message": record.getMessage(),
        }
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging():
    """初始化日志"""
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)

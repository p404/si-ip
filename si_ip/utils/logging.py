import sys
import json
import logging
from datetime import datetime
from typing import Any, Dict

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        }
        
        # Include all extra fields from record
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
                
        # Include all custom attributes
        for attr in dir(record):
            if attr not in ('args', 'asctime', 'created', 'exc_info', 'exc_text', 'filename',
                          'funcName', 'id', 'levelname', 'levelno', 'lineno', 'module',
                          'msecs', 'msecs', 'message', 'msg', 'name', 'pathname', 'process',
                          'processName', 'relativeCreated', 'stack_info', 'thread', 'threadName',
                          'extra'):
                value = getattr(record, attr)
                if not attr.startswith('_') and not callable(value):
                    log_record[attr] = value

        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging(level: int = logging.INFO) -> logging.LoggerAdapter:
    logger = logging.getLogger('si-ip')
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    
    logger.setLevel(level)
    
    return logging.LoggerAdapter(
        logger,
        {'service': 'si-ip', 'version': '1.0.0'}
    )
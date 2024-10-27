import sys
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict
from si_ip import __version__

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        }
        
        if hasattr(record, 'extra'):
            log_record.update(record.extra)
                
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

def get_log_level(level_name: str) -> int:
    """Convert string log level to logging constant"""
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    return levels.get(level_name.upper(), logging.ERROR)

def setup_logging() -> logging.LoggerAdapter:
    logger = logging.getLogger('si-ip')
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    
    # Get log level from environment or default to ERROR
    log_level = get_log_level(os.getenv('LOG_LEVEL', 'INFO'))
    logger.setLevel(log_level)
    
    return logging.LoggerAdapter(
        logger,
        {
            'service': 'si-ip',
            'version': __version__,
            'log_level': logging.getLevelName(log_level)
        }
    )
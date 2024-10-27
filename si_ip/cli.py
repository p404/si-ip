#!/usr/bin/env python3
import sys
import asyncio
from .utils.config import load_config, validate_config
from .utils.logging import setup_logging
from .core.updater import DNSUpdater

def main():
    try:
        config = load_config()
        validate_config(config)
        logger = setup_logging()
        updater = DNSUpdater(config, logger)
        
        logger.info('Starting SI-IP', extra={
            'config': {k: '***' if 'key' in k else v for k, v in config.items()},
            'operation': 'startup'
        })
        
        asyncio.run(updater.run())
        
    except KeyboardInterrupt:
        logger.info('Shutting down SI-IP', extra={
            'operation': 'shutdown',
            'shutdown_type': 'user_initiated'
        })
        return 0
    except Exception as e:
        logger.error('Fatal error', extra={
            'error': str(e),
            'error_type': type(e).__name__,
            'operation': 'startup'
        })
        return 1

if __name__ == '__main__':
    sys.exit(main())
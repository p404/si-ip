import os
import configparser
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    config = {
        'provider': os.getenv('DNS_PROVIDER', 'aws'),
        'refresh_interval': os.getenv('REFRESH_INTERVAL', '300')
    }

    parser = configparser.ConfigParser()
    config_file = os.getenv('CONFIG_FILE')
    
    if config_file and os.path.exists(config_file):
        parser.read(config_file)
        
        # Load base configuration
        if 'global' in parser:
            config['provider'] = parser.get('global', 'provider', fallback=config['provider'])
            config['refresh_interval'] = parser.get('global', 'refresh_interval', 
                                                  fallback=config['refresh_interval'])

        # Load provider-specific configuration
        if config['provider'] == 'aws':
            config.update(_load_aws_config(parser))

    # Environment variables override config file
    if config['provider'] == 'aws':
        config.update({
            'aws_access_key_id': os.getenv('AWS_ACCESS_KEY_ID', config.get('aws_access_key_id')),
            'aws_secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY', config.get('aws_secret_access_key')),
            'hosted_zone_id': os.getenv('HOSTED_ZONE_ID', config.get('hosted_zone_id')),
            'record_name': os.getenv('RECORD_NAME', config.get('record_name'))
        })

    return config

def _load_aws_config(parser: configparser.ConfigParser) -> Dict[str, str]:
    config = {}
    
    if 'aws' in parser:
        config.update({
            'aws_access_key_id': parser.get('aws', 'aws_access_key_id', fallback=''),
            'aws_secret_access_key': parser.get('aws', 'aws_secret_access_key', fallback=''),
            'hosted_zone_id': parser.get('aws', 'hosted_zone_id', fallback=''),
            'record_name': parser.get('aws', 'record_name', fallback='')
        })
    
    return config

def validate_config(config: Dict[str, Any]) -> None:
    required_fields = ['provider', 'refresh_interval']
    
    if config['provider'] == 'aws':
        required_fields.extend([
            'aws_access_key_id',
            'aws_secret_access_key',
            'hosted_zone_id',
            'record_name'
        ])

    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
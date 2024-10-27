import boto3
from typing import Optional
from botocore.exceptions import ClientError
from ..base import DNSProvider

class Route53Provider(DNSProvider):
    def __init__(self, config, logger):
        super().__init__(config, logger)
        self.session = boto3.session.Session(
            aws_access_key_id=config['aws_access_key_id'],
            aws_secret_access_key=config['aws_secret_access_key']
        )
        self.client = self.session.client('route53')

    async def record_exists(self, name: str) -> bool:
        try:
            response = self.client.list_resource_record_sets(
                HostedZoneId=self.config['hosted_zone_id'],
                StartRecordName=name,
                StartRecordType='A',
                MaxItems='1'
            )
            records = response.get('ResourceRecordSets', [])
            return any(record['Name'].rstrip('.') == name.rstrip('.') for record in records)
        except Exception as e:
            self.logger.error('Failed to check record', extra={
                'error': str(e),
                'error_type': type(e).__name__,
                'record_name': name,
                'operation': 'check_record'
            })
            return False

    async def create_record(self, name: str, ip: str) -> bool:
        try:
            response = self.client.change_resource_record_sets(
                HostedZoneId=self.config['hosted_zone_id'],
                ChangeBatch={
                    'Comment': 'Initial DNS record creation',
                    'Changes': [
                        {
                            'Action': 'CREATE',
                            'ResourceRecordSet': {
                                'Name': name,
                                'Type': 'A',
                                'TTL': int(self.config['refresh_interval']),
                                'ResourceRecords': [{'Value': ip}]
                            }
                        }
                    ]
                }
            )
            self.logger.info('Created DNS record', extra={
                'record_name': name,
                'ip': ip,
                'change_id': response['ChangeInfo']['Id'],
                'operation': 'create_record'
            })
            return True
        except ClientError as e:
            self.logger.error('Failed to create record', extra={
                'error': str(e),
                'error_type': type(e).__name__,
                'record_name': name,
                'ip': ip,
                'aws_error_code': e.response.get('Error', {}).get('Code', 'unknown'),
                'operation': 'create_record'
            })
            return False

    async def update_record(self, name: str, ip: str) -> bool:
        try:
            response = self.client.change_resource_record_sets(
                HostedZoneId=self.config['hosted_zone_id'],
                ChangeBatch={
                    'Comment': 'Automatic DNS update',
                    'Changes': [
                        {
                            'Action': 'UPSERT',
                            'ResourceRecordSet': {
                                'Name': name,
                                'Type': 'A',
                                'TTL': int(self.config['refresh_interval']),
                                'ResourceRecords': [{'Value': ip}]
                            }
                        }
                    ]
                }
            )
            self.logger.info('Updated DNS record', extra={
                'record_name': name,
                'ip': ip,
                'change_id': response['ChangeInfo']['Id'],
                'operation': 'update_record'
            })
            return True
        except ClientError as e:
            self.logger.error('Failed to update record', extra={
                'error': str(e),
                'error_type': type(e).__name__,
                'record_name': name,
                'ip': ip,
                'aws_error_code': e.response.get('Error', {}).get('Code', 'unknown'),
                'operation': 'update_record'
            })
            return False

    async def get_record_ip(self, name: str) -> Optional[str]:
        try:
            response = self.client.list_resource_record_sets(
                HostedZoneId=self.config['hosted_zone_id'],
                StartRecordName=name,
                StartRecordType='A',
                MaxItems='1'
            )
            records = response.get('ResourceRecordSets', [])
            for record in records:
                if record['Name'].rstrip('.') == name.rstrip('.') and record['Type'] == 'A':
                    return record['ResourceRecords'][0]['Value']
            return None
        except Exception as e:
            self.logger.error('Failed to get record IP', extra={
                'error': str(e),
                'error_type': type(e).__name__,
                'record_name': name,
                'operation': 'get_record_ip'
            })
            return None
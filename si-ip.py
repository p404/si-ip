#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import boto3
import logging
import argparse
import ipgetter
import threading
import dns.resolver
import ConfigParser

parser = argparse.ArgumentParser(description='SI-IP Minimal Dynamic DNS for AWS Route 53')
parser.add_argument('-c','--config', help='Loads configuration', required=True)
args = vars(parser.parse_args())

if args['config']:
    config = ConfigParser.ConfigParser()
    config.read(args['config'])

    AWS_ACCESS_KEY   = config.get('global', 'aws_access_key_id')
    AWS_SECRET_KEY   = config.get('global', 'aws_secret_access_key')
    HOST_ZONE_ID     = config.get('records', 'hosted_zone_id') 
    RECORD_NAME      = config.get('records', 'record_name')
    REFRESH_INTERVAL = config.get('records', 'refresh_interval')

    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler) 
    logger.setLevel(logging.INFO)
    logger.info('Starting SI-IP') 

    def resolve_name_ip(name):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [
            '1.1.1.1',
            '8.8.4.4'
        ]
        answer = resolver.query(name)
        return answer.response.answer[0].items[0].address

    def update_dns_record():
        threading.Timer(float(REFRESH_INTERVAL), update_dns_record).start()
        ip = ipgetter.myip()
        resolved_ip = resolve_name_ip(RECORD_NAME)

        if ip != resolved_ip:     
            session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
            client = session.client('route53')
            client.change_resource_record_sets(
                HostedZoneId= HOST_ZONE_ID,
                ChangeBatch={
                    "Comment": "Automatic DNS update",
                    "Changes": [
                        {
                            "Action": "UPSERT",
                            "ResourceRecordSet": {
                                "Name": RECORD_NAME,
                                "Type": "A",
                                "TTL": int(REFRESH_INTERVAL),
                                "ResourceRecords": [
                                    {
                                        "Value": ip
                                    },
                                ],
                            }
                        },
                    ]
                }
            )
            logger.info('IP Changed from {} to {}'.format(resolved_ip, ip))

    update_dns_record()
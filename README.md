# SI-IP

SI-IP Is a A Dynamic DNS updater built on top of AWS Route 53.

## Installing
```bash
1. git clone https://github.com/p404/si-ip.git
2. cd si-ip
3. pip install -r requirements.txt
```
## How to use
```bash
usage: si-ip.py [-h] -c CONFIG

SI-IP Minimal Dynamic DNS for AWS Route 53

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Loads configuration
```
## Configuration example
config.ini
```bash
[global]
aws_access_key_id     = <AWS KEY>
aws_secret_access_key = <AWS KEY SECRET>
local_ip_resolver     = <ifconfig.co or ipgetter>
[records]
refresh_interval      = <REFRESH INTERVAL IN SECONDS>
hosted_zone_id        = <AWS ZONE ID>
record_name           = <AWS RECORD NAME>
```
## License
[MIT](https://github.com/p404/si-ip/blob/master/LICENSE)

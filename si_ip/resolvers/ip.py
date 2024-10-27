import re
import random
import asyncio
import aiohttp
from typing import Optional, Dict
from datetime import datetime, timedelta

class IPResolver:
    IP_PATTERN = re.compile(r'(?:\d{1,3}\.){3}\d{1,3}')
    
    SERVERS = {
        'https://api.ipify.org': {'weight': 10, 'retries': 0},
        'https://icanhazip.com': {'weight': 9, 'retries': 0},
        'https://ifconfig.me/ip': {'weight': 8, 'retries': 0},
        'https://ipecho.net/plain': {'weight': 7, 'retries': 0},
        'https://myexternalip.com/raw': {'weight': 6, 'retries': 0}
    }

    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=2)
        self.headers = {
            'User-Agent': 'SI-IP Dynamic DNS updater',
            'Accept': 'text/plain'
        }
        self.failed_servers: Dict[str, datetime] = {}
        self.retry_after = timedelta(hours=1)
        self.max_retries = 3

    async def get_ip(self) -> str:
        servers = self._get_available_servers(3)
        if not servers:
            await asyncio.sleep(300)  # Wait 5 minutes if all servers are blocked
            servers = self._get_available_servers(3)
            if not servers:
                raise RuntimeError("No available IP resolution servers")

        async with aiohttp.ClientSession(headers=self.headers) as session:
            tasks = [self._fetch_ip(session, server) for server in servers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_ips = [ip for ip in results if isinstance(ip, str) and ip]
            if not valid_ips:
                raise RuntimeError("Failed to fetch IP from any server")
                
            return max(set(valid_ips), key=valid_ips.count)

    async def _fetch_ip(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status in {429, 403, 503}:
                    self._mark_server_failed(url)
                    return None
                    
                if response.status != 200:
                    return None
                
                content = await response.text()
                match = self.IP_PATTERN.search(content)
                return match.group(0) if match else None
                
        except Exception:
            self._mark_server_failed(url)
            return None

    def _mark_server_failed(self, server: str) -> None:
        self.SERVERS[server]['retries'] += 1
        if self.SERVERS[server]['retries'] >= self.max_retries:
            self.failed_servers[server] = datetime.now()

    def _get_available_servers(self, count: int) -> list:
        available = [
            server for server in self.SERVERS 
            if server not in self.failed_servers or 
            datetime.now() - self.failed_servers[server] > self.retry_after
        ]
        
        if not available:
            return []
            
        return random.sample(available, min(count, len(available)))
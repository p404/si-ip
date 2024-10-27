from abc import ABC, abstractmethod
from typing import Optional

class DNSProvider(ABC):
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    @abstractmethod
    async def record_exists(self, name: str) -> bool:
        """Check if record exists"""
        pass

    @abstractmethod
    async def create_record(self, name: str, ip: str) -> bool:
        """Create a new DNS record"""
        pass

    @abstractmethod
    async def update_record(self, name: str, ip: str) -> bool:
        """Update existing DNS record"""
        pass

    @abstractmethod
    async def get_record_ip(self, name: str) -> Optional[str]:
        """Get current IP from DNS record"""
        pass
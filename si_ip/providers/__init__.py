from typing import Type
from .base import DNSProvider
from .aws.route53 import Route53Provider

PROVIDERS = {
    'aws': Route53Provider
}

def get_provider(provider_name: str) -> Type[DNSProvider]:
    provider = PROVIDERS.get(provider_name.lower())
    if not provider:
        raise ValueError(f"Provider '{provider_name}' not supported. Available providers: {', '.join(PROVIDERS.keys())}")
    return provider
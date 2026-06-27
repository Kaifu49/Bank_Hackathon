import ssl
import certifi

_original = ssl.create_default_context

def fixed_context(*args, **kwargs):
    return _original(cafile=certifi.where())

ssl.create_default_context = fixed_context

import aiohttp

print("aiohttp imported successfully")
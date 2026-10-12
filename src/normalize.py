"""Conservative normalization; never connects to indicator destinations."""
import ipaddress
import re
from urllib.parse import urlsplit

def normalize_url(original):
    if not isinstance(original, str) or not original:
        raise ValueError("URL must be a nonempty string")
    if any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in original):
        raise ValueError("Whitespace or control character")
    if "\\" in original:
        raise ValueError("Backslash is ambiguous")
    match = re.fullmatch(r"(https?)://([^/?#]+)(.*)", original, re.I)
    if not match:
        raise ValueError("Absolute HTTP/HTTPS URL required")
    parts = urlsplit(original)
    if parts.username is not None or parts.password is not None:
        raise ValueError("URLs with credentials are unsupported")
    host = parts.hostname
    if not host:
        raise ValueError("Missing hostname")
    port = parts.port
    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid port")
    if parts.netloc.endswith(":"):
        raise ValueError("Empty port")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        labels = host.rstrip(".").split(".")
        if len(host) > 253 or any(
            not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", label)
            for label in labels
        ):
            raise ValueError("Invalid or unsupported hostname")
    # Preserve the suffix exactly, excluding fragments not sent in HTTP requests.
    suffix = match[3].split("#", 1)[0]
    normalized = match[1].lower() + "://" + match[2].lower() + suffix
    return {
        "original_url": original,
        "normalized_url": normalized,
        "hostname": host.lower(),
    }

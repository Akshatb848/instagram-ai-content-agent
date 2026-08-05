import hashlib
import html
import ipaddress
import re
import socket
from dataclasses import dataclass
from datetime import UTC, datetime
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "ref", "source"}
INJECTION_PATTERNS = (
    re.compile(r"ignore (all|any|the|previous) (instructions|rules)", re.I),
    re.compile(r"system\s*(prompt|message)", re.I),
    re.compile(r"reveal\s+(secrets?|tokens?|credentials?)", re.I),
)


@dataclass(frozen=True)
class NormalizedItem:
    title: str
    canonical_url: str
    author: str | None
    published_at: datetime
    raw_text: str
    normalized_text: str
    content_hash: str


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        raise ValueError("Only absolute HTTP(S) URLs are accepted")
    host = parts.hostname.lower().rstrip(".")
    port = parts.port
    netloc = (
        host
        if not port
        or (parts.scheme == "http" and port == 80)
        or (parts.scheme == "https" and port == 443)
        else f"{host}:{port}"
    )
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k.lower() not in TRACKING_KEYS and not k.lower().startswith(TRACKING_PREFIXES)
    ]
    path = re.sub(r"/{2,}", "/", parts.path or "/")
    if path != "/":
        path = path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), netloc, path, urlencode(sorted(query)), ""))


def normalize_text(value: str) -> str:
    no_tags = re.sub(r"<[^>]+>", " ", html.unescape(value))
    return re.sub(r"\s+", " ", no_tags).strip()


def contains_prompt_injection(text: str) -> bool:
    return any(pattern.search(text) for pattern in INJECTION_PATTERNS)


def normalize_item(
    *, title: str, url: str, text: str, published_at: datetime, author: str | None = None
) -> NormalizedItem:
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=UTC)
    normalized = normalize_text(text)
    if not title.strip() or not normalized:
        raise ValueError("Title and content are required")
    if contains_prompt_injection(normalized):
        raise ValueError("Potential prompt injection detected")
    digest = hashlib.sha256(normalized.casefold().encode()).hexdigest()
    return NormalizedItem(
        title.strip(), canonicalize_url(url), author, published_at, text, normalized, digest
    )


def title_hash(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9 ]", "", normalize_text(title).casefold())
    return hashlib.sha256(normalized.encode()).hexdigest()


def token_similarity(left: str, right: str) -> float:
    a, b = (
        set(normalize_text(left).casefold().split()),
        set(normalize_text(right).casefold().split()),
    )
    return len(a & b) / len(a | b) if a | b else 1.0


def is_duplicate(left: NormalizedItem, right: NormalizedItem, threshold: float = 0.82) -> bool:
    return bool(
        left.canonical_url == right.canonical_url
        or left.content_hash == right.content_hash
        or title_hash(left.title) == title_hash(right.title)
        or token_similarity(left.normalized_text, right.normalized_text) >= threshold
        or SequenceMatcher(
            None, left.normalized_text.casefold(), right.normalized_text.casefold()
        ).ratio()
        >= 0.9
    )


def validate_public_url(url: str, allowed_hosts: set[str]) -> str:
    canonical = canonicalize_url(url)
    host = urlsplit(canonical).hostname
    if host is None or host not in {h.casefold() for h in allowed_hosts}:
        raise ValueError("Host is not allowlisted")
    for result in socket.getaddrinfo(host, None):
        address = ipaddress.ip_address(result[4][0])
        if not address.is_global:
            raise ValueError("URL resolves to a non-public address")
    return canonical

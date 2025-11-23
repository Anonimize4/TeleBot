"""Lightweight replacement for the stdlib `imghdr` module.

This small shim implements the minimal `what()` function used by
`python-telegram-bot` to detect image types from a byte stream.

It only recognizes a few common formats (jpeg, png, gif, bmp, webp)
which is sufficient for basic usage in the project.
"""
from __future__ import annotations

from typing import Optional


def what(file: object | None, h: bytes | None = None) -> Optional[str]:
    """Return a string describing the image type, or None if not recognized.

    Args:
        file: Ignored (kept for compatibility with stdlib signature).
        h: Bytes of the file header (or full content).
    """
    if h is None:
        try:
            # If a file-like was provided, read some bytes
            if hasattr(file, "read"):
                h = file.read(32)
        except Exception:
            return None

    if not h:
        return None

    # JPEG
    if h[:2] == b"\xff\xd8":
        return "jpeg"

    # PNG
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    # GIF
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"

    # BMP
    if h[:2] == b"BM":
        return "bmp"

    # WebP (RIFF header with 'WEBP' in bytes 8..12)
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        return "webp"

    return None

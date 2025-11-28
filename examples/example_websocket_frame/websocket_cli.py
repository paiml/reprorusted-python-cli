#!/usr/bin/env python3
"""WebSocket Frame CLI.

Parse and encode WebSocket protocol frames.
"""

import argparse
import os
import sys
from dataclasses import dataclass
from enum import IntEnum


class Opcode(IntEnum):
    """WebSocket frame opcodes."""

    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA


# Close status codes
CLOSE_CODES = {
    1000: "Normal Closure",
    1001: "Going Away",
    1002: "Protocol Error",
    1003: "Unsupported Data",
    1005: "No Status Received",
    1006: "Abnormal Closure",
    1007: "Invalid Payload",
    1008: "Policy Violation",
    1009: "Message Too Big",
    1010: "Mandatory Extension",
    1011: "Internal Server Error",
    1015: "TLS Handshake",
}


@dataclass
class WebSocketFrame:
    """WebSocket frame structure."""

    fin: bool
    rsv1: bool
    rsv2: bool
    rsv3: bool
    opcode: Opcode
    mask: bool
    payload_length: int
    masking_key: bytes | None
    payload: bytes


def encode_frame(
    payload: bytes,
    opcode: Opcode = Opcode.TEXT,
    fin: bool = True,
    mask: bool = False,
    masking_key: bytes | None = None,
) -> bytes:
    """Encode WebSocket frame."""
    frame = bytearray()

    # First byte: FIN + RSV + Opcode
    first_byte = (0x80 if fin else 0x00) | (opcode & 0x0F)
    frame.append(first_byte)

    # Second byte: Mask + Payload length
    payload_length = len(payload)

    if payload_length <= 125:
        second_byte = (0x80 if mask else 0x00) | payload_length
        frame.append(second_byte)
    elif payload_length <= 65535:
        second_byte = (0x80 if mask else 0x00) | 126
        frame.append(second_byte)
        frame.extend(payload_length.to_bytes(2, "big"))
    else:
        second_byte = (0x80 if mask else 0x00) | 127
        frame.append(second_byte)
        frame.extend(payload_length.to_bytes(8, "big"))

    # Masking key
    if mask:
        if masking_key is None:
            masking_key = os.urandom(4)
        frame.extend(masking_key)

        # Mask payload
        masked_payload = bytearray(payload_length)
        for i in range(payload_length):
            masked_payload[i] = payload[i] ^ masking_key[i % 4]
        frame.extend(masked_payload)
    else:
        frame.extend(payload)

    return bytes(frame)


def parse_frame(data: bytes) -> tuple[WebSocketFrame, int]:
    """Parse WebSocket frame from bytes. Returns (frame, bytes_consumed)."""
    if len(data) < 2:
        raise ValueError("Frame too short")

    pos = 0

    # First byte
    first_byte = data[pos]
    pos += 1

    fin = bool(first_byte & 0x80)
    rsv1 = bool(first_byte & 0x40)
    rsv2 = bool(first_byte & 0x20)
    rsv3 = bool(first_byte & 0x10)
    opcode = Opcode(first_byte & 0x0F)

    # Second byte
    second_byte = data[pos]
    pos += 1

    mask = bool(second_byte & 0x80)
    payload_length = second_byte & 0x7F

    # Extended payload length
    if payload_length == 126:
        if len(data) < pos + 2:
            raise ValueError("Frame too short for extended length")
        payload_length = int.from_bytes(data[pos : pos + 2], "big")
        pos += 2
    elif payload_length == 127:
        if len(data) < pos + 8:
            raise ValueError("Frame too short for extended length")
        payload_length = int.from_bytes(data[pos : pos + 8], "big")
        pos += 8

    # Masking key
    masking_key = None
    if mask:
        if len(data) < pos + 4:
            raise ValueError("Frame too short for masking key")
        masking_key = data[pos : pos + 4]
        pos += 4

    # Payload
    if len(data) < pos + payload_length:
        raise ValueError("Frame too short for payload")

    payload = data[pos : pos + payload_length]
    pos += payload_length

    # Unmask if needed
    if mask and masking_key:
        unmasked = bytearray(payload_length)
        for i in range(payload_length):
            unmasked[i] = payload[i] ^ masking_key[i % 4]
        payload = bytes(unmasked)

    return (
        WebSocketFrame(
            fin=fin,
            rsv1=rsv1,
            rsv2=rsv2,
            rsv3=rsv3,
            opcode=opcode,
            mask=mask,
            payload_length=payload_length,
            masking_key=masking_key,
            payload=payload,
        ),
        pos,
    )


def encode_text(text: str, mask: bool = False) -> bytes:
    """Encode text frame."""
    return encode_frame(text.encode("utf-8"), Opcode.TEXT, mask=mask)


def encode_binary(data: bytes, mask: bool = False) -> bytes:
    """Encode binary frame."""
    return encode_frame(data, Opcode.BINARY, mask=mask)


def encode_close(code: int = 1000, reason: str = "", mask: bool = False) -> bytes:
    """Encode close frame."""
    payload = code.to_bytes(2, "big")
    if reason:
        payload += reason.encode("utf-8")
    return encode_frame(payload, Opcode.CLOSE, mask=mask)


def encode_ping(data: bytes = b"", mask: bool = False) -> bytes:
    """Encode ping frame."""
    return encode_frame(data, Opcode.PING, mask=mask)


def encode_pong(data: bytes = b"", mask: bool = False) -> bytes:
    """Encode pong frame."""
    return encode_frame(data, Opcode.PONG, mask=mask)


def parse_close_payload(payload: bytes) -> tuple[int, str]:
    """Parse close frame payload."""
    if len(payload) < 2:
        return 1005, ""  # No status received

    code = int.from_bytes(payload[:2], "big")
    reason = payload[2:].decode("utf-8", errors="replace") if len(payload) > 2 else ""

    return code, reason


def mask_payload(payload: bytes, key: bytes) -> bytes:
    """Apply XOR masking to payload."""
    result = bytearray(len(payload))
    for i in range(len(payload)):
        result[i] = payload[i] ^ key[i % 4]
    return bytes(result)


def generate_masking_key() -> bytes:
    """Generate random masking key."""
    return os.urandom(4)


def fragment_message(
    data: bytes, opcode: Opcode, max_fragment_size: int = 1024, mask: bool = False
) -> list[bytes]:
    """Fragment a message into multiple frames."""
    if len(data) <= max_fragment_size:
        return [encode_frame(data, opcode, fin=True, mask=mask)]

    frames = []
    offset = 0

    while offset < len(data):
        chunk = data[offset : offset + max_fragment_size]
        is_first = offset == 0
        is_last = offset + max_fragment_size >= len(data)

        if is_first:
            frame = encode_frame(chunk, opcode, fin=is_last, mask=mask)
        else:
            frame = encode_frame(chunk, Opcode.CONTINUATION, fin=is_last, mask=mask)

        frames.append(frame)
        offset += max_fragment_size

    return frames


def defragment_frames(frames: list[WebSocketFrame]) -> tuple[Opcode, bytes]:
    """Reassemble fragmented frames into complete message."""
    if not frames:
        raise ValueError("No frames to defragment")

    opcode = frames[0].opcode
    payload = bytearray()

    for frame in frames:
        payload.extend(frame.payload)

        if frame.fin:
            break

    return opcode, bytes(payload)


def is_control_frame(opcode: Opcode) -> bool:
    """Check if opcode is a control frame."""
    return opcode >= 0x8


def validate_frame(frame: WebSocketFrame) -> list[str]:
    """Validate frame and return list of errors."""
    errors = []

    # Control frames must not be fragmented
    if is_control_frame(frame.opcode) and not frame.fin:
        errors.append("Control frame must not be fragmented")

    # Control frame payload must be <= 125 bytes
    if is_control_frame(frame.opcode) and frame.payload_length > 125:
        errors.append("Control frame payload too large")

    # RSV bits must be 0 unless extension is negotiated
    if frame.rsv1 or frame.rsv2 or frame.rsv3:
        errors.append("RSV bits must be 0 without extensions")

    # Check close code validity
    if frame.opcode == Opcode.CLOSE and frame.payload_length >= 2:
        code, _ = parse_close_payload(frame.payload)
        if code < 1000 or (code >= 1004 and code <= 1006) or (code >= 1012 and code <= 1015):
            if code not in CLOSE_CODES:
                errors.append(f"Invalid close code: {code}")

    return errors


class WebSocketConnection:
    """Simple WebSocket connection state machine."""

    def __init__(self, is_client: bool = True):
        self.is_client = is_client
        self.is_open = True
        self.closing = False
        self.fragments: list[WebSocketFrame] = []

    def process_frame(self, frame: WebSocketFrame) -> tuple[str, bytes | None]:
        """Process incoming frame. Returns (action, response_frame)."""
        if not self.is_open:
            return "error", None

        errors = validate_frame(frame)
        if errors:
            close_frame = encode_close(1002, errors[0], mask=self.is_client)
            return "protocol_error", close_frame

        if frame.opcode == Opcode.PING:
            pong = encode_pong(frame.payload, mask=self.is_client)
            return "pong", pong

        if frame.opcode == Opcode.PONG:
            return "pong_received", None

        if frame.opcode == Opcode.CLOSE:
            code, reason = parse_close_payload(frame.payload)
            if not self.closing:
                # Echo close frame
                response = encode_close(code, reason, mask=self.is_client)
                self.closing = True
                return "close", response
            self.is_open = False
            return "closed", None

        # Data frames
        if frame.opcode in (Opcode.TEXT, Opcode.BINARY):
            self.fragments = [frame]
        elif frame.opcode == Opcode.CONTINUATION:
            self.fragments.append(frame)

        if frame.fin:
            opcode, data = defragment_frames(self.fragments)
            self.fragments = []

            if opcode == Opcode.TEXT:
                return "text", data
            return "binary", data

        return "fragment", None

    def send_text(self, text: str) -> bytes:
        """Create text frame to send."""
        return encode_text(text, mask=self.is_client)

    def send_binary(self, data: bytes) -> bytes:
        """Create binary frame to send."""
        return encode_binary(data, mask=self.is_client)

    def send_close(self, code: int = 1000, reason: str = "") -> bytes:
        """Create close frame to send."""
        self.closing = True
        return encode_close(code, reason, mask=self.is_client)


def format_frame(frame: WebSocketFrame) -> str:
    """Format frame for display."""
    lines = []

    opcode_name = frame.opcode.name if hasattr(frame.opcode, "name") else str(frame.opcode)
    lines.append(f"Opcode: {opcode_name}")
    lines.append(f"FIN: {frame.fin}")
    lines.append(f"RSV: {frame.rsv1}/{frame.rsv2}/{frame.rsv3}")
    lines.append(f"Mask: {frame.mask}")
    lines.append(f"Payload Length: {frame.payload_length}")

    if frame.masking_key:
        lines.append(f"Masking Key: {frame.masking_key.hex()}")

    if frame.opcode == Opcode.TEXT:
        try:
            text = frame.payload.decode("utf-8")
            lines.append(f"Payload (text): {text}")
        except UnicodeDecodeError:
            lines.append(f"Payload (hex): {frame.payload.hex()}")
    elif frame.opcode == Opcode.CLOSE:
        code, reason = parse_close_payload(frame.payload)
        code_name = CLOSE_CODES.get(code, "Unknown")
        lines.append(f"Close Code: {code} ({code_name})")
        if reason:
            lines.append(f"Close Reason: {reason}")
    else:
        lines.append(f"Payload (hex): {frame.payload.hex()}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="WebSocket frame parser")
    parser.add_argument(
        "--mode",
        choices=["encode", "parse", "ping", "close", "fragment"],
        default="encode",
        help="Operation mode",
    )
    parser.add_argument("--text", help="Text to encode")
    parser.add_argument("--hex", help="Hex data to parse")
    parser.add_argument("--mask", action="store_true", help="Apply masking")
    parser.add_argument("--code", type=int, default=1000, help="Close code")
    parser.add_argument("--reason", default="", help="Close reason")
    parser.add_argument("--fragment-size", type=int, default=10, help="Max fragment size")

    args = parser.parse_args()

    if args.mode == "encode" and args.text:
        frame = encode_text(args.text, mask=args.mask)
        print(f"Text: {args.text}")
        print(f"Frame: {frame.hex()}")
        print(f"Length: {len(frame)} bytes")

    elif args.mode == "parse" and args.hex:
        data = bytes.fromhex(args.hex.replace(" ", ""))
        frame, consumed = parse_frame(data)
        print(format_frame(frame))

    elif args.mode == "ping":
        frame = encode_ping(b"ping", mask=args.mask)
        print(f"Ping frame: {frame.hex()}")

        pong = encode_pong(b"ping", mask=args.mask)
        print(f"Pong frame: {pong.hex()}")

    elif args.mode == "close":
        frame = encode_close(args.code, args.reason, mask=args.mask)
        code_name = CLOSE_CODES.get(args.code, "Unknown")
        print(f"Close frame (code {args.code} - {code_name}):")
        print(f"  Hex: {frame.hex()}")

    elif args.mode == "fragment":
        text = args.text or "Hello, WebSocket World! This is a test message."
        data = text.encode("utf-8")
        frames = fragment_message(data, Opcode.TEXT, args.fragment_size, mask=args.mask)

        print(f"Original: {text}")
        print(f"Fragments: {len(frames)}")
        for i, frame in enumerate(frames):
            parsed, _ = parse_frame(frame)
            fin_marker = " (FIN)" if parsed.fin else ""
            print(f"  Frame {i + 1}: {len(parsed.payload)} bytes{fin_marker}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

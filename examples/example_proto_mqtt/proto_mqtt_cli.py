"""MQTT Protocol Parser CLI.

Demonstrates MQTT packet parsing and encoding.
"""

import sys
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


class PacketType(IntEnum):
    """MQTT packet types."""

    CONNECT = 1
    CONNACK = 2
    PUBLISH = 3
    PUBACK = 4
    PUBREC = 5
    PUBREL = 6
    PUBCOMP = 7
    SUBSCRIBE = 8
    SUBACK = 9
    UNSUBSCRIBE = 10
    UNSUBACK = 11
    PINGREQ = 12
    PINGRESP = 13
    DISCONNECT = 14


class QoS(IntEnum):
    """MQTT QoS levels."""

    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


class ConnectReturnCode(IntEnum):
    """CONNECT return codes."""

    ACCEPTED = 0
    UNACCEPTABLE_PROTOCOL = 1
    IDENTIFIER_REJECTED = 2
    SERVER_UNAVAILABLE = 3
    BAD_CREDENTIALS = 4
    NOT_AUTHORIZED = 5


class MqttError(Exception):
    """MQTT parsing error."""

    pass


@dataclass
class ConnectPacket:
    """MQTT CONNECT packet."""

    client_id: str
    clean_session: bool = True
    keep_alive: int = 60
    username: str | None = None
    password: str | None = None
    will_topic: str | None = None
    will_message: bytes | None = None
    will_qos: QoS = QoS.AT_MOST_ONCE
    will_retain: bool = False


@dataclass
class ConnackPacket:
    """MQTT CONNACK packet."""

    session_present: bool
    return_code: ConnectReturnCode


@dataclass
class PublishPacket:
    """MQTT PUBLISH packet."""

    topic: str
    payload: bytes
    qos: QoS = QoS.AT_MOST_ONCE
    retain: bool = False
    dup: bool = False
    packet_id: int | None = None


@dataclass
class SubscribePacket:
    """MQTT SUBSCRIBE packet."""

    packet_id: int
    topics: list[tuple[str, QoS]] = field(default_factory=list)


@dataclass
class SubackPacket:
    """MQTT SUBACK packet."""

    packet_id: int
    return_codes: list[int] = field(default_factory=list)


@dataclass
class UnsubscribePacket:
    """MQTT UNSUBSCRIBE packet."""

    packet_id: int
    topics: list[str] = field(default_factory=list)


MqttPacket = (
    ConnectPacket
    | ConnackPacket
    | PublishPacket
    | SubscribePacket
    | SubackPacket
    | UnsubscribePacket
    | None
)


class MqttEncoder:
    """MQTT packet encoder."""

    @staticmethod
    def encode_remaining_length(length: int) -> bytes:
        """Encode variable length field."""
        result = bytearray()
        while True:
            byte = length % 128
            length //= 128
            if length > 0:
                byte |= 0x80
            result.append(byte)
            if length == 0:
                break
        return bytes(result)

    @staticmethod
    def encode_string(s: str) -> bytes:
        """Encode MQTT string."""
        encoded = s.encode("utf-8")
        return len(encoded).to_bytes(2, "big") + encoded

    @staticmethod
    def encode_connect(packet: ConnectPacket) -> bytes:
        """Encode CONNECT packet."""
        # Variable header
        var_header = bytearray()
        var_header.extend(MqttEncoder.encode_string("MQTT"))  # Protocol name
        var_header.append(4)  # Protocol level (MQTT 3.1.1)

        # Connect flags
        flags = 0
        if packet.clean_session:
            flags |= 0x02
        if packet.will_topic:
            flags |= 0x04
            flags |= (packet.will_qos & 0x03) << 3
            if packet.will_retain:
                flags |= 0x20
        if packet.password:
            flags |= 0x40
        if packet.username:
            flags |= 0x80
        var_header.append(flags)

        var_header.extend(packet.keep_alive.to_bytes(2, "big"))

        # Payload
        payload = bytearray()
        payload.extend(MqttEncoder.encode_string(packet.client_id))
        if packet.will_topic:
            payload.extend(MqttEncoder.encode_string(packet.will_topic))
            will_msg = packet.will_message or b""
            payload.extend(len(will_msg).to_bytes(2, "big"))
            payload.extend(will_msg)
        if packet.username:
            payload.extend(MqttEncoder.encode_string(packet.username))
        if packet.password:
            payload.extend(MqttEncoder.encode_string(packet.password))

        # Fixed header
        remaining = bytes(var_header) + bytes(payload)
        fixed = bytes([PacketType.CONNECT << 4])
        fixed += MqttEncoder.encode_remaining_length(len(remaining))

        return fixed + remaining

    @staticmethod
    def encode_connack(packet: ConnackPacket) -> bytes:
        """Encode CONNACK packet."""
        flags = 0x01 if packet.session_present else 0x00
        return bytes([PacketType.CONNACK << 4, 2, flags, packet.return_code])

    @staticmethod
    def encode_publish(packet: PublishPacket) -> bytes:
        """Encode PUBLISH packet."""
        # Fixed header flags
        flags = packet.qos << 1
        if packet.retain:
            flags |= 0x01
        if packet.dup:
            flags |= 0x08

        # Variable header
        var_header = MqttEncoder.encode_string(packet.topic)
        if packet.qos > 0 and packet.packet_id is not None:
            var_header += packet.packet_id.to_bytes(2, "big")

        # Build packet
        remaining = var_header + packet.payload
        fixed = bytes([(PacketType.PUBLISH << 4) | flags])
        fixed += MqttEncoder.encode_remaining_length(len(remaining))

        return fixed + remaining

    @staticmethod
    def encode_subscribe(packet: SubscribePacket) -> bytes:
        """Encode SUBSCRIBE packet."""
        var_header = packet.packet_id.to_bytes(2, "big")
        payload = bytearray()
        for topic, qos in packet.topics:
            payload.extend(MqttEncoder.encode_string(topic))
            payload.append(qos)

        remaining = var_header + bytes(payload)
        fixed = bytes([(PacketType.SUBSCRIBE << 4) | 0x02])
        fixed += MqttEncoder.encode_remaining_length(len(remaining))

        return fixed + remaining

    @staticmethod
    def encode_pingreq() -> bytes:
        """Encode PINGREQ packet."""
        return bytes([PacketType.PINGREQ << 4, 0])

    @staticmethod
    def encode_pingresp() -> bytes:
        """Encode PINGRESP packet."""
        return bytes([PacketType.PINGRESP << 4, 0])

    @staticmethod
    def encode_disconnect() -> bytes:
        """Encode DISCONNECT packet."""
        return bytes([PacketType.DISCONNECT << 4, 0])


class MqttDecoder:
    """MQTT packet decoder."""

    def __init__(self) -> None:
        self.buffer = b""

    def feed(self, data: bytes) -> None:
        """Feed data to decoder."""
        self.buffer += data

    def decode_remaining_length(self, pos: int) -> tuple[int, int]:
        """Decode variable length field. Returns (length, bytes_consumed)."""
        multiplier = 1
        value = 0
        consumed = 0
        while pos + consumed < len(self.buffer):
            byte = self.buffer[pos + consumed]
            value += (byte & 0x7F) * multiplier
            consumed += 1
            if (byte & 0x80) == 0:
                return value, consumed
            multiplier *= 128
            if multiplier > 128 * 128 * 128:
                raise MqttError("Malformed remaining length")
        return -1, 0  # Need more data

    def decode_string(self, pos: int) -> tuple[str, int]:
        """Decode MQTT string. Returns (string, bytes_consumed)."""
        if pos + 2 > len(self.buffer):
            raise MqttError("Incomplete string length")
        length = int.from_bytes(self.buffer[pos : pos + 2], "big")
        if pos + 2 + length > len(self.buffer):
            raise MqttError("Incomplete string data")
        s = self.buffer[pos + 2 : pos + 2 + length].decode("utf-8")
        return s, 2 + length

    def decode(self) -> tuple[MqttPacket, int]:
        """Decode packet. Returns (packet, bytes_consumed) or (None, 0)."""
        if len(self.buffer) < 2:
            return None, 0

        fixed_byte = self.buffer[0]
        packet_type = PacketType(fixed_byte >> 4)
        flags = fixed_byte & 0x0F

        remaining_length, length_bytes = self.decode_remaining_length(1)
        if remaining_length < 0:
            return None, 0

        total_length = 1 + length_bytes + remaining_length
        if len(self.buffer) < total_length:
            return None, 0

        pos = 1 + length_bytes

        if packet_type == PacketType.CONNACK:
            session_present = bool(self.buffer[pos] & 0x01)
            return_code = ConnectReturnCode(self.buffer[pos + 1])
            return ConnackPacket(session_present, return_code), total_length

        elif packet_type == PacketType.PUBLISH:
            topic, consumed = self.decode_string(pos)
            pos += consumed
            qos = QoS((flags >> 1) & 0x03)
            retain = bool(flags & 0x01)
            dup = bool(flags & 0x08)
            packet_id = None
            if qos > 0:
                packet_id = int.from_bytes(self.buffer[pos : pos + 2], "big")
                pos += 2
            payload_end = 1 + length_bytes + remaining_length
            payload = self.buffer[pos:payload_end]
            return (
                PublishPacket(topic, payload, qos, retain, dup, packet_id),
                total_length,
            )

        elif packet_type == PacketType.SUBACK:
            packet_id = int.from_bytes(self.buffer[pos : pos + 2], "big")
            pos += 2
            end = 1 + length_bytes + remaining_length
            return_codes = list(self.buffer[pos:end])
            return SubackPacket(packet_id, return_codes), total_length

        elif packet_type == PacketType.PINGREQ:
            return None, total_length  # Simple packet

        elif packet_type == PacketType.PINGRESP:
            return None, total_length

        return None, total_length

    def consume(self, length: int) -> None:
        """Remove consumed bytes from buffer."""
        self.buffer = self.buffer[length:]


def encode_connect(client_id: str, **kwargs: Any) -> bytes:
    """Encode CONNECT packet."""
    packet = ConnectPacket(client_id, **kwargs)
    return MqttEncoder.encode_connect(packet)


def encode_publish(topic: str, payload: bytes, qos: int = 0) -> bytes:
    """Encode PUBLISH packet."""
    packet = PublishPacket(topic, payload, QoS(qos))
    return MqttEncoder.encode_publish(packet)


def encode_subscribe(packet_id: int, topics: list[tuple[str, int]]) -> bytes:
    """Encode SUBSCRIBE packet."""
    packet = SubscribePacket(packet_id, [(t, QoS(q)) for t, q in topics])
    return MqttEncoder.encode_subscribe(packet)


def decode_packet(data: bytes) -> MqttPacket:
    """Decode MQTT packet."""
    decoder = MqttDecoder()
    decoder.feed(data)
    packet, _ = decoder.decode()
    return packet


def simulate_mqtt(operations: list[str]) -> list[str]:
    """Simulate MQTT operations."""
    results: list[str] = []

    for op in operations:
        parts = op.split(":", 1)
        cmd = parts[0]

        if cmd == "connect":
            data = encode_connect(parts[1])
            results.append(f"CONNECT len={len(data)}")
        elif cmd == "publish":
            topic, payload = parts[1].split(",", 1)
            data = encode_publish(topic, payload.encode())
            results.append(f"PUBLISH len={len(data)}")
        elif cmd == "subscribe":
            topic = parts[1]
            data = encode_subscribe(1, [(topic, 0)])
            results.append(f"SUBSCRIBE len={len(data)}")
        elif cmd == "ping":
            data = MqttEncoder.encode_pingreq()
            results.append(f"PINGREQ len={len(data)}")
        elif cmd == "disconnect":
            data = MqttEncoder.encode_disconnect()
            results.append(f"DISCONNECT len={len(data)}")

    return results


def main() -> int:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: proto_mqtt_cli.py <command> [args]")
        return 1

    cmd = sys.argv[1]
    if cmd == "connect" and len(sys.argv) > 2:
        data = encode_connect(sys.argv[2])
        print(f"CONNECT packet: {len(data)} bytes")
    elif cmd == "publish" and len(sys.argv) > 3:
        data = encode_publish(sys.argv[2], sys.argv[3].encode())
        print(f"PUBLISH packet: {len(data)} bytes")
    else:
        print("Unknown command")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

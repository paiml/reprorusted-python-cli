"""Tests for proto_mqtt_cli.py"""


from proto_mqtt_cli import (
    ConnackPacket,
    ConnectPacket,
    ConnectReturnCode,
    MqttDecoder,
    MqttEncoder,
    PacketType,
    PublishPacket,
    QoS,
    SubackPacket,
    SubscribePacket,
    decode_packet,
    encode_connect,
    encode_publish,
    encode_subscribe,
    simulate_mqtt,
)


class TestPacketType:
    def test_values(self):
        assert PacketType.CONNECT == 1
        assert PacketType.PUBLISH == 3
        assert PacketType.SUBSCRIBE == 8
        assert PacketType.DISCONNECT == 14


class TestQoS:
    def test_values(self):
        assert QoS.AT_MOST_ONCE == 0
        assert QoS.AT_LEAST_ONCE == 1
        assert QoS.EXACTLY_ONCE == 2


class TestConnectReturnCode:
    def test_values(self):
        assert ConnectReturnCode.ACCEPTED == 0
        assert ConnectReturnCode.BAD_CREDENTIALS == 4


class TestConnectPacket:
    def test_create(self):
        packet = ConnectPacket("client1")
        assert packet.client_id == "client1"
        assert packet.clean_session is True
        assert packet.keep_alive == 60

    def test_with_auth(self):
        packet = ConnectPacket("client1", username="user", password="pass")
        assert packet.username == "user"
        assert packet.password == "pass"

    def test_with_will(self):
        packet = ConnectPacket(
            "client1",
            will_topic="last/will",
            will_message=b"goodbye",
            will_qos=QoS.AT_LEAST_ONCE,
        )
        assert packet.will_topic == "last/will"
        assert packet.will_message == b"goodbye"


class TestPublishPacket:
    def test_create(self):
        packet = PublishPacket("topic/test", b"hello")
        assert packet.topic == "topic/test"
        assert packet.payload == b"hello"
        assert packet.qos == QoS.AT_MOST_ONCE

    def test_with_qos(self):
        packet = PublishPacket("topic", b"data", QoS.EXACTLY_ONCE, packet_id=42)
        assert packet.qos == QoS.EXACTLY_ONCE
        assert packet.packet_id == 42


class TestMqttEncoder:
    def test_encode_remaining_length_small(self):
        assert MqttEncoder.encode_remaining_length(0) == b"\x00"
        assert MqttEncoder.encode_remaining_length(127) == b"\x7f"

    def test_encode_remaining_length_medium(self):
        assert MqttEncoder.encode_remaining_length(128) == b"\x80\x01"
        assert MqttEncoder.encode_remaining_length(16383) == b"\xff\x7f"

    def test_encode_remaining_length_large(self):
        result = MqttEncoder.encode_remaining_length(16384)
        assert result == b"\x80\x80\x01"

    def test_encode_string(self):
        assert MqttEncoder.encode_string("") == b"\x00\x00"
        assert MqttEncoder.encode_string("AB") == b"\x00\x02AB"
        assert MqttEncoder.encode_string("test") == b"\x00\x04test"

    def test_encode_connect_simple(self):
        packet = ConnectPacket("client1")
        data = MqttEncoder.encode_connect(packet)
        assert data[0] >> 4 == PacketType.CONNECT
        assert b"MQTT" in data
        assert b"client1" in data

    def test_encode_connect_with_auth(self):
        packet = ConnectPacket("client1", username="user", password="pass")
        data = MqttEncoder.encode_connect(packet)
        assert b"user" in data
        assert b"pass" in data

    def test_encode_connack(self):
        packet = ConnackPacket(False, ConnectReturnCode.ACCEPTED)
        data = MqttEncoder.encode_connack(packet)
        assert data[0] >> 4 == PacketType.CONNACK
        assert data[2] == 0  # No session present
        assert data[3] == 0  # Accepted

    def test_encode_connack_session_present(self):
        packet = ConnackPacket(True, ConnectReturnCode.ACCEPTED)
        data = MqttEncoder.encode_connack(packet)
        assert data[2] == 1  # Session present

    def test_encode_publish_qos0(self):
        packet = PublishPacket("topic", b"data")
        data = MqttEncoder.encode_publish(packet)
        assert data[0] >> 4 == PacketType.PUBLISH
        assert b"topic" in data
        assert b"data" in data

    def test_encode_publish_qos1(self):
        packet = PublishPacket("topic", b"data", QoS.AT_LEAST_ONCE, packet_id=1)
        data = MqttEncoder.encode_publish(packet)
        # QoS 1 should be in flags
        assert (data[0] & 0x06) >> 1 == 1

    def test_encode_publish_retain(self):
        packet = PublishPacket("topic", b"data", retain=True)
        data = MqttEncoder.encode_publish(packet)
        assert data[0] & 0x01 == 1

    def test_encode_subscribe(self):
        packet = SubscribePacket(1, [("topic/+", QoS.AT_LEAST_ONCE)])
        data = MqttEncoder.encode_subscribe(packet)
        assert data[0] >> 4 == PacketType.SUBSCRIBE
        assert b"topic/+" in data

    def test_encode_pingreq(self):
        data = MqttEncoder.encode_pingreq()
        assert data == bytes([PacketType.PINGREQ << 4, 0])

    def test_encode_pingresp(self):
        data = MqttEncoder.encode_pingresp()
        assert data == bytes([PacketType.PINGRESP << 4, 0])

    def test_encode_disconnect(self):
        data = MqttEncoder.encode_disconnect()
        assert data == bytes([PacketType.DISCONNECT << 4, 0])


class TestMqttDecoder:
    def test_decode_remaining_length(self):
        decoder = MqttDecoder()
        decoder.feed(b"\x00")
        length, consumed = decoder.decode_remaining_length(0)
        assert length == 0
        assert consumed == 1

    def test_decode_remaining_length_two_bytes(self):
        decoder = MqttDecoder()
        decoder.feed(b"\x80\x01")
        length, consumed = decoder.decode_remaining_length(0)
        assert length == 128
        assert consumed == 2

    def test_decode_string(self):
        decoder = MqttDecoder()
        decoder.feed(b"\x00\x05hello")
        s, consumed = decoder.decode_string(0)
        assert s == "hello"
        assert consumed == 7

    def test_decode_connack(self):
        data = MqttEncoder.encode_connack(
            ConnackPacket(True, ConnectReturnCode.ACCEPTED)
        )
        decoder = MqttDecoder()
        decoder.feed(data)
        packet, consumed = decoder.decode()
        assert isinstance(packet, ConnackPacket)
        assert packet.session_present is True
        assert packet.return_code == ConnectReturnCode.ACCEPTED

    def test_decode_publish_qos0(self):
        original = PublishPacket("test/topic", b"hello world")
        data = MqttEncoder.encode_publish(original)
        decoder = MqttDecoder()
        decoder.feed(data)
        packet, consumed = decoder.decode()
        assert isinstance(packet, PublishPacket)
        assert packet.topic == "test/topic"
        assert packet.payload == b"hello world"

    def test_decode_publish_qos1(self):
        original = PublishPacket(
            "topic", b"data", QoS.AT_LEAST_ONCE, packet_id=123
        )
        data = MqttEncoder.encode_publish(original)
        decoder = MqttDecoder()
        decoder.feed(data)
        packet, consumed = decoder.decode()
        assert isinstance(packet, PublishPacket)
        assert packet.qos == QoS.AT_LEAST_ONCE
        assert packet.packet_id == 123

    def test_decode_suback(self):
        data = bytes([PacketType.SUBACK << 4, 4, 0, 1, 0, 1])
        decoder = MqttDecoder()
        decoder.feed(data)
        packet, consumed = decoder.decode()
        assert isinstance(packet, SubackPacket)
        assert packet.packet_id == 1
        assert packet.return_codes == [0, 1]

    def test_decode_incomplete(self):
        decoder = MqttDecoder()
        decoder.feed(b"\x30")  # Incomplete PUBLISH
        packet, consumed = decoder.decode()
        assert packet is None
        assert consumed == 0

    def test_consume(self):
        decoder = MqttDecoder()
        decoder.feed(b"\x00\x00\x00\x00")
        decoder.consume(2)
        assert len(decoder.buffer) == 2


class TestEncodeConnect:
    def test_simple(self):
        data = encode_connect("myclient")
        assert b"myclient" in data
        assert data[0] >> 4 == PacketType.CONNECT

    def test_with_keepalive(self):
        data = encode_connect("client", keep_alive=120)
        assert len(data) > 0


class TestEncodePublish:
    def test_simple(self):
        data = encode_publish("topic", b"message")
        assert b"topic" in data
        assert b"message" in data

    def test_with_qos(self):
        data = encode_publish("topic", b"msg", qos=1)
        assert (data[0] & 0x06) >> 1 == 1


class TestEncodeSubscribe:
    def test_single_topic(self):
        data = encode_subscribe(1, [("topic/#", 0)])
        assert b"topic/#" in data

    def test_multiple_topics(self):
        data = encode_subscribe(1, [("topic1", 0), ("topic2", 1)])
        assert b"topic1" in data
        assert b"topic2" in data


class TestDecodePacket:
    def test_connack(self):
        data = MqttEncoder.encode_connack(
            ConnackPacket(False, ConnectReturnCode.ACCEPTED)
        )
        packet = decode_packet(data)
        assert isinstance(packet, ConnackPacket)

    def test_publish(self):
        data = encode_publish("test", b"data")
        packet = decode_packet(data)
        assert isinstance(packet, PublishPacket)


class TestSimulateMqtt:
    def test_connect(self):
        result = simulate_mqtt(["connect:client1"])
        assert "CONNECT" in result[0]

    def test_publish(self):
        result = simulate_mqtt(["publish:topic,message"])
        assert "PUBLISH" in result[0]

    def test_subscribe(self):
        result = simulate_mqtt(["subscribe:topic/#"])
        assert "SUBSCRIBE" in result[0]

    def test_ping(self):
        result = simulate_mqtt(["ping:"])
        assert "PINGREQ" in result[0]

    def test_disconnect(self):
        result = simulate_mqtt(["disconnect:"])
        assert "DISCONNECT" in result[0]


class TestWildcards:
    def test_single_level(self):
        data = encode_subscribe(1, [("sensors/+/temperature", 0)])
        assert b"sensors/+/temperature" in data

    def test_multi_level(self):
        data = encode_subscribe(1, [("sensors/#", 0)])
        assert b"sensors/#" in data


class TestRoundTrip:
    def test_publish_roundtrip(self):
        original = PublishPacket("test/topic", b"test payload", QoS.AT_MOST_ONCE)
        encoded = MqttEncoder.encode_publish(original)
        decoded = decode_packet(encoded)
        assert isinstance(decoded, PublishPacket)
        assert decoded.topic == original.topic
        assert decoded.payload == original.payload

    def test_connack_roundtrip(self):
        original = ConnackPacket(True, ConnectReturnCode.ACCEPTED)
        encoded = MqttEncoder.encode_connack(original)
        decoded = decode_packet(encoded)
        assert isinstance(decoded, ConnackPacket)
        assert decoded.session_present == original.session_present
        assert decoded.return_code == original.return_code

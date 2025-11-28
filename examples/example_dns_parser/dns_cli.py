#!/usr/bin/env python3
"""DNS Parser CLI.

Parse and encode DNS protocol messages.
"""

import argparse
import sys
from dataclasses import dataclass

# DNS record types
DNS_TYPES = {
    1: "A",
    2: "NS",
    5: "CNAME",
    6: "SOA",
    12: "PTR",
    15: "MX",
    16: "TXT",
    28: "AAAA",
}

DNS_TYPES_REVERSE = {v: k for k, v in DNS_TYPES.items()}

# DNS classes
DNS_CLASSES = {
    1: "IN",
    3: "CH",
    4: "HS",
}


@dataclass
class DNSHeader:
    """DNS message header."""

    id: int
    qr: int  # Query (0) or Response (1)
    opcode: int
    aa: int  # Authoritative Answer
    tc: int  # Truncation
    rd: int  # Recursion Desired
    ra: int  # Recursion Available
    z: int  # Reserved
    rcode: int  # Response code
    qdcount: int  # Question count
    ancount: int  # Answer count
    nscount: int  # Authority count
    arcount: int  # Additional count


@dataclass
class DNSQuestion:
    """DNS question section."""

    name: str
    qtype: int
    qclass: int


@dataclass
class DNSRecord:
    """DNS resource record."""

    name: str
    rtype: int
    rclass: int
    ttl: int
    rdlength: int
    rdata: bytes


def parse_header(data: bytes) -> DNSHeader:
    """Parse DNS header from bytes."""
    if len(data) < 12:
        raise ValueError("DNS header too short")

    id_ = (data[0] << 8) | data[1]
    flags = (data[2] << 8) | data[3]

    qr = (flags >> 15) & 0x1
    opcode = (flags >> 11) & 0xF
    aa = (flags >> 10) & 0x1
    tc = (flags >> 9) & 0x1
    rd = (flags >> 8) & 0x1
    ra = (flags >> 7) & 0x1
    z = (flags >> 4) & 0x7
    rcode = flags & 0xF

    qdcount = (data[4] << 8) | data[5]
    ancount = (data[6] << 8) | data[7]
    nscount = (data[8] << 8) | data[9]
    arcount = (data[10] << 8) | data[11]

    return DNSHeader(
        id=id_,
        qr=qr,
        opcode=opcode,
        aa=aa,
        tc=tc,
        rd=rd,
        ra=ra,
        z=z,
        rcode=rcode,
        qdcount=qdcount,
        ancount=ancount,
        nscount=nscount,
        arcount=arcount,
    )


def encode_header(header: DNSHeader) -> bytes:
    """Encode DNS header to bytes."""
    id_bytes = bytes([header.id >> 8, header.id & 0xFF])

    flags = (
        (header.qr << 15)
        | (header.opcode << 11)
        | (header.aa << 10)
        | (header.tc << 9)
        | (header.rd << 8)
        | (header.ra << 7)
        | (header.z << 4)
        | header.rcode
    )
    flags_bytes = bytes([flags >> 8, flags & 0xFF])

    counts = bytes(
        [
            header.qdcount >> 8,
            header.qdcount & 0xFF,
            header.ancount >> 8,
            header.ancount & 0xFF,
            header.nscount >> 8,
            header.nscount & 0xFF,
            header.arcount >> 8,
            header.arcount & 0xFF,
        ]
    )

    return id_bytes + flags_bytes + counts


def parse_name(data: bytes, offset: int) -> tuple[str, int]:
    """Parse DNS domain name with compression support."""
    labels = []
    pos = offset
    jumped = False
    original_pos = offset

    while True:
        if pos >= len(data):
            break

        length = data[pos]

        # Check for compression pointer
        if (length & 0xC0) == 0xC0:
            if pos + 1 >= len(data):
                break
            pointer = ((length & 0x3F) << 8) | data[pos + 1]
            if not jumped:
                original_pos = pos + 2
            jumped = True
            pos = pointer
            continue

        if length == 0:
            pos += 1
            break

        pos += 1
        if pos + length > len(data):
            break

        label = data[pos : pos + length].decode("ascii")
        labels.append(label)
        pos += length

    name = ".".join(labels)
    return name, original_pos if jumped else pos


def encode_name(name: str) -> bytes:
    """Encode domain name to DNS format."""
    if not name or name == ".":
        return b"\x00"

    result = b""
    for label in name.rstrip(".").split("."):
        encoded = label.encode("ascii")
        result += bytes([len(encoded)]) + encoded

    return result + b"\x00"


def parse_question(data: bytes, offset: int) -> tuple[DNSQuestion, int]:
    """Parse DNS question section."""
    name, pos = parse_name(data, offset)

    if pos + 4 > len(data):
        raise ValueError("Question section too short")

    qtype = (data[pos] << 8) | data[pos + 1]
    qclass = (data[pos + 2] << 8) | data[pos + 3]

    return DNSQuestion(name=name, qtype=qtype, qclass=qclass), pos + 4


def encode_question(question: DNSQuestion) -> bytes:
    """Encode DNS question to bytes."""
    name_bytes = encode_name(question.name)
    type_bytes = bytes([question.qtype >> 8, question.qtype & 0xFF])
    class_bytes = bytes([question.qclass >> 8, question.qclass & 0xFF])
    return name_bytes + type_bytes + class_bytes


def parse_record(data: bytes, offset: int) -> tuple[DNSRecord, int]:
    """Parse DNS resource record."""
    name, pos = parse_name(data, offset)

    if pos + 10 > len(data):
        raise ValueError("Record too short")

    rtype = (data[pos] << 8) | data[pos + 1]
    rclass = (data[pos + 2] << 8) | data[pos + 3]
    ttl = (data[pos + 4] << 24) | (data[pos + 5] << 16) | (data[pos + 6] << 8) | data[pos + 7]
    rdlength = (data[pos + 8] << 8) | data[pos + 9]

    pos += 10
    if pos + rdlength > len(data):
        raise ValueError("Record data too short")

    rdata = data[pos : pos + rdlength]

    return (
        DNSRecord(
            name=name,
            rtype=rtype,
            rclass=rclass,
            ttl=ttl,
            rdlength=rdlength,
            rdata=rdata,
        ),
        pos + rdlength,
    )


def format_rdata(rtype: int, rdata: bytes, full_data: bytes | None = None) -> str:
    """Format resource data for display."""
    if rtype == 1 and len(rdata) == 4:  # A record
        return f"{rdata[0]}.{rdata[1]}.{rdata[2]}.{rdata[3]}"

    if rtype == 28 and len(rdata) == 16:  # AAAA record
        parts = []
        for i in range(0, 16, 2):
            parts.append(f"{rdata[i]:02x}{rdata[i + 1]:02x}")
        return ":".join(parts)

    if rtype in (2, 5, 12):  # NS, CNAME, PTR
        if full_data:
            name, _ = parse_name(full_data, full_data.index(rdata))
            return name
        return rdata.hex()

    if rtype == 15 and len(rdata) >= 3:  # MX record
        preference = (rdata[0] << 8) | rdata[1]
        if full_data:
            # Find where rdata starts in full_data and parse exchange
            name, _ = parse_name(full_data, full_data.index(rdata) + 2)
            return f"{preference} {name}"
        return f"{preference} {rdata[2:].hex()}"

    if rtype == 16:  # TXT record
        texts = []
        pos = 0
        while pos < len(rdata):
            length = rdata[pos]
            pos += 1
            if pos + length <= len(rdata):
                texts.append(rdata[pos : pos + length].decode("utf-8", errors="replace"))
            pos += length
        return " ".join(f'"{t}"' for t in texts)

    return rdata.hex()


def build_query(domain: str, qtype: str = "A", id_: int = 1234) -> bytes:
    """Build a DNS query message."""
    header = DNSHeader(
        id=id_,
        qr=0,
        opcode=0,
        aa=0,
        tc=0,
        rd=1,
        ra=0,
        z=0,
        rcode=0,
        qdcount=1,
        ancount=0,
        nscount=0,
        arcount=0,
    )

    type_num = DNS_TYPES_REVERSE.get(qtype.upper(), 1)
    question = DNSQuestion(name=domain, qtype=type_num, qclass=1)

    return encode_header(header) + encode_question(question)


def parse_message(data: bytes) -> dict:
    """Parse complete DNS message."""
    header = parse_header(data)

    result = {
        "header": {
            "id": header.id,
            "qr": "response" if header.qr else "query",
            "opcode": header.opcode,
            "rcode": header.rcode,
            "flags": {
                "aa": bool(header.aa),
                "tc": bool(header.tc),
                "rd": bool(header.rd),
                "ra": bool(header.ra),
            },
        },
        "questions": [],
        "answers": [],
        "authority": [],
        "additional": [],
    }

    pos = 12

    # Parse questions
    for _ in range(header.qdcount):
        question, pos = parse_question(data, pos)
        result["questions"].append(
            {
                "name": question.name,
                "type": DNS_TYPES.get(question.qtype, str(question.qtype)),
                "class": DNS_CLASSES.get(question.qclass, str(question.qclass)),
            }
        )

    # Parse answers
    for _ in range(header.ancount):
        record, pos = parse_record(data, pos)
        result["answers"].append(
            {
                "name": record.name,
                "type": DNS_TYPES.get(record.rtype, str(record.rtype)),
                "class": DNS_CLASSES.get(record.rclass, str(record.rclass)),
                "ttl": record.ttl,
                "data": format_rdata(record.rtype, record.rdata, data),
            }
        )

    # Parse authority
    for _ in range(header.nscount):
        record, pos = parse_record(data, pos)
        result["authority"].append(
            {
                "name": record.name,
                "type": DNS_TYPES.get(record.rtype, str(record.rtype)),
                "ttl": record.ttl,
            }
        )

    # Parse additional
    for _ in range(header.arcount):
        record, pos = parse_record(data, pos)
        result["additional"].append(
            {
                "name": record.name,
                "type": DNS_TYPES.get(record.rtype, str(record.rtype)),
                "ttl": record.ttl,
            }
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="DNS protocol parser")
    parser.add_argument(
        "--mode",
        choices=["query", "parse", "encode-name"],
        default="query",
        help="Operation mode",
    )
    parser.add_argument("--domain", help="Domain name for query")
    parser.add_argument("--type", default="A", help="DNS record type")
    parser.add_argument("--hex", help="Hex-encoded DNS message to parse")

    args = parser.parse_args()

    if args.mode == "query" and args.domain:
        query = build_query(args.domain, args.type)
        print(f"DNS Query for {args.domain} ({args.type}):")
        print(f"Hex: {query.hex()}")
        print(f"Length: {len(query)} bytes")

    elif args.mode == "parse" and args.hex:
        data = bytes.fromhex(args.hex.replace(" ", ""))
        result = parse_message(data)

        print(f"ID: {result['header']['id']}")
        print(f"Type: {result['header']['qr']}")
        print(f"Opcode: {result['header']['opcode']}")
        print(f"Response code: {result['header']['rcode']}")

        for q in result["questions"]:
            print(f"Question: {q['name']} {q['type']} {q['class']}")

        for a in result["answers"]:
            print(f"Answer: {a['name']} {a['type']} TTL={a['ttl']} -> {a['data']}")

    elif args.mode == "encode-name" and args.domain:
        encoded = encode_name(args.domain)
        print(f"Domain: {args.domain}")
        print(f"Encoded: {encoded.hex()}")

    else:
        print("Usage: dns_cli.py --mode query --domain example.com")
        print("       dns_cli.py --mode parse --hex <hex_data>")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

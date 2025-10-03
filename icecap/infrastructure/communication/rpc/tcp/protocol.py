import struct

from google.protobuf.message import Message


class ProtocolCodec:
    """Handles wire-format encoding/decoding for the agent protocol.

    Protocol format: [4 bytes: message length (big-endian)] [N bytes: protobuf payload]
    """

    HEADER_SIZE = 4
    MAX_MESSAGE_SIZE = 10 * 1024 * 1024  # 10MB max message size

    @staticmethod
    def encode_message(message: Message) -> bytes:
        payload = message.SerializeToString()
        length = len(payload)

        if length > ProtocolCodec.MAX_MESSAGE_SIZE:
            raise ValueError(
                f"Message too large: {length} bytes (max {ProtocolCodec.MAX_MESSAGE_SIZE})"
            )

        # Pack length as 4-byte big-endian integer
        header = struct.pack(">I", length)
        return header + payload

    @staticmethod
    def decode_frame(buffer: bytearray) -> bytes | None:
        """Extract one complete frame from buffer if available.

        Args:
            buffer: Accumulator buffer containing received bytes

        Returns:
            Frame payload bytes if complete frame available, None otherwise.
            The extracted frame is removed from the buffer.
        """
        if len(buffer) < ProtocolCodec.HEADER_SIZE:
            return None

        # Extract length from first 4 bytes
        length = struct.unpack(">I", buffer[: ProtocolCodec.HEADER_SIZE])[0]

        if length > ProtocolCodec.MAX_MESSAGE_SIZE:
            raise ValueError(
                f"Invalid message length: {length} bytes (max {ProtocolCodec.MAX_MESSAGE_SIZE})"
            )

        # Check if a full message is available
        total_size = ProtocolCodec.HEADER_SIZE + length
        if len(buffer) < total_size:
            return None

        # Extract payload
        payload = bytes(buffer[ProtocolCodec.HEADER_SIZE : total_size])

        # Remove processed frame from buffer
        del buffer[:total_size]

        return payload

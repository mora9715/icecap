"""TCP connection management for agent communication."""

import logging
import socket
import threading
from typing import Callable

from icecap.agent.v1 import commands_pb2, events_pb2
from icecap.infrastructure.communication.rpc.exceptions import AgentConnectionError
from icecap.infrastructure.communication.rpc.interface import AgentClientEventHandler
from .protocol import ProtocolCodec

logger = logging.getLogger(__name__)


class TcpConnection:
    def __init__(self) -> None:
        self._socket: socket.socket | None = None
        self._receiver_thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._on_event_received: AgentClientEventHandler | None = None
        self._on_error: Callable[[Exception], None] | None = None

    def connect(self, host: str, port: int, timeout: float = 5.0) -> None:
        if self._running:
            logger.error("Attempted to connect while already connected")
            raise AgentConnectionError("Already connected")

        logger.debug(f"Establishing TCP connection to {host}:{port} (timeout: {timeout}s)")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((host, port))
            self._socket.settimeout(None)
            logger.info(f"TCP connection established to {host}:{port}")
        except (socket.error, socket.timeout) as e:
            self._socket = None
            logger.error(f"Failed to connect to {host}:{port}: {e}")
            raise AgentConnectionError(f"Failed to connect to {host}:{port}: {e}") from e

        self._running = True
        self._receiver_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._receiver_thread.start()
        logger.debug("Receiver thread started")

    def close(self) -> None:
        logger.debug("Closing TCP connection")
        self._running = False

        with self._lock:
            if self._socket:
                try:
                    self._socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    self._socket.close()
                except OSError:
                    pass
                self._socket = None

        if self._receiver_thread and self._receiver_thread.is_alive():
            self._receiver_thread.join(timeout=1.0)

        logger.info("TCP connection closed")

    def send_command(self, command: commands_pb2.Command) -> None:
        with self._lock:
            if not self._socket or not self._running:
                logger.error("Attempted to send command while not connected")
                raise AgentConnectionError("Not connected")

            try:
                encoded = ProtocolCodec.encode_message(command)
                self._socket.sendall(encoded)
                logger.debug(f"Sent command ({len(encoded)} bytes)")
            except (socket.error, OSError) as e:
                self._running = False
                logger.error(f"Failed to send command: {e}")
                raise AgentConnectionError(f"Failed to send command: {e}") from e

    def set_event_callback(self, callback: AgentClientEventHandler) -> None:
        self._on_event_received = callback

    def set_error_callback(self, callback: Callable[[Exception], None]) -> None:
        self._on_error = callback

    def _receive_loop(self) -> None:
        logger.debug("Receiver loop started")
        buffer = bytearray()

        while self._running:
            try:
                with self._lock:
                    if not self._socket:
                        break
                    sock = self._socket

                sock.settimeout(0.5)
                try:
                    data = sock.recv(4096)
                except socket.timeout:
                    continue

                if not data:
                    logger.warning("Connection closed by agent")
                    self._handle_error(AgentConnectionError("Connection closed by agent"))
                    break

                logger.debug(f"Received {len(data)} bytes")
                buffer.extend(data)

                while True:
                    frame = ProtocolCodec.decode_frame(buffer)
                    if frame is None:
                        break

                    try:
                        event = events_pb2.Event()
                        event.ParseFromString(frame)
                        logger.debug(f"Received event (operation_id: {event.operation_id})")

                        if self._on_event_received:
                            self._on_event_received(event)
                    except Exception as e:
                        logger.error(f"Failed to parse event: {e}")
                        self._handle_error(AgentConnectionError(f"Failed to parse event: {e}"))

            except (socket.error, OSError) as e:
                if self._running:
                    logger.error(f"Connection error: {e}")
                    self._handle_error(AgentConnectionError(f"Connection error: {e}"))
                break
            except Exception as e:
                logger.error(f"Unexpected error in receiver: {e}")
                self._handle_error(AgentConnectionError(f"Unexpected error in receiver: {e}"))
                break

        self._running = False
        logger.debug("Receiver loop stopped")

    def _handle_error(self, error: Exception) -> None:
        if self._on_error:
            try:
                self._on_error(error)
            except Exception:
                pass

    @property
    def is_connected(self) -> bool:
        return self._running and self._socket is not None

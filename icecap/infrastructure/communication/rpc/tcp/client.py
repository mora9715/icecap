import logging
from icecap.agent.v1 import commands_pb2, events_pb2
from .connection import TcpConnection
from .dispatcher import EventDispatcher
from icecap.infrastructure.communication.rpc.exceptions import (
    AgentConnectionError,
    AgentTimeoutError,
)
from icecap.infrastructure.communication.rpc.interface import AgentClientEventHandler

logger = logging.getLogger(__name__)


class TCPAgentClient:
    def __init__(self, host: str = "localhost", port: int = 5050):
        self._host = host
        self._port = port
        self._connection = TcpConnection()
        self._dispatcher = EventDispatcher()
        self._connected = False

        self._connection.set_event_callback(self._on_event_received)
        logger.debug(f"TCPAgentClient initialized for {host}:{port}")

    def connect(self, timeout: float = 5.0) -> None:
        if self._connected:
            logger.debug(f"Already connected to {self._host}:{self._port}")
            return

        logger.info(f"Connecting to agent at {self._host}:{self._port}")
        self._connection.connect(self._host, self._port, timeout)
        self._connected = True
        logger.info(f"Successfully connected to agent at {self._host}:{self._port}")

    def close(self) -> None:
        if not self._connected:
            return

        logger.info(f"Closing connection to agent at {self._host}:{self._port}")
        self._connected = False
        self._connection.close()
        self._dispatcher.clear_handlers()

    def send(self, command: commands_pb2.Command, timeout: float = 5.0) -> events_pb2.Event:
        if not self._connected:
            logger.error("Attempted to send command while not connected to agent")
            raise AgentConnectionError("Not connected to agent")

        if not command.operation_id:
            logger.error("Attempted to send command without operation_id")
            raise ValueError("Command must have an operation_id")

        logger.debug(f"Sending command with operation_id: {command.operation_id}")
        waiter = self._dispatcher.register_waiter(command.operation_id)

        try:
            self._connection.send_command(command)

            if not waiter.event.wait(timeout=timeout):
                logger.error(f"Timeout waiting for response to operation {command.operation_id}")
                raise AgentTimeoutError(
                    f"Timeout waiting for response to operation {command.operation_id}"
                )

            if waiter.result is None:
                logger.error(f"No response received for operation {command.operation_id}")
                raise AgentConnectionError(
                    f"No response received for operation {command.operation_id}"
                )

            logger.debug(f"Received response for operation {command.operation_id}")
            return waiter.result
        finally:
            self._dispatcher.unregister_waiter(command.operation_id)

    def add_event_handler(self, callback: AgentClientEventHandler) -> None:
        logger.debug("Adding event handler")
        self._dispatcher.add_handler(callback)

    def remove_event_handler(self, callback: AgentClientEventHandler) -> None:
        logger.debug("Removing event handler")
        self._dispatcher.remove_handler(callback)

    def _on_event_received(self, event: events_pb2.Event) -> None:
        self._dispatcher.dispatch_event(event)

    def is_connected(self) -> bool:
        return self._connected and self._connection.is_connected

    def __del__(self) -> None:
        """Close the connection on deletion."""
        self.close()

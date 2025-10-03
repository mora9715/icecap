from typing import Protocol
from icecap.agent.v1 import commands_pb2, events_pb2


class AgentClientEventHandler(Protocol):
    """Callback protocol for handling agent events.

    Can be either class-based or function-based.
    """

    def __call__(self, event: events_pb2.Event) -> None:
        """Handle an agent event.

        Args:
            event: The event received from the agent
        """


class AgentClient(Protocol):
    """High-level client for communicating with icecap-agent."""

    def connect(self, timeout: float = 5.0) -> None:
        """Connect to the agent.

        Args:
            timeout: Connection timeout in seconds

        Raises:
            AgentConnectionError: If connection fails
        """

    def close(self) -> None:
        """Close the connection to the agent."""

    def send(self, command: commands_pb2.Command, timeout: float = 5.0) -> events_pb2.Event:
        """Send a command and wait for the response event.

        Args:
            command: Command protobuf to send
            timeout: Maximum time to wait for response in seconds (None = wait forever)

        Returns:
            The response event with matching operation_id

        Raises:
            AgentConnectionError: If not connected or connection fails
            AgentTimeoutError: If no response is received within timeout
        """

    def add_event_handler(self, callback: AgentClientEventHandler) -> None:
        """Add an event handler for all received events.

        Args:
            callback: Function to call for each event
        """

    def remove_event_handler(self, callback: AgentClientEventHandler) -> None:
        """Remove an event handler.

        Args:
            callback: Handler to remove
        """

    def is_connected(self) -> bool:
        """Check if the client is connected to the agent."""

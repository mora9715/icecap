import logging
import threading
from typing import Dict, List

from icecap.agent.v1 import events_pb2
from icecap.infrastructure.communication.rpc.interface import AgentClientEventHandler

logger = logging.getLogger(__name__)


class EventDispatcher:
    """Routes incoming events to waiting operations and registered handlers.

    Thread-safe dispatcher that:
    - Matches events to waiting operations by operation_id
    - Dispatches all events to registered handler callbacks
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._waiters: Dict[str, "WaiterContext"] = {}
        self._handlers: List[AgentClientEventHandler] = []

    def register_waiter(self, operation_id: str) -> "WaiterContext":
        with self._lock:
            context = WaiterContext()
            self._waiters[operation_id] = context
            logger.debug(f"Registered waiter for operation: {operation_id}")
            return context

    def unregister_waiter(self, operation_id: str) -> None:
        with self._lock:
            self._waiters.pop(operation_id, None)
            logger.debug(f"Unregistered waiter for operation: {operation_id}")

    def dispatch_event(self, event: events_pb2.Event) -> None:
        waiter = None
        with self._lock:
            if event.operation_id in self._waiters:
                waiter = self._waiters[event.operation_id]
            handlers = list(self._handlers)

        if waiter:
            logger.debug(f"Dispatching event to waiter for operation: {event.operation_id}")
            waiter.result = event
            waiter.event.set()

        if handlers:
            logger.debug(f"Dispatching event to {len(handlers)} handler(s)")
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.warning(f"Event handler raised exception: {e}")

    def add_handler(self, callback: AgentClientEventHandler) -> None:
        with self._lock:
            if callback not in self._handlers:
                self._handlers.append(callback)
                logger.debug(f"Added event handler (total: {len(self._handlers)})")

    def remove_handler(self, callback: AgentClientEventHandler) -> None:
        with self._lock:
            if callback in self._handlers:
                self._handlers.remove(callback)
                logger.debug(f"Removed event handler (total: {len(self._handlers)})")

    def clear_handlers(self) -> None:
        with self._lock:
            count = len(self._handlers)
            self._handlers.clear()
            logger.debug(f"Cleared {count} event handler(s)")


class WaiterContext:
    """Context for a waiting operation."""

    def __init__(self) -> None:
        self.event = threading.Event()
        self.result: events_pb2.Event | None = None

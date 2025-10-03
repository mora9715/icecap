import threading
from typing import Dict, List

from icecap.agent.v1 import events_pb2
from icecap.infrastructure.communication.rpc.interface import AgentClientEventHandler


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
            return context

    def unregister_waiter(self, operation_id: str) -> None:
        with self._lock:
            self._waiters.pop(operation_id, None)

    def dispatch_event(self, event: events_pb2.Event) -> None:
        waiter = None
        with self._lock:
            if event.operation_id in self._waiters:
                waiter = self._waiters[event.operation_id]
            handlers = list(self._handlers)

        if waiter:
            waiter.result = event
            waiter.event.set()

        for handler in handlers:
            try:
                handler(event)
            except Exception:
                pass

    def add_handler(self, callback: AgentClientEventHandler) -> None:
        with self._lock:
            if callback not in self._handlers:
                self._handlers.append(callback)

    def remove_handler(self, callback: AgentClientEventHandler) -> None:
        with self._lock:
            if callback in self._handlers:
                self._handlers.remove(callback)

    def clear_handlers(self) -> None:
        with self._lock:
            self._handlers.clear()


class WaiterContext:
    """Context for a waiting operation."""

    def __init__(self) -> None:
        self.event = threading.Event()
        self.result: events_pb2.Event | None = None

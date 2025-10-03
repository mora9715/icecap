from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EVENT_TYPE_UNSPECIFIED: _ClassVar[EventType]
    EVENT_TYPE_LUA_VARIABLE_READ: _ClassVar[EventType]
    EVENT_TYPE_OPERATION_SUCCEEDED: _ClassVar[EventType]
    EVENT_TYPE_OPERATION_FAILED: _ClassVar[EventType]
EVENT_TYPE_UNSPECIFIED: EventType
EVENT_TYPE_LUA_VARIABLE_READ: EventType
EVENT_TYPE_OPERATION_SUCCEEDED: EventType
EVENT_TYPE_OPERATION_FAILED: EventType

class LuaVariableReadEventPayload(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("id", "operation_id", "type", "lua_variable_read_event_payload")
    ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LUA_VARIABLE_READ_EVENT_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    id: str
    operation_id: str
    type: EventType
    lua_variable_read_event_payload: LuaVariableReadEventPayload
    def __init__(self, id: _Optional[str] = ..., operation_id: _Optional[str] = ..., type: _Optional[_Union[EventType, str]] = ..., lua_variable_read_event_payload: _Optional[_Union[LuaVariableReadEventPayload, _Mapping]] = ...) -> None: ...

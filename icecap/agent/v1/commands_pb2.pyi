from icecap.agent.v1 import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommandType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    COMMAND_TYPE_UNSPECIFIED: _ClassVar[CommandType]
    COMMAND_TYPE_LUA_EXECUTE: _ClassVar[CommandType]
    COMMAND_TYPE_LUA_READ_VARIABLE: _ClassVar[CommandType]
    COMMAND_TYPE_CLICK_TO_MOVE: _ClassVar[CommandType]

class ClickToMoveAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLICK_TO_MOVE_ACTION_UNSPECIFIED: _ClassVar[ClickToMoveAction]
    CLICK_TO_MOVE_ACTION_FACE_TARGET: _ClassVar[ClickToMoveAction]
    CLICK_TO_MOVE_ACTION_FACE: _ClassVar[ClickToMoveAction]
    CLICK_TO_MOVE_ACTION_MOVE: _ClassVar[ClickToMoveAction]
COMMAND_TYPE_UNSPECIFIED: CommandType
COMMAND_TYPE_LUA_EXECUTE: CommandType
COMMAND_TYPE_LUA_READ_VARIABLE: CommandType
COMMAND_TYPE_CLICK_TO_MOVE: CommandType
CLICK_TO_MOVE_ACTION_UNSPECIFIED: ClickToMoveAction
CLICK_TO_MOVE_ACTION_FACE_TARGET: ClickToMoveAction
CLICK_TO_MOVE_ACTION_FACE: ClickToMoveAction
CLICK_TO_MOVE_ACTION_MOVE: ClickToMoveAction

class ClickToMovePayload(_message.Message):
    __slots__ = ("action", "precision", "player_base_address", "position", "interact_entity_guid")
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    PLAYER_BASE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    INTERACT_ENTITY_GUID_FIELD_NUMBER: _ClassVar[int]
    action: ClickToMoveAction
    precision: float
    player_base_address: int
    position: _common_pb2.Position
    interact_entity_guid: int
    def __init__(self, action: _Optional[_Union[ClickToMoveAction, str]] = ..., precision: _Optional[float] = ..., player_base_address: _Optional[int] = ..., position: _Optional[_Union[_common_pb2.Position, _Mapping]] = ..., interact_entity_guid: _Optional[int] = ...) -> None: ...

class LuaExecutePayload(_message.Message):
    __slots__ = ("executable_code",)
    EXECUTABLE_CODE_FIELD_NUMBER: _ClassVar[int]
    executable_code: str
    def __init__(self, executable_code: _Optional[str] = ...) -> None: ...

class LuaReadVariablePayload(_message.Message):
    __slots__ = ("variable_name",)
    VARIABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    variable_name: str
    def __init__(self, variable_name: _Optional[str] = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("id", "operation_id", "type", "lua_execute_payload", "lua_read_variable_payload", "click_to_move_payload")
    ID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LUA_EXECUTE_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    LUA_READ_VARIABLE_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    CLICK_TO_MOVE_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    id: str
    operation_id: str
    type: CommandType
    lua_execute_payload: LuaExecutePayload
    lua_read_variable_payload: LuaReadVariablePayload
    click_to_move_payload: ClickToMovePayload
    def __init__(self, id: _Optional[str] = ..., operation_id: _Optional[str] = ..., type: _Optional[_Union[CommandType, str]] = ..., lua_execute_payload: _Optional[_Union[LuaExecutePayload, _Mapping]] = ..., lua_read_variable_payload: _Optional[_Union[LuaReadVariablePayload, _Mapping]] = ..., click_to_move_payload: _Optional[_Union[ClickToMovePayload, _Mapping]] = ...) -> None: ...

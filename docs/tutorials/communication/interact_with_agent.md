# Interacting with the Icecap Agent

## Overview

The [icecap-agent](https://github.com/mora9715/icecap-agent) is a DLL that can be injected into the World of Warcraft 3.3.5a client process, providing an asynchronous RPC interface for programmatic interaction with the game. The agent runs inside the game process and exposes a TCP server (default port 5050) that accepts Protocol Buffer-encoded commands and publishes events.

### Key Features

- **Embedded TCP Server**: Listens on port 5050 for client connections
- **Command Execution**: Execute Lua code, read Lua variables, and control character movement
- **Event Publishing**: Asynchronous event notifications for command results
- **Protocol Buffers**: Type-safe message serialization

## Prerequisites

Before you can interact with the agent, you need to:

1. **Get the icecap-agent DLL**:
   Download the latest release from [icecap-agent releases](https://github.com/mora9715/icecap-agent/releases)

2. **Inject the DLL**: Inject `injector.dll` into your running WoW 3.3.5a (build 12340) client using any DLL injector

3. **Verify injection**: Check the logs at `%TEMP%\icecap-agent\icecap-agent.log`

4. **Install icecap**: Ensure you have the icecap Python package with RPC support

## Getting Started

### Connecting to the Agent

The simplest way to connect to the agent is using the factory function:

```python
from icecap.infrastructure.communication.rpc.factory import get_agent_client

# Create the client
agent_client = get_agent_client()

# Connect to the agent (timeout defaults to 5.0 seconds)
agent_client.connect()

# Check if connected
if agent_client.is_connected():
    print("Connected to agent!")
```

### Closing the Connection

Always close the connection when you're done:

```python
agent_client.close()
```

## Available Commands

The agent supports three types of commands, all defined in the corresponding [.proto](https://github.com/mora9715/icecap-contracts/blob/main/icecap/agent/v1/commands.proto) file:

### 1. Lua Execute

Execute arbitrary Lua code in the game client. This does not return a value directly.

```python
from uuid import uuid4
from icecap.agent.v1.commands_pb2 import (
    Command,
    CommandType,
    LuaExecutePayload,
)

result = agent_client.send(
    Command(
        id=str(uuid4()),
        operation_id=str(uuid4()),
        type=CommandType.COMMAND_TYPE_LUA_EXECUTE,
        lua_execute_payload=LuaExecutePayload(
            executable_code='health = UnitHealth("player")'
        ),
    )
)
```

### 2. Lua Read Variable

Read the value of a Lua variable that was previously set:

```python
from icecap.agent.v1.commands_pb2 import (
    Command,
    CommandType,
    LuaReadVariablePayload,
)

result = agent_client.send(
    Command(
        id=str(uuid4()),
        operation_id=str(uuid4()),
        type=CommandType.COMMAND_TYPE_LUA_READ_VARIABLE,
        lua_read_variable_payload=LuaReadVariablePayload(
            variable_name='health'
        ),
    )
)

# Access the result
if result.type == EventType.EVENT_TYPE_LUA_VARIABLE_READ:
    health_value = result.lua_variable_read_event_payload.result
    print(f"Player health: {health_value}")
```

### 3. Click-to-Move

Control character movement using the game's click-to-move system:

```python
from icecap.agent.v1.commands_pb2 import (
    Command,
    CommandType,
    ClickToMovePayload,
    ClickToMoveAction,
)
from icecap.agent.v1.common_pb2 import Position

result = agent_client.send(
    Command(
        id=str(uuid4()),
        operation_id=str(uuid4()),
        type=CommandType.COMMAND_TYPE_CLICK_TO_MOVE,
        click_to_move_payload=ClickToMovePayload(
            action=ClickToMoveAction.CLICK_TO_MOVE_ACTION_MOVE,
            precision=0.5,  # Movement precision in yards
            player_base_address=0x12345678,  # Base address of player object
            position=Position(x=100.0, y=200.0, z=50.0),
        ),
    )
)
```

#### Click-to-Move Actions

- `CLICK_TO_MOVE_ACTION_FACE_TARGET`: Face a target entity
- `CLICK_TO_MOVE_ACTION_FACE`: Face a specific direction
- `CLICK_TO_MOVE_ACTION_MOVE`: Move to a position

## Understanding Events

Every command sent to the agent produces an event response. Events are defined in `icecap.agent.v1.events_pb2`:

### Event Types

- `EVENT_TYPE_LUA_VARIABLE_READ`: Response to a Lua variable read command
- `EVENT_TYPE_OPERATION_SUCCEEDED`: Command completed successfully
- `EVENT_TYPE_OPERATION_FAILED`: Command failed

### Processing Event Responses

The `send()` method returns an `Event` object that corresponds to your command:

```python
from icecap.agent.v1.events_pb2 import EventType

result = agent_client.send(command)

if result.type == EventType.EVENT_TYPE_OPERATION_SUCCEEDED:
    print("Command succeeded!")
elif result.type == EventType.EVENT_TYPE_OPERATION_FAILED:
    print("Command failed!")
elif result.type == EventType.EVENT_TYPE_LUA_VARIABLE_READ:
    value = result.lua_variable_read_event_payload.result
    print(f"Variable value: {value}")
```

## Event Handlers

For asynchronous event processing, you can register event handlers that are called for all received events:

```python
from icecap.agent.v1.events_pb2 import Event, EventType

def my_event_handler(event: Event) -> None:
    """Handle incoming events from the agent."""
    print(f"Received event: {event.id}, type: {event.type}")

    if event.type == EventType.EVENT_TYPE_LUA_VARIABLE_READ:
        print(f"Variable value: {event.lua_variable_read_event_payload.result}")

# Register the handler
agent_client.add_event_handler(my_event_handler)

# Your handler will be called for all events
# ...

# Remove the handler when done
agent_client.remove_event_handler(my_event_handler)
```

## Complete Example: Reading Player Health

Here's a complete example that reads the player's current health:

```python
from uuid import uuid4
from icecap.infrastructure.communication.rpc.factory import get_agent_client
from icecap.agent.v1.commands_pb2 import (
    Command,
    CommandType,
    LuaExecutePayload,
    LuaReadVariablePayload,
)
from icecap.agent.v1.events_pb2 import EventType

# Create and connect to the agent
agent_client = get_agent_client()
agent_client.connect()

try:
    # Step 1: Execute Lua to store health in a variable
    agent_client.send(
        Command(
            id=str(uuid4()),
            operation_id=str(uuid4()),
            type=CommandType.COMMAND_TYPE_LUA_EXECUTE,
            lua_execute_payload=LuaExecutePayload(
                executable_code='health = UnitHealth("player")'
            ),
        )
    )

    # Step 2: Read the variable
    result = agent_client.send(
        Command(
            id=str(uuid4()),
            operation_id=str(uuid4()),
            type=CommandType.COMMAND_TYPE_LUA_READ_VARIABLE,
            lua_read_variable_payload=LuaReadVariablePayload(
                variable_name='health'
            ),
        )
    )

    # Step 3: Process the result
    if result.type == EventType.EVENT_TYPE_LUA_VARIABLE_READ:
        health = result.lua_variable_read_event_payload.result
        print(f"Player health: {health}")
    else:
        print("Failed to read health variable")

finally:
    # Always close the connection
    agent_client.close()
```

## Error Handling

The agent client can raise several exceptions:

```python
from icecap.infrastructure.communication.rpc.tcp.exceptions import (
    AgentConnectionError,
    AgentTimeoutError,
)

try:
    agent_client.connect(timeout=10.0)
    result = agent_client.send(command, timeout=5.0)
except AgentConnectionError as e:
    print(f"Connection error: {e}")
except AgentTimeoutError as e:
    print(f"Command timed out: {e}")
```

### Common Issues

1. **Connection refused**: Ensure the agent DLL is injected and the TCP server is running
2. **Timeout errors**: Increase the timeout value or check if the game is responding
3. **Invalid commands**: Verify your Protocol Buffer messages are properly constructed

## Best Practices

1. **Use UUIDs for IDs**: Always generate unique IDs for `id` and `operation_id` fields
2. **Handle timeouts**: Set appropriate timeout values based on command complexity
3. **Close connections**: Always close the client when done to free resources
4. **Check event types**: Always verify the event type before accessing payload fields
5. **Error handling**: Wrap send operations in try-except blocks
6. **Two-step pattern**: Use the execute-then-read pattern for Lua operations that return values

## Advanced Usage

### Custom Timeout Values

```python
# Custom connection timeout
agent_client.connect(timeout=10.0)

# Custom send timeout (wait indefinitely)
result = agent_client.send(command, timeout=None)
```

### Multiple Event Handlers

You can register multiple event handlers for different purposes:

```python
def logging_handler(event: Event) -> None:
    print(f"[LOG] {event.id}: {event.type}")

def metrics_handler(event: Event) -> None:
    # Record metrics
    pass

agent_client.add_event_handler(logging_handler)
agent_client.add_event_handler(metrics_handler)
```

## Reference

- **Agent Repository**: [github.com/mora9715/icecap-agent](https://github.com/mora9715/icecap-agent)
- **Commands and Events definitions**: [github.com/mora9715/icecap-contracts/tree/main/icecap/agent/v1](https://github.com/mora9715/icecap-contracts/tree/main/icecap/agent/v1)


# Getting Started with Icecap

This guide will help you get up and running with Icecap quickly.

## Installation

Install Icecap from PyPI using pip:

```bash
pip install icecap
```


## Basic Usage

Here's a minimal example to get you started with Icecap:

```python title="Finding players around you"
from icecap.infrastructure import (
    get_wow_process_id,
    get_memory_manager,
    GameDriver,
    PlayerRepository,
)

memory_manager = get_memory_manager(get_wow_process_id())
driver = GameDriver(memory_manager)
player_repository = PlayerRepository(driver)

for player in player_repository.yield_players():
    print(player)
```

Let's break down what's happening in this example:

1. First, we create a memory manager responsible for reading from the game's memory.
2. Next, we create a `GameDriver` instance that uses the memory manager to interact with the game.
3. We then create a `PlayerRepository`, which provides access to player entities in the game.
4. Finally, we iterate over all players in the game and print their details.

## Next Steps

Once you're familiar with the basics, check out the [Tutorials](tutorials.md) for more detailed examples or explore the [API Reference](api/index.md) for complete documentation of all available components.

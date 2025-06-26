# Driver

**Driver** is one of the core modules of the library. 

The main purpose of the module is to encapsulate the low-level interactions with the game client's memory and provide an 
interface for accessing and manipulating game data.
    
Key responsibilities include:

- Memory access and manipulation
- Game entity management
- Process interaction handling

## Important implementation details

The [`GameDriver`][icecap.infrastructure.driver.GameDriver] class automatically handles the following scenarios:

- Game client recreation
- Local player change
- Logging out & Logging in

The driver detects any of these events and automatically reinitiates affected dependencies.

::: icecap.infrastructure.driver
    options:
        show_submodules: false
        summary:
            classes: true
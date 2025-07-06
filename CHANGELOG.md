# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2025-07-06

### Features

- Add an ability to get the current map ID using the object manager
- Add an ability to work with MPQ archives

## [0.3.0] - 2025-06-26

### Features

- Add an ability to calculate the distance between objects with position 
- Game driver:
  - Add an ability to detect if the game is running
  - Automatically recreate all dependent objects when the game state changes. I.e., the consumer closed and opened the game, logged out & logged in, player switch

## [0.2.2] - 2025-06-24

### Bug Fixes

- Get the correct position offset for game objects
- Add a game object name mapping file to the library as a resource

## [0.2.1] - 2025-06-22

### Bug Fixes

- Correctly discover package submodules via setuptools

## [0.2.0] - 2025-06-22

### Features

- Introduce full support for a Windows operating system

### Bug Fixes

- Add 4 bytes padding after Z coordinate in ObjectPosition to read the correct rotation value
- Swap x and y coordinate offsets in ObjectPosition to represent c struct correctly

## [0.1.1] - 2025-06-22

Initial release with basic functionality.
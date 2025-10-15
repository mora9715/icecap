# Logging Guide

## Overview

IceCap uses Python's standard `logging` module with explicit logger names for different components.

## Default Behavior

By default, IceCap:
- Outputs logs to **stdout** (console)
- Uses **INFO** log level

To enable logging, call `icecap.configure_logging()` or use standard Python logging configuration.

## Configuration

### Basic Usage

```python
import icecap
import logging

# Enable default logging (INFO to stdout)
icecap.configure_logging()

# Enable debug logging
icecap.configure_logging(level=logging.DEBUG)

# Custom format
icecap.configure_logging(
  level=logging.INFO,
  log_format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
```

### Standard Python logging Configuration

IceCap integrates with standard Python logging:

```python
import logging

# Configure Python logging normally
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler()]
)

# IceCap will use this configuration automatically
# No need to call icecap.configure_logging()
```

## Best Practices

1. **In production**: Use WARNING or ERROR level to reduce noise
2. **During development**: Use DEBUG level for detailed information
3. **For performance-critical code**: Check `logger.isEnabledFor(DEBUG)` before expensive operations
4. **For libraries/frameworks**: Let consumers control logging configuration
5. **For applications**: Configure logging early in your application startup
6. **Use appropriate levels**: Don't log everything as ERROR or INFO

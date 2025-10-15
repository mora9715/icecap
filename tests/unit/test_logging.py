import logging
import importlib
from io import StringIO


import icecap


class TestLoggingConfiguration:
    """Test suite for icecap logging configuration"""

    def setup_method(self):
        """Reset logging configuration before each test"""
        # Clear all handlers from icecap and component loggers
        for logger_name in [
            "icecap",
            "memory",
            "driver",
            "communication",
            "process",
            "resource",
            "ai",
            "services",
        ]:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)

    def test_configure_logging_default(self):
        """Test default configuration (INFO, stdout)"""
        icecap.configure_logging()

        # Check icecap logger
        logger = logging.getLogger("icecap")
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check component loggers are also configured
        for component in ["memory", "driver", "ai"]:
            component_logger = logging.getLogger(component)
            assert component_logger.level == logging.INFO

    def test_configure_logging_debug_level(self):
        """Test setting DEBUG level"""
        icecap.configure_logging(level=logging.DEBUG)

        logger = logging.getLogger("icecap")
        assert logger.level == logging.DEBUG

        # Component loggers should also be DEBUG
        driver_logger = logging.getLogger("driver")
        assert driver_logger.level == logging.DEBUG

    def test_configure_logging_warning_level(self):
        """Test setting WARNING level"""
        icecap.configure_logging(level=logging.WARNING)

        logger = logging.getLogger("icecap")
        assert logger.level == logging.WARNING

    def test_configure_logging_custom_format(self):
        """Test custom format string"""
        custom_format = "%(name)s - %(message)s"
        icecap.configure_logging(log_format=custom_format)

        logger = logging.getLogger("icecap")
        formatter = logger.handlers[0].formatter
        assert formatter._fmt == custom_format

    def test_configure_logging_multiple_handlers(self):
        """Test multiple handlers"""
        stream_handler = logging.StreamHandler()
        string_stream = StringIO()
        file_handler = logging.StreamHandler(string_stream)

        icecap.configure_logging(handlers=[stream_handler, file_handler])

        logger = logging.getLogger("icecap")
        assert len(logger.handlers) == 2

        # Component loggers should also have both handlers
        memory_logger = logging.getLogger("memory")
        assert len(memory_logger.handlers) == 2

    def test_logger_hierarchy(self):
        """Test that component loggers are configured"""
        icecap.configure_logging(level=logging.INFO)

        # Component loggers should have their own level set
        component_logger = logging.getLogger("driver")
        assert component_logger.level == logging.INFO

    def test_log_output(self):
        """Test that logs are actually output"""
        # Create string buffer to capture output
        stream = StringIO()
        handler = logging.StreamHandler(stream)

        icecap.configure_logging(
            level=logging.INFO,
            handlers=[handler],
            log_format="%(levelname)s: %(message)s",
        )

        logger = logging.getLogger("memory")
        logger.info("Test message")

        output = stream.getvalue()
        assert "INFO: Test message" in output

    def test_configure_logging_clears_existing_handlers(self):
        """Test that reconfiguring clears old handlers"""
        # First configuration
        icecap.configure_logging(level=logging.INFO)
        logger = logging.getLogger("icecap")
        initial_handler_count = len(logger.handlers)

        # Reconfigure
        icecap.configure_logging(level=logging.DEBUG)

        # Should still have the same number of handlers, not double
        assert len(logger.handlers) == initial_handler_count

    def test_component_logger_independence(self):
        """Test that component logger levels can be changed independently"""
        icecap.configure_logging(level=logging.INFO)

        # Change one component logger
        memory_logger = logging.getLogger("memory")
        memory_logger.setLevel(logging.DEBUG)

        # Verify it changed
        assert memory_logger.level == logging.DEBUG

        # Other component loggers should still be INFO
        driver_logger = logging.getLogger("driver")
        assert driver_logger.level == logging.INFO

    def test_all_component_loggers_configured(self):
        """Test that all component loggers are configured"""
        icecap.configure_logging(level=logging.INFO)

        component_loggers = [
            "memory",
            "driver",
            "communication",
            "process",
            "resource",
            "ai",
            "services",
        ]

        for component in component_loggers:
            logger = logging.getLogger(component)
            assert logger.level == logging.INFO
            assert len(logger.handlers) > 0

    def test_configure_logging_with_file_handler(self):
        """Test configuration with file handler (using StringIO as mock file)"""
        import tempfile
        import os

        # Use temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
            temp_file = f.name

        try:
            file_handler = logging.FileHandler(temp_file)
            icecap.configure_logging(
                level=logging.INFO,
                handlers=[file_handler],
            )

            logger = logging.getLogger("ai")
            logger.info("Test file logging")

            # Close handler to flush
            file_handler.close()

            # Read the file
            with open(temp_file, "r") as f:
                content = f.read()

            assert "Test file logging" in content
            assert "[INFO]" in content
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_configure_logging_respects_format_parameter(self):
        """Test that the format parameter is applied to handlers"""
        stream = StringIO()
        handler = logging.StreamHandler(stream)

        custom_format = "%(levelname)s|%(name)s|%(message)s"
        icecap.configure_logging(
            level=logging.INFO,
            handlers=[handler],
            log_format=custom_format,
        )

        logger = logging.getLogger("communication")
        logger.info("Connection established")

        output = stream.getvalue()
        # Should match custom format: LEVEL|NAME|MESSAGE
        assert "INFO|communication|Connection established" in output

    def test_logging_is_silent_by_default(self):
        """Test that logging is silent without configuration"""
        # Reload to get fresh state
        importlib.reload(icecap)

        stream = StringIO()
        # Create a handler at root level to catch any stray output
        root_handler = logging.StreamHandler(stream)
        logging.root.addHandler(root_handler)

        try:
            # Try to log without configuring
            logger = logging.getLogger("memory")
            logger.info("This should not appear")

            output = stream.getvalue()
            # Should be empty because of NullHandler
            assert "This should not appear" not in output
        finally:
            logging.root.removeHandler(root_handler)

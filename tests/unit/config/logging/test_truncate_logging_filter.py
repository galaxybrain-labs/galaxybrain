import io
import logging
from contextlib import redirect_stdout

from griptape.config import config
from griptape.config.logging import TruncateLoggingFilter
from griptape.structures import Agent


class TestTruncateLoggingFilter:
    def test_filter(self):
        # use the filter in an Agent
        logger = logging.getLogger(config.logging.logger_name)
        logger.addFilter(TruncateLoggingFilter(max_log_length=0))
        agent = Agent()
        # use a context manager to capture the stdout
        with io.StringIO() as buf, redirect_stdout(buf):
            agent.run("test")
            output = buf.getvalue()
            assert "more characters]" in output

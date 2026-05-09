import logging
import os
import tempfile

from demo_server.logging_config import setup_logging


def test_log_file_created():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_logging(verbose=False, log_dir=tmpdir)
        log_file = os.path.join(tmpdir, "demo-server.log")
        logging.getLogger("demo_server").info("test entry")
        assert os.path.exists(log_file)


def test_verbose_sets_debug_level():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_logging(verbose=True, log_dir=tmpdir)
        assert logging.getLogger().level == logging.DEBUG


def test_non_verbose_sets_info_level():
    with tempfile.TemporaryDirectory() as tmpdir:
        setup_logging(verbose=False, log_dir=tmpdir)
        assert logging.getLogger().level == logging.INFO

"""
test_logging.py - Logging System Module Unit Tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import os
import pytest
from halpybot.packages.configmanager import config

logFile: str = str(config.logging.log_file)  # TODO: rewrite this to use Path objects.
logFolder = os.path.dirname(logFile)


@pytest.mark.asyncio
async def test_log_path():
    """Test that the log folder exists"""
    assert os.path.exists(logFolder)


@pytest.mark.asyncio
async def test_log_write():
    """Test that the log directory is writable"""
    with open(os.path.join(logFolder, "testFile.txt"), "w", encoding="UTF-8"):
        pass
    assert os.path.exists(f"{logFolder}/testFile.txt")


@pytest.mark.asyncio
async def test_log_delete():
    """Test that the log directory can be rotated"""
    os.remove(f"{logFolder}/testFile.txt")
    assert not os.path.exists(f"{logFolder}/testFile.txt")

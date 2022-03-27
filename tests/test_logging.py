"""
HalpyBOT v1.6

test_logging.py - Logging System Module Unit Tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import os
import pytest
from halpybot.packages.configmanager import config

logFile: str = config["Logging"]["log_file"]
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

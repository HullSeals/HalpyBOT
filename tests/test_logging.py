"""
HalpyBOT v1.5.2

test_logging.py - Logging System Module Unit Tests

Copyright (c) 2021 The Hull Seals,
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


# Test for Logging Directory Existence.
@pytest.mark.asyncio
async def test_log_path():
    assert os.path.exists(logFolder)


# Test if we can create a file in the log directory
@pytest.mark.asyncio
async def test_log_write():
    with open(os.path.join(logFolder, "testFile.txt"), "w", encoding='UTF-8'):
        pass
    assert os.path.exists(f"{logFolder}/testFile.txt")


# Test for log rotation
@pytest.mark.asyncio
async def test_log_delete():
    os.remove(f"{logFolder}/testFile.txt")
    assert not os.path.exists(f"{logFolder}/testFile.txt")

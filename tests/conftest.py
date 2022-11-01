from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def test_conf() -> None:
    dotenv_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        '.env',
    )
    load_dotenv(dotenv_file)

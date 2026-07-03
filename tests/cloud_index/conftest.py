from collections.abc import Generator
from functools import cache
from unittest.mock import patch

import pytest
from boto3 import Session


@pytest.fixture
def session() -> Generator[Session]:
    session = Session()
    with patch.object(session, "client", side_effect=cache(session.client)):
        yield session


@pytest.fixture
def offline_session() -> Generator[Session]:
    session = Session()
    error = AssertionError("test unexpectedly created an AWS client")
    with patch.object(session, "client", side_effect=error):
        yield session

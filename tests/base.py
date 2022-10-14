import pytest

from backend.core.context_vars import SESSION


class BaseRepoTest:

    @pytest.fixture(autouse=True)
    def _set_session(self, async_session):
        SESSION.set(async_session)
        yield
        SESSION.set(None)

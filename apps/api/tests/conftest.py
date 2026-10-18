"""Keep API test cases independent of the shared per-process rate limiter."""
import pytest
from vybe.main import app

@pytest.fixture(autouse=True)
def reset_test_rate_limit():
    yield
    node = app.middleware_stack
    while node is not None:
        if node.__class__.__name__ == "MatchRequestGuard":
            node._hits.clear()
            break
        node = getattr(node, "app", None)

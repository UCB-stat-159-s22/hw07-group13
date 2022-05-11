import pytest

def something_plugin():
    return 'nothing'


def pytest_configure():
    pytest.shared1 = something_plugin()
    pytest.shared2 = something_plugin()
    pytest.shared3 = something_plugin()
    pytest.shared4 = something_plugin()
    pytest.shared5 = something_plugin()
import logging

import pytest

from customer_service.config import Config


@pytest.fixture
def conf():
    configs = Config()
    return configs


def test_settings_loading(conf):
    logging.info(conf.model_dump())
    assert conf.agent_settings.model.startswith("gemini")

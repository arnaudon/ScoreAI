"""test settings"""

from shared.settings import Setting


def test_settings():
    """test settings"""
    setting = Setting(key="test_key", value="test_value")
    assert setting.key == "test_key"
    assert setting.value == "test_value"

from app.config.settings import settings


def test_settings_load():
    assert settings.PORT == 8000 or isinstance(settings.PORT, int)
    assert settings.WEIGHTS["skills"] == 0.50
    assert settings.WEIGHTS["experience"] == 0.20
    assert settings.WEIGHTS["responsibilities"] == 0.15
    assert settings.WEIGHTS["education"] == 0.05
    assert settings.WEIGHTS["preferred"] == 0.10
    assert sum(settings.WEIGHTS.values()) == 1.0

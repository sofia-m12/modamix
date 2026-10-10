from app.models.preferences import SearchPreferences
def test_preferences_default_to_jackets() -> None:
    assert SearchPreferences().category == "jacket"

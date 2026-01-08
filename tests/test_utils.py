import pytest
from app.utils import text_to_base64

@pytest.mark.run(order=100)
def test_text_to_base64():
    text = "{'message': 'Привет мир!!!'}"
    encoded = text_to_base64(text)
    assert encoded == 'eydtZXNzYWdlJzogJ9Cf0YDQuNCy0LXRgiDQvNC40YAhISEnfQ=='


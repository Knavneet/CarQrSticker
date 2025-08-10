import os
import pytest
from PIL import Image


@pytest.fixture
def test_assets_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")


@pytest.fixture
def test_output_dir(tmp_path):
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_qr_image():
    # Create a sample QR-sized image for testing
    img = Image.new("RGBA", (300, 300), "white")
    return img


@pytest.fixture
def template_path(test_assets_dir):
    return os.path.join(test_assets_dir, "sticQR_template.png")


@pytest.fixture
def phone_icon_path(test_assets_dir):
    return os.path.join(test_assets_dir, "phone_icon.png")

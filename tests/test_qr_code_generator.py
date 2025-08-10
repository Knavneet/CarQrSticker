import os
import pytest
import qrcode
from PIL import Image
from src.qr_code_generator import QRCodeGenerator, _create_rounded_qr


def test_qr_code_generator_init():
    # Test default initialization
    generator = QRCodeGenerator()
    assert generator.config["qr_style"] == "rounded"
    assert generator.config["icon_style"] == "modern"
    assert generator.icon_path is None

    # Test custom initialization
    custom_config = {"qr_style": "square", "corner_radius": 40}
    generator = QRCodeGenerator(style_config=custom_config)
    assert generator.config["qr_style"] == "square"
    assert generator.config["corner_radius"] == 40


def test_qr_code_generator_with_icon(phone_icon_path):
    generator = QRCodeGenerator(icon_path=phone_icon_path)
    assert generator.icon_path == phone_icon_path
    assert generator.config["icon_style"] == "custom"


def test_generate_qr_code():
    generator = QRCodeGenerator()
    qr_image = generator.generate("test123", size=300)

    # Check if image was created with correct properties
    assert isinstance(qr_image, Image.Image)
    # Size includes padding for frame and border
    assert qr_image.size[0] == qr_image.size[1]  # Should be square
    assert qr_image.size[0] >= 300  # Should be at least the requested size
    assert qr_image.mode == "RGBA"


def test_create_rounded_qr(sample_qr_image):
    rounded_qr = _create_rounded_qr(sample_qr_image, corner_radius=20)

    # Check if the image properties are correct
    assert isinstance(rounded_qr, Image.Image)
    assert rounded_qr.size == sample_qr_image.size
    assert rounded_qr.mode == "RGBA"


def test_qr_code_different_sizes():
    generator = QRCodeGenerator()
    sizes = [200, 400, 600]

    previous_size = 0
    for size in sizes:
        qr_image = generator.generate("test123", size=size)
        # Check that images are square and increase with requested size
        assert qr_image.size[0] == qr_image.size[1]  # Should be square
        assert qr_image.size[0] >= size  # Should be at least the requested size
        assert qr_image.size[0] > previous_size  # Should increase with requested size
        previous_size = qr_image.size[0]


def test_qr_code_generator_custom_config():
    custom_config = {
        "corner_radius": 40,
        "border_width": 8,
        "frame_color": (60, 60, 60, 255),
    }
    generator = QRCodeGenerator(style_config=custom_config)

    # Test if custom configuration was properly applied
    assert generator.config["corner_radius"] == 40
    assert generator.config["border_width"] == 8
    assert generator.config["frame_color"] == (60, 60, 60, 255)


def test_qr_code_with_icon_integration(phone_icon_path):
    generator = QRCodeGenerator(icon_path=phone_icon_path)
    qr_image = generator.generate("test_with_icon", size=400)

    # Check if image was created with correct properties
    assert isinstance(qr_image, Image.Image)
    assert qr_image.size[0] == qr_image.size[1]  # Should be square
    assert qr_image.size[0] >= 400  # Should be at least the requested size
    assert qr_image.mode == "RGBA"


def test_qr_code_no_border():
    generator = QRCodeGenerator(style_config={"border_width": 0})
    qr_image = generator.generate("test_no_border", size=300)

    # Check if the size is exactly the requested size (no border)
    assert qr_image.size == (300, 300)


def test_qr_code_no_frame(phone_icon_path):
    generator = QRCodeGenerator(
        icon_path=phone_icon_path, style_config={"frame_enabled": False}
    )
    qr_image = generator.generate("test_no_frame", size=300)

    # Check if image was created with correct properties
    assert isinstance(qr_image, Image.Image)
    assert qr_image.size[0] == qr_image.size[1]  # Should be square
    assert qr_image.size[0] >= 300  # Should be at least the requested size
    assert qr_image.mode == "RGBA"


def test_qr_code_invalid_icon_path():
    invalid_path = "non_existent_icon.png"
    generator = QRCodeGenerator(icon_path=invalid_path)

    # Should not raise an error, but handle it gracefully
    qr_image = generator.generate("test_invalid_icon", size=300)

    # Check if a valid QR code is still generated
    assert isinstance(qr_image, Image.Image)
    assert qr_image.size[0] == qr_image.size[1]  # Should be square
    assert qr_image.size[0] >= 300  # Should be at least the requested size
    assert qr_image.mode == "RGBA"


def test_icon_not_rgba(phone_icon_path, tmp_path):
    # Create a non-RGBA icon
    non_rgba_icon_path = tmp_path / "icon.jpg"
    Image.new("RGB", (100, 100)).save(non_rgba_icon_path)

    generator = QRCodeGenerator(icon_path=str(non_rgba_icon_path))
    qr_image = generator.generate("test_icon_not_rgba", size=300)
    assert qr_image.mode == "RGBA"


def test_qr_not_rgba(phone_icon_path):
    generator = QRCodeGenerator(icon_path=phone_icon_path)
    # Mock qr_img to be RGB
    original_make_image = qrcode.QRCode.make_image
    try:

        def mock_make_image(self, *args, **kwargs):
            return Image.new("RGB", (200, 200))

        qrcode.QRCode.make_image = mock_make_image
        qr_image = generator.generate("test_qr_not_rgba", size=300)
        assert qr_image.mode == "RGBA"
    finally:
        qrcode.QRCode.make_image = original_make_image


def test_no_frame_no_border(phone_icon_path):
    generator = QRCodeGenerator(
        icon_path=phone_icon_path,
        style_config={"frame_enabled": False, "border_width": 0},
    )
    qr_image = generator.generate("test_no_frame_no_border", size=300)
    assert qr_image.size == (300, 300)


def test_cutout_shape_circle(phone_icon_path):
    generator = QRCodeGenerator(
        icon_path=phone_icon_path, style_config={"cutout_shape": "circle"}
    )
    qr_image = generator.generate("test_cutout_shape_circle", size=300)
    assert qr_image.mode == "RGBA"

def test_generate_batch(tmpdir):
    generator = QRCodeGenerator()
    num_qrs = 5
    output_folder = str(tmpdir)
    image_paths = generator.generate_batch(num_qrs, 200, output_folder)

    assert len(image_paths) == num_qrs
    for image_path in image_paths:
        assert os.path.exists(image_path)
        assert os.path.basename(image_path).startswith("carqr_")
        assert os.path.basename(image_path).endswith(".png")

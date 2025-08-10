import os
import pytest
from PIL import Image
from src.sticker_generator import StickerGenerator


def test_sticker_generator_init(template_path):
    generator = StickerGenerator(template_path)
    assert isinstance(generator.template, Image.Image)
    assert generator.template.mode == "RGBA"


def test_create_sticker(template_path, sample_qr_image, test_output_dir):
    generator = StickerGenerator(template_path)
    output_path = os.path.join(test_output_dir, "test_sticker.png")

    # Test with default scale
    result = generator.create_sticker(
        sample_qr_image, position=(400, 400), output_path=output_path
    )

    assert os.path.exists(output_path)
    assert isinstance(result, Image.Image)


def test_create_sticker_with_scaling(template_path, sample_qr_image, test_output_dir):
    generator = StickerGenerator(template_path)
    output_path = os.path.join(test_output_dir, "test_sticker_scaled.png")

    # Test with scaling
    scale_factor = 0.5
    result = generator.create_sticker(
        sample_qr_image,
        position=(400, 400),
        output_path=output_path,
        scale_factor=scale_factor,
    )

    # Check if scaling was applied correctly
    expected_width = int(generator.template.width * scale_factor)
    expected_height = int(generator.template.height * scale_factor)
    assert result.size == (expected_width, expected_height)


def test_sticker_generator_rgb_conversion(
    template_path, sample_qr_image, test_output_dir
):
    # Create an RGB template for testing
    rgb_template = Image.new("RGB", (800, 600), "white")
    rgb_template_path = os.path.join(test_output_dir, "rgb_template.png")
    rgb_template.save(rgb_template_path)

    generator = StickerGenerator(rgb_template_path)
    output_path = os.path.join(test_output_dir, "test_sticker_rgb.png")

    result = generator.create_sticker(
        sample_qr_image, position=(400, 400), output_path=output_path
    )

    assert isinstance(result, Image.Image)
    assert os.path.exists(output_path)

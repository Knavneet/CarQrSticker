import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from exp_qr import main

@patch('uuid.uuid4')
@patch('exp_qr.StickerGenerator')
@patch('exp_qr.QRCodeGenerator')
def test_main_script_execution(mock_qr_generator, mock_sticker_generator, mock_uuid, tmp_path, phone_icon_path, template_path):
    """Test the main execution block of the experimental script."""
    # Setup mocks
    mock_uuid.return_value = 'test-uuid'
    mock_qr_instance = MagicMock()
    mock_sticker_instance = MagicMock()
    mock_qr_generator.return_value = mock_qr_instance
    mock_sticker_generator.return_value = mock_sticker_instance

    # Define the output path for the test
    output_path = tmp_path / "enhanced_qr_card.png"

    # Run the main function
    main(template_path, phone_icon_path, str(output_path))

    # Check if the script ran to completion
    mock_qr_generator.assert_called_once_with(icon_path=phone_icon_path)
    mock_sticker_generator.assert_called_once_with(template_path=template_path)
    mock_qr_instance.generate.assert_called_once_with(qr_id='test-uuid', size=700)
    mock_sticker_instance.create_sticker.assert_called_once_with(
        qr_image=mock_qr_instance.generate.return_value,
        position=(720, 1200),
        output_path=str(output_path),
        scale_factor=0.6
    )


import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from main import main


import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from main import main


import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from main import main


@patch("uuid.uuid4")
@patch("main.Image.open")
@patch("main.PDFGenerator")
@patch("main.StickerGenerator")
@patch("main.QRCodeGenerator")
def test_main_script_execution(
    mock_qr_generator,
    mock_sticker_generator,
    mock_pdf_generator,
    mock_image_open,
    mock_uuid,
    tmp_path,
    phone_icon_path,
    template_path,
):
    """Test the main execution block of the experimental script."""
    # Setup mocks
    mock_uuid.return_value = "test-uuid"
    mock_qr_instance = MagicMock()
    mock_sticker_instance = MagicMock()
    mock_pdf_instance = MagicMock()
    mock_qr_generator.return_value = mock_qr_instance
    mock_sticker_generator.return_value = mock_sticker_instance
    mock_pdf_generator.return_value = mock_pdf_instance
    mock_qr_instance.generate_batch.return_value = ["qr_path_1", "qr_path_2"]

    # Define the output path for the test
    output_path = tmp_path / "enhanced_qr_card.png"

    # Run the main function
    main(template_path, phone_icon_path, str(output_path), output_dir=str(tmp_path))

    # Check if the script ran to completion
    mock_qr_generator.assert_called_once_with(icon_path=phone_icon_path)
    mock_sticker_generator.assert_called_once_with(template_path=template_path)
    assert mock_sticker_instance.create_sticker.call_count == 2
    mock_pdf_instance.create_pdf_from_images.assert_called_once()

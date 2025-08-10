import os
import pytest
from unittest.mock import patch, MagicMock

try:
    from src.main import main
except ImportError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from src.main import main


@patch("uuid.uuid4")
@patch("src.main.Image.open")
@patch("src.main.PDFGenerator")
@patch("src.main.StickerGenerator")
@patch("src.main.QRCodeGenerator")
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
    # Setup mocks with consistent UUIDs
    # We need batch_uuid + qr_uuids, so 11 total
    mock_uuids = [f"test-uuid-{i}" for i in range(11)]  # 1 for batch + 10 for QRs
    mock_uuid.side_effect = mock_uuids

    mock_qr_instance = MagicMock()
    mock_sticker_instance = MagicMock()
    mock_pdf_instance = MagicMock()
    mock_qr_generator.return_value = mock_qr_instance
    mock_sticker_generator.return_value = mock_sticker_instance
    mock_pdf_generator.return_value = mock_pdf_instance

    # Mock the database to avoid actual DB operations
    mock_db = MagicMock()

    # Mock the QR paths with the UUIDs (excluding the batch UUID)
    qr_uuids = mock_uuids[1:]  # Skip the first UUID which will be used for batch_id
    mock_qr_paths = [f"qr_path_{uuid}" for uuid in qr_uuids]
    mock_qr_instance.generate_batch.return_value = mock_qr_paths

    # Define the output path for the test
    output_path = tmp_path / "enhanced_qr_card.png"

    # Setup database mock and run the main function
    with patch("src.main.Database", return_value=mock_db):
        # Run the main function
        main(template_path, phone_icon_path, str(output_path), output_dir=str(tmp_path))

        # Check if the script ran to completion
        mock_qr_generator.assert_called_once_with(icon_path=phone_icon_path)
        mock_sticker_generator.assert_called_once_with(template_path=template_path)

        # Should create stickers for all QR codes
        assert mock_sticker_instance.create_sticker.call_count == len(mock_qr_paths)

        # Verify PDF generation
        mock_pdf_instance.create_pdf_from_images.assert_called_once()

        # Verify QR batch generation with proper parameters
        mock_qr_instance.generate_batch.assert_called_once()
        _, call_kwargs = mock_qr_instance.generate_batch.call_args
        assert call_kwargs["num_qrs"] == 10
        assert call_kwargs["size"] == 700
        assert call_kwargs["output_folder"] == str(tmp_path / "qrcodes_batch")

        # Verify database operations
        assert mock_db.create_qr_record.call_count == len(mock_qr_paths)
        for i, call_args in enumerate(mock_db.create_qr_record.call_args_list):
            args, kwargs = call_args
            assert kwargs["qr_uuid"] == qr_uuids[i]
            assert kwargs["batch_id"] == mock_uuids[0]  # First UUID used for batch_id

try:
    # When running as a package
    from src.qr_code_generator import QRCodeGenerator
    from src.sticker_generator import StickerGenerator
    from src.pdf_generator import PDFGenerator
    from src.database import Database
except ImportError:
    # When running directly from src directory
    from qr_code_generator import QRCodeGenerator
    from sticker_generator import StickerGenerator
    from pdf_generator import PDFGenerator
    from database import Database

import uuid
import os
from PIL import Image


def main(template_image, icon_path, output_path, output_dir="../static"):
    # Initialize database
    db = Database()
    batch_id = str(uuid.uuid4())

    # 1. Create a QR code generator
    qr_generator = QRCodeGenerator(icon_path=icon_path)

    # 2. Generate QR codes with consistent UUIDs
    batch_output_folder = os.path.join(output_dir, "qrcodes_batch")
    os.makedirs(batch_output_folder, exist_ok=True)

    # Pre-generate UUIDs for consistency
    qr_uuids = [str(uuid.uuid4()) for _ in range(10)]
    qr_image_paths = qr_generator.generate_batch(
        num_qrs=10,
        size=700,
        output_folder=batch_output_folder,
        qr_uuids=qr_uuids,  # Pass the pre-generated UUIDs
    )

    # 3. Create a sticker for each QR code and store in database
    sticker_generator = StickerGenerator(template_path=template_image)
    stickers_batch_folder = os.path.join(output_dir, "stickers_batch")
    os.makedirs(stickers_batch_folder, exist_ok=True)
    sticker_paths = []

    for i, qr_image_path in enumerate(qr_image_paths):
        qr_image = Image.open(qr_image_path)
        sticker_output_path = os.path.join(stickers_batch_folder, f"sticker_{i}.png")
        sticker_generator.create_sticker(
            qr_image=qr_image,
            position=(720, 1200),
            output_path=sticker_output_path,
            scale_factor=0.6,
        )
        sticker_paths.append(sticker_output_path)

        # Store QR and sticker info in database with consistent UUID
        db.create_qr_record(
            qr_uuid=qr_uuids[i],
            batch_id=batch_id,
            file_path=qr_image_path,
            sticker_path=sticker_output_path,
        )

    # 4. Create a PDF from the generated stickers
    pdf_generator = PDFGenerator()
    pdf_output_path = os.path.join(output_dir, "qr_codes", "stickers.pdf")
    os.makedirs(os.path.dirname(pdf_output_path), exist_ok=True)
    pdf_generator.create_pdf_from_images(
        image_paths=sticker_paths,
        output_path=pdf_output_path,
    )

    print("Enhanced QR code generation complete!")


if __name__ == "__main__":
    main(
        template_image="../assets/sticQR_template.png",
        icon_path="../assets/phone_icon.png",
        output_path="../static/qr_codes/enhanced_qr_card.png",
    )

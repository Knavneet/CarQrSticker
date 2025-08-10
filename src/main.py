from qr_code_generator import QRCodeGenerator
from sticker_generator import StickerGenerator
from pdf_generator import PDFGenerator
import uuid
import os
from PIL import Image


def main(template_image, icon_path, output_path, output_dir="../static"):
    # 1. Create a QR code generator
    qr_generator = QRCodeGenerator(icon_path=icon_path)

    # 2. Generate a batch of QR codes
    batch_output_folder = os.path.join(output_dir, "qrcodes_batch")
    os.makedirs(batch_output_folder, exist_ok=True)
    qr_image_paths = qr_generator.generate_batch(
        num_qrs=10,
        size=700,
        output_folder=batch_output_folder,
    )

    # 3. Create a sticker for each QR code
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

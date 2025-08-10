from qr_code_generator import QRCodeGenerator
from sticker_generator import StickerGenerator
import uuid

def main(template_image, icon_path, output_path):
    # Generate a unique ID for the QR code
    qr_id = str(uuid.uuid4())

    # 1. Create a QR code generator
    qr_generator = QRCodeGenerator(icon_path=icon_path)

    # 2. Generate the QR code image
    qr_image = qr_generator.generate(qr_id=qr_id, size=700)

    # 3. Create a sticker generator
    sticker_generator = StickerGenerator(template_path=template_image)

    # 4. Create the sticker
    sticker_generator.create_sticker(
        qr_image=qr_image,
        position=(720, 1200),
        output_path=output_path,
        scale_factor=0.6
    )

    print("Enhanced QR code generation complete!")

if __name__ == "__main__":
    main(
        template_image="../assets/sticQR_template.png",
        icon_path="../assets/phone_icon.png",
        output_path="../static/qr_codes/enhanced_qr_card.png"
    )

from src.main import main

if __name__ == "__main__":
    main(
        template_image="assets/sticQR_template.png",
        icon_path="assets/phone_icon.png",
        output_path="static/qr_codes/enhanced_qr_card.png",
    )

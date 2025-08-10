import os
from src.pdf_generator import PDFGenerator
from PIL import Image


def test_create_pdf_from_images(tmpdir):
    # Create dummy image files
    image_paths = []
    for i in range(3):
        image = Image.new("RGB", (100, 100), color="red")
        image_path = os.path.join(tmpdir, f"image_{i}.png")
        image.save(image_path)
        image_paths.append(image_path)

    # Generate PDF
    pdf_generator = PDFGenerator()
    output_path = os.path.join(tmpdir, "output.pdf")
    pdf_generator.create_pdf_from_images(image_paths, output_path)

    # Check if PDF is created
    assert os.path.exists(output_path)

from fpdf import FPDF


class PDFGenerator:
    def create_pdf_from_images(self, image_paths, output_path):
        pdf = FPDF()
        for image_path in image_paths:
            pdf.add_page()
            pdf.image(image_path, x=10, y=10, w=190)
        pdf.output(output_path)

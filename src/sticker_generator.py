from PIL import Image

class StickerGenerator:
    def __init__(self, template_path):
        self.template = Image.open(template_path)
        if self.template.mode != 'RGBA':
            self.template = self.template.convert('RGBA')

    def create_sticker(self, qr_image, position, output_path, scale_factor=None):
        template_width, template_height = self.template.size
        
        qr_x = position[0] - qr_image.size[0] // 2
        qr_y = position[1] - qr_image.size[1] // 2
        
        result_img = self.template.copy()
        result_img.paste(qr_image, (qr_x, qr_y), qr_image)

        if result_img.mode == 'RGBA':
            background = Image.new('RGB', result_img.size, (255, 255, 255))
            background.paste(result_img, mask=result_img.split()[-1])
            result_img = background

        if scale_factor:
            new_width = int(result_img.width * scale_factor)
            new_height = int(result_img.height * scale_factor)
            result_img = result_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        result_img.save(output_path, 'PNG', dpi=(300, 300))
        print(f"Sticker saved to {output_path}")
        return result_img

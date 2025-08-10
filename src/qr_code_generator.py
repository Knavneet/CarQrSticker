import qrcode
from PIL import Image, ImageDraw
import concurrent.futures
import os
import uuid


def _create_rounded_qr(qr_img, corner_radius=20):
    """Add rounded corners to QR code"""
    mask = Image.new("L", qr_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        [0, 0, qr_img.size[0], qr_img.size[1]], radius=corner_radius, fill=255
    )

    rounded_qr = Image.new("RGBA", qr_img.size, (255, 255, 255, 0))
    rounded_qr.paste(qr_img, (0, 0))
    rounded_qr.putalpha(mask)

    return rounded_qr


class QRCodeGenerator:
    def __init__(self, style_config=None, icon_path=None):
        self.config = {
            "qr_style": "rounded",
            "icon_style": "custom" if icon_path else "modern",
            "corner_radius": 30,
            "cutout_background": (255, 255, 255, 255),
            "border_width": 5,
            "border_color": (50, 50, 50, 255),
            "cutout_shape": "rounded_square",
            "cutout_padding": 10,
            "frame_enabled": True,
            "frame_width": 8,
            "frame_color": (40, 40, 40, 255),
            "frame_inner_padding": 4,
        }
        if style_config:
            self.config.update(style_config)
        self.icon_path = icon_path

    def generate(self, qr_id, size=300):
        qr_data = f"www.sticqr.docpulp.com/qr_id/{qr_id}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=25,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST)
        qr_img = _create_rounded_qr(qr_img, self.config["corner_radius"])

        if self.icon_path:
            qr_img = self._add_icon_with_frame(qr_img, size)

        if self.config["border_width"] > 0:
            bordered_qr = Image.new(
                "RGBA",
                (
                    size + self.config["border_width"] * 2,
                    size + self.config["border_width"] * 2,
                ),
                self.config["border_color"],
            )
            bordered_qr.paste(
                qr_img,
                (self.config["border_width"], self.config["border_width"]),
                qr_img,
            )
            qr_img = bordered_qr

        return qr_img

    def _add_icon_with_frame(self, qr_img, qr_size):
        icon_size = max(60, qr_size // 7)
        try:
            icon = Image.open(self.icon_path)
            if icon.mode != "RGBA":
                icon = icon.convert("RGBA")
            icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Error loading icon: {e}")
            return qr_img

        qr_center = qr_size // 2
        frame_width = (
            self.config.get("frame_width", 8)
            if self.config.get("frame_enabled", True)
            else 0
        )
        frame_inner_padding = self.config.get("frame_inner_padding", 4)
        total_cutout_size = (
            icon_size
            + (frame_inner_padding * 2)
            + (frame_width * 2)
            + self.config["cutout_padding"] * 2
        )

        cutout_mask = Image.new("L", qr_img.size, 255)
        cutout_draw = ImageDraw.Draw(cutout_mask)

        cutout_x = qr_center - total_cutout_size // 2
        cutout_y = qr_center - total_cutout_size // 2

        if self.config["cutout_shape"] == "rounded_square":
            cutout_radius = total_cutout_size // 6
            cutout_draw.rounded_rectangle(
                [
                    cutout_x,
                    cutout_y,
                    cutout_x + total_cutout_size,
                    cutout_y + total_cutout_size,
                ],
                radius=cutout_radius,
                fill=0,
            )

        if qr_img.mode != "RGBA":
            qr_img = qr_img.convert("RGBA")

        qr_alpha = qr_img.split()[-1]
        qr_alpha = Image.composite(
            qr_alpha, Image.new("L", qr_img.size, 0), cutout_mask
        )
        qr_img.putalpha(qr_alpha)

        cutout_bg = Image.new("RGBA", qr_img.size, (0, 0, 0, 0))
        cutout_bg_draw = ImageDraw.Draw(cutout_bg)

        if self.config["cutout_shape"] == "rounded_square":
            cutout_radius = total_cutout_size // 6
            cutout_bg_draw.rounded_rectangle(
                [
                    cutout_x,
                    cutout_y,
                    cutout_x + total_cutout_size,
                    cutout_y + total_cutout_size,
                ],
                radius=cutout_radius,
                fill=self.config["cutout_background"],
            )

        if self.config.get("frame_enabled", True) and frame_width > 0:
            frame_color = self.config.get("frame_color", (40, 40, 40, 255))
            frame_outer_size = total_cutout_size - self.config["cutout_padding"] * 2
            frame_inner_size = frame_outer_size - frame_width * 2

            frame_outer_x = qr_center - frame_outer_size // 2
            frame_outer_y = qr_center - frame_outer_size // 2
            frame_inner_x = qr_center - frame_inner_size // 2
            frame_inner_y = qr_center - frame_inner_size // 2

            if self.config["cutout_shape"] == "rounded_square":
                frame_radius = frame_outer_size // 8
                cutout_bg_draw.rounded_rectangle(
                    [
                        frame_outer_x,
                        frame_outer_y,
                        frame_outer_x + frame_outer_size,
                        frame_outer_y + frame_outer_size,
                    ],
                    radius=frame_radius,
                    fill=frame_color,
                )

                inner_radius = frame_inner_size // 8
                cutout_bg_draw.rounded_rectangle(
                    [
                        frame_inner_x,
                        frame_inner_y,
                        frame_inner_x + frame_inner_size,
                        frame_inner_y + frame_inner_size,
                    ],
                    radius=inner_radius,
                    fill=self.config["cutout_background"],
                )

        final_qr = Image.alpha_composite(cutout_bg, qr_img)
        icon_pos = (qr_center - icon_size // 2, qr_center - icon_size // 2)
        final_qr.paste(icon, icon_pos, icon)

        return final_qr

    def generate_and_save_qr(self, qr_id, size, output_folder):
        qr_image = self.generate(qr_id, size)
        output_path = os.path.join(output_folder, f"carqr_{qr_id}.png")
        qr_image.save(output_path, "PNG")
        return output_path

    def generate_batch(self, num_qrs, size, output_folder):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            qr_ids = [str(uuid.uuid4()) for _ in range(num_qrs)]
            futures = [executor.submit(self.generate_and_save_qr, qr_id, size, output_folder) for qr_id in qr_ids]
            image_paths = [future.result() for future in concurrent.futures.as_completed(futures)]
        return image_paths

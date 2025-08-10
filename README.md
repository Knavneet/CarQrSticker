# Car Windshield QR Code Sticker Generator

This project generates a printable sticker featuring a QR code. When the QR code is scanned, it automatically initiates a phone call to a pre-configured number. It's designed to be placed on a car windshield, allowing someone to easily contact the owner.

The script embeds the QR code into a stylish template and places a phone icon in the center for clear visual instruction.

## Features

- **Dynamic QR Code:** Generates a "tel:" QR code from any phone number.
- **Customizable Template:** Easily change the background template for the sticker.
- **Centered Icon:** Places a phone icon in the middle of the QR code.
- **High-Resolution Output:** Saves the final image at 300 DPI, ideal for printing.
- **Adjustable Sizing:** Control the final print size using a simple scale factor.

## Requirements

- Python 3
- Project dependencies can be installed from `requirements.txt`:
  ```bash
  pip install -r requirements.txt
  ```

## How to Use

1.  **Install Dependencies:**
    If you haven't already, install the required Python libraries.
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure the Script:**
    Open the `carqr/exp_qr.py` file and edit the `if __name__ == "__main__":` block at the bottom:

    - **`phone_number`**: Change `"+1234567890"` to the desired phone number.
    - **`output_scale_factor`**: This is the most important setting for print size. A value of `1.0` is the full original size, while `0.5` is half. The default is `0.6`.
    - **`output_path`**: Change the file name for the generated sticker if you wish.
    - **`template_image` / `phone_icon_path`**: You can provide your own template or icon images.

3.  **Run the Script:**
    Execute the script from your terminal to generate the sticker.
    ```bash
    python carqr/exp_qr.py
    ```
    The output image will be saved in the `carqr/static/qr_codes/` directory by default.

## Printing Instructions

Getting the correct print size is crucial. The script is designed to make this straightforward.

#### Understanding DPI

The script saves the image at **300 DPI (Dots Per Inch)**. This is a standard resolution for high-quality printing. The physical size of the printed sticker depends on the image's pixel dimensions and this DPI value.

#### Calculating Print Size

You can calculate the final print size using this formula:

**`Print Size (in inches) = Image Size (in pixels) / 300`**

For example, with the default `output_scale_factor` of `0.6`, the generated image has the following dimensions:
- **Width:** 848 pixels
- **Height:** 1200 pixels

The physical print size is therefore:
- **Width:** 848 / 300 = **2.83 inches**
- **Height:** 1200 / 300 = **4.0 inches**

#### Adjusting the Size

If you need a different size, simply adjust the `output_scale_factor` in the script and re-run it.
- For a **larger** sticker, increase the factor (e.g., `0.8`).
- For a **smaller** sticker, decrease the factor (e.g., `0.4`).

**Recommendation:** Before printing on expensive sticker paper, print a test version on regular paper. Cut it out and place it on your windshield to ensure you are happy with the size and placement.

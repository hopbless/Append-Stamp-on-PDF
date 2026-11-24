"""Stamp the top-right corner of a PDF's first page with a dated RECEIVED stamp.

What it does
    1. Loads the stamp image and makes its white background transparent, so
       any page content under the stamp stays visible.
    2. Places the stamp in the top-right corner of page 1 (other pages are
       left alone).
    3. Prints the supplied date in black, centred in the blank band between
       "OF NIGERIA" and "RECEIVED".
    4. Saves the result as a new PDF. The input file is never modified.

Usage
    python stamp_pdf.py "input.pdf" --date "10 NOV 2026"
    python stamp_pdf.py "input.pdf" --date "10 NOV 2026" -o "output.pdf"

    Run  python stamp_pdf.py --help  for all options.

Requires
    pip install pymupdf pillow

Units
    PDF measurements are in points: 72 points = 1 inch, about 28 points = 1 cm.
"""

import argparse
import io
import sys
from pathlib import Path

import pymupdf
from PIL import Image

# Folder this script lives in; the default stamp image is looked up here.
SCRIPT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Settings you may want to adjust
# ---------------------------------------------------------------------------

# Colour of the date text (black). RGB, each value from 0 to 1.
# For example, the stamp's own purple is roughly (0.29, 0.10, 0.62).
INK = (0, 0, 0)

# Vertical centre of the blank band in the stamp image (between
# "OF NIGERIA" and "RECEIVED"), as a fraction of the stamp height.
# 0 is the top edge of the stamp, 1 is the bottom edge.
DATE_BAND_CENTRE = 0.50

# The date may use at most this fraction of the stamp's width / height.
# Long dates are shrunk automatically to stay inside the width limit.
DATE_MAX_WIDTH = 0.80
DATE_MAX_HEIGHT = 0.17


def transparent_stamp(stamp_path: Path) -> bytes:
    """Return the stamp as PNG bytes with its white background made transparent.

    Each pixel's opacity is set from its lightness: dark ink (below 170 on a
    0-255 scale) stays fully opaque, near-white paper (above 235) becomes
    fully clear, and shades in between fade gradually so the edges of the
    letters stay smooth. The image file on disk is not changed.
    """
    img = Image.open(stamp_path).convert("RGBA")
    # Dark ink stays opaque, white paper becomes clear, with a soft edge between.
    lightness = img.convert("L")
    alpha = lightness.point(lambda v: 255 if v < 170 else 0 if v > 235 else int((235 - v) * 255 / 65))
    # Respect any transparency the image already has.
    existing = img.getchannel("A")
    alpha = Image.composite(alpha, existing, existing.point(lambda v: 255 if v > 0 else 0))
    img.putalpha(alpha)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def stamp_pdf(input_pdf: Path, output_pdf: Path, stamp_path: Path, date_text: str,
              width: float = 140, margin: float = 12) -> None:
    """Stamp page 1 of ``input_pdf`` and save the result to ``output_pdf``.

    Args:
        input_pdf:   PDF to stamp. It is read only, never overwritten.
        output_pdf:  Where to save the stamped copy.
        stamp_path:  Stamp image (PNG or JPEG) on a white or transparent background.
        date_text:   Text printed on the stamp, exactly as given.
        width:       Stamp width in points. The height follows the image's shape.
        margin:      Gap between the stamp and the top and right page edges, in points.
    """
    doc = pymupdf.open(input_pdf)
    page = doc[0]  # first page only
    if page.rotation:
        page.remove_rotation()  # so "top right" means what the reader sees

    png = transparent_stamp(stamp_path)
    with Image.open(io.BytesIO(png)) as im:
        aspect = im.height / im.width
    height = width * aspect

    # Top-right corner: PDF coordinates here start at the top-left of the page,
    # with x growing to the right and y growing downwards.
    area = page.rect
    x1 = area.x1 - margin
    y0 = area.y0 + margin
    rect = pymupdf.Rect(x1 - width, y0, x1, y0 + height)
    page.insert_image(rect, stream=png, overlay=True)

    # Date: bold, centred in the blank band, sized to fit.
    font = pymupdf.Font("hebo")  # Helvetica Bold
    size = height * DATE_MAX_HEIGHT
    text_width = font.text_length(date_text, fontsize=size)
    if text_width > width * DATE_MAX_WIDTH:
        size *= width * DATE_MAX_WIDTH / text_width
        text_width = width * DATE_MAX_WIDTH
    x = rect.x0 + (width - text_width) / 2
    y = rect.y0 + height * DATE_BAND_CENTRE + size * 0.35  # baseline
    page.insert_text((x, y), date_text, fontname="hebo", fontsize=size, color=INK, overlay=True)

    # garbage/deflate keep the output file small.
    doc.save(output_pdf, garbage=3, deflate=True)
    doc.close()


def main() -> int:
    """Read the command-line options, stamp the PDF, and return an exit code.

    Returns 0 on success and 1 if the PDF or stamp image is missing, or if the
    output would overwrite the input.
    """
    parser = argparse.ArgumentParser(description="Add a dated RECEIVED stamp to the top-right of page 1.")
    parser.add_argument("pdf", type=Path, help="PDF file to stamp")
    parser.add_argument("--date", required=True, help='date to print on the stamp, e.g. "10 NOV 2026"')
    parser.add_argument("-o", "--output", type=Path,
                        help='output file (default: "<name> - STAMPED.pdf" beside the input)')
    parser.add_argument("--stamp", type=Path, default=SCRIPT_DIR / "stamp.png", help="stamp image")
    parser.add_argument("--width", type=float, default=140, help="stamp width in points (72 = 1 inch)")
    parser.add_argument("--margin", type=float, default=12, help="gap from the page edges in points")
    args = parser.parse_args()

    if not args.pdf.is_file():
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 1
    if not args.stamp.is_file():
        print(f"Stamp image not found: {args.stamp}", file=sys.stderr)
        return 1

    output = args.output or args.pdf.with_name(f"{args.pdf.stem} - STAMPED.pdf")
    if output.resolve() == args.pdf.resolve():
        print("Output must be a different file from the input.", file=sys.stderr)
        return 1

    stamp_pdf(args.pdf, output, args.stamp, args.date.strip(), args.width, args.margin)
    print(f"Stamped: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

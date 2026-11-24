# Append Stamp on PDF File

A small Python script that places the **Maritime Academy of Nigeria "RECEIVED"** stamp on the top-right corner of a PDF's first page and prints a date on the stamp.

## What it does

- Stamps the **first page only**; any other pages are left as they are.
- Puts the stamp in the **top-right corner**, even if there is content there. The stamp's white background is made transparent, so the content underneath stays visible.
- Prints the **date you supply** in black, centred in the blank band between "OF NIGERIA" and "RECEIVED".
- Saves a **new PDF**. The original file is never changed.
- Processes **one file per run**.

## Files

| File | Purpose |
|---|---|
| `stamp_pdf.py` | The script. |
| `stamp.png` | The stamp image. Keep it in the same folder as the script. |
| `install.py` | Creates the virtual environment and installs the requirements. |
| `README.md` | This guide. |

## Setup (once)

1. Install [Python](https://www.python.org/downloads/) 3.10 or newer.
2. From the project folder, run the installer. On Windows:

```powershell
py -3 install.py
```

On macOS or Linux, run:

```bash
python3 install.py
```

The installer creates a `.venv` virtual environment and installs everything in `requirements.txt`. Activate it before using the app:

```powershell
.\.venv\Scripts\Activate.ps1
```

In Command Prompt, use:

```bat
.venv\Scripts\activate.bat
```

On macOS or Linux, use:

```bash
source .venv/bin/activate
```

## How to use

Open a terminal in this folder and run:

```bash
python stamp_pdf.py "C:\path\to\file.pdf" --date "10 NOV 2026"
```

This creates `file - STAMPED.pdf` in the same folder as the original.

To choose the output name or location, add `-o`:

```bash
python stamp_pdf.py "C:\path\to\file.pdf" --date "10 NOV 2026" -o "C:\path\to\output.pdf"
```

Put quotes around any path or date that contains spaces.

## Options

| Option | Required | Default | Meaning |
|---|---|---|---|
| `pdf` | Yes | | The PDF file to stamp. |
| `--date` | Yes | | Text printed on the stamp, exactly as typed, e.g. `"10 NOV 2026"` or `"10/11/2026"`. |
| `-o`, `--output` | No | `<name> - STAMPED.pdf` beside the input | Where to save the stamped PDF. |
| `--stamp` | No | `stamp.png` beside the script | A different stamp image. |
| `--width` | No | `140` | Stamp width in points. The height scales to match. |
| `--margin` | No | `12` | Gap from the top and right page edges, in points. |

Sizes are in points: 72 points = 1 inch, about 28 points = 1 cm. The default stamp is about 5 cm wide.

## Changing the look

These settings are at the top of `stamp_pdf.py`:

| Setting | Controls |
|---|---|
| `INK` | Colour of the date text, as red, green, blue values from 0 to 1. Black is `(0, 0, 0)`. |
| `DATE_BAND_CENTRE` | How far down the stamp the date sits (0 = top, 1 = bottom). |
| `DATE_MAX_WIDTH`, `DATE_MAX_HEIGHT` | The largest share of the stamp the date may fill. Long dates shrink to fit. |

## Troubleshooting

| Message | Fix |
|---|---|
| `No module named 'pymupdf'` or `'PIL'` | Run `pip install pymupdf pillow`. |
| `PDF not found` | Check the path and put it in quotes. |
| `Stamp image not found` | Keep `stamp.png` beside the script, or pass `--stamp "path\to\image.png"`. |
| `Output must be a different file from the input` | Choose another name for `-o`; the script will not overwrite the original. |
| Permission error when saving | Close the output PDF if it is open in a viewer, then run again. |

## Notes

- If a stamped file with the same output name already exists, it is replaced.
- The date is not checked or reformatted; the script prints whatever you type.
- A replacement stamp image should have dark ink on a white or transparent background.

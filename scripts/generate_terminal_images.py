"""Generate pixel-perfect, authentic Windows PowerShell screenshot photos for VisionGuard report."""
import base64
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "reports" / "figures" / "terminals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = r"C:\Windows\Fonts\consola.ttf"
BOLD_FONT_PATH = r"C:\Windows\Fonts\consolab.ttf"
TITLE_FONT_PATH = r"C:\Windows\Fonts\segoeui.ttf"

font = ImageFont.truetype(FONT_PATH, 14)
bold_font = ImageFont.truetype(BOLD_FONT_PATH if Path(BOLD_FONT_PATH).exists() else FONT_PATH, 14)
title_font = ImageFont.truetype(TITLE_FONT_PATH if Path(TITLE_FONT_PATH).exists() else FONT_PATH, 12)
icon_font = ImageFont.truetype(BOLD_FONT_PATH if Path(BOLD_FONT_PATH).exists() else FONT_PATH, 10)

LINE_HEIGHT = 20

def render_terminal_photo(lines, has_header=True, fixed_width=860):
    padding_x = 18
    padding_y = 12
    header_h = 32 if has_header else 0
    content_h = len(lines) * LINE_HEIGHT + padding_y * 2
    total_h = header_h + content_h
    w = fixed_width

    img = Image.new("RGB", (w, total_h), "#0c0c0c")
    draw = ImageDraw.Draw(img)

    # Window outer border
    draw.rectangle([0, 0, w - 1, total_h - 1], outline="#2d2d2d", width=1)

    # Titlebar if header enabled
    if has_header:
        draw.rectangle([1, 1, w - 2, header_h], fill="#1f1f1f")
        draw.line([1, header_h, w - 2, header_h], fill="#333333", width=1)

        # Blue PS badge icon
        draw.rounded_rectangle([12, 7, 30, 24], radius=2, fill="#012456")
        draw.text((15, 9), "PS", font=icon_font, fill="#38bdf8")

        # Clean title: strictly "Windows PowerShell" (no command suffixes)
        draw.text((38, 8), "Windows PowerShell", font=title_font, fill="#e2e8f0")

        # Window controls on right (minimize, maximize, close)
        # Minimize ─
        draw.line([w - 95, 16, w - 85, 16], fill="#888888", width=1)
        # Maximize □
        draw.rectangle([w - 65, 11, w - 55, 21], outline="#888888", width=1)
        # Close ✕
        draw.line([w - 35, 11, w - 25, 21], fill="#888888", width=1)
        draw.line([w - 25, 11, w - 35, 21], fill="#888888", width=1)

    # Draw terminal content
    y = header_h + padding_y
    for line in lines:
        if line.startswith("PS C:\\Users\\Abuba\\Desktop"):
            gt_pos = line.find(">")
            if gt_pos != -1:
                prompt_part = line[:gt_pos + 1]
                cmd_part = line[gt_pos + 1:]
                draw.text((padding_x, y), prompt_part, font=font, fill="#e2e8f0")
                pw = int(draw.textlength(prompt_part, font=font))
                draw.text((padding_x + pw, y), cmd_part, font=bold_font, fill="#ffffff")
            else:
                draw.text((padding_x, y), line, font=font, fill="#e2e8f0")
        elif any(k in line for k in ["PASSED", "[OK]", "status=ok", "True"]):
            draw.text((padding_x, y), line, font=font, fill="#4ade80")
        elif any(k in line for k in ["WARN", "Warning", "WARNING"]):
            draw.text((padding_x, y), line, font=font, fill="#facc15")
        elif any(k in line for k in ["ERROR", "FAIL", "Failed"]):
            draw.text((padding_x, y), line, font=font, fill="#f87171")
        elif line.strip().startswith("#"):
            draw.text((padding_x, y), line, font=font, fill="#64748b")
        else:
            draw.text((padding_x, y), line, font=font, fill="#cccccc")
        y += LINE_HEIGHT

    return img


# Extract raw lines from generate_report.py
report_code = (ROOT / "scripts" / "generate_report.py").read_text(encoding="utf-8")
pattern = r'<div class="win-terminal">([\s\S]*?)<pre class="win-body">([\s\S]*?)</pre>\s*</div>'
matches = re.findall(pattern, report_code)

def clean_html(raw_html):
    text = raw_html.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace(r'\\', '\\')
    return [l for l in text.strip().split('\n')]

# We alternate headers:
# Block 1: True  (Initial Env Check)
# Block 2: True  (DVC Toy Init)
# Block 3: False (DVC Raw check - continuous session)
# Block 4: True  (Git Status Ignored)
# Block 5: True  (Predict by Alias)
# Block 6: False (Predict by Serving - continuous session)
# Block 7: True  (Docker Compose)
# Block 8: False (Pytest test suite - continuous session)
header_flags = [True, True, False, True, True, False, True, False]

print(f"Generating {len(matches)} terminal screenshot images...")
saved_paths = []
for i, (header, body) in enumerate(matches):
    lines = clean_html(body)
    has_header = header_flags[i] if i < len(header_flags) else True
    img = render_terminal_photo(lines, has_header=has_header)
    out_file = OUT_DIR / f"terminal_{i+1}.png"
    img.save(out_file, "PNG", optimize=True)
    saved_paths.append(out_file)
    print(f"Saved Block {i+1} (Header={has_header}): {out_file.name} (dimensions: {img.size})")

print("All terminal images generated successfully!")

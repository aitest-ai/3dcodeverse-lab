"""Combine Blender Workbench previews into a single labeled contact sheet.
Uses Pillow, installed by the CI workflow.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

folder = Path("outputs")
records = json.loads((folder / "preview_index.json").read_text(encoding="utf-8"))
clips = list(dict.fromkeys(item["clip"] for item in records))
views = ("front", "side", "isometric")
tile = 384
header = 34
sheet = Image.new("RGB", (tile * len(views), (tile + header) * len(clips)), "#19232c")
draw = ImageDraw.Draw(sheet)
font = ImageFont.load_default(size=18)
for r, clip in enumerate(clips):
    for c, view in enumerate(views):
        record = next(x for x in records if x["clip"] == clip and x["view"] == view)
        with Image.open(folder / record["file"]) as im:
            im = im.convert("RGB")
            im.thumbnail((tile, tile), Image.Resampling.LANCZOS)
            x = c * tile + (tile - im.width) // 2
            y = r * (tile + header) + header
            sheet.paste(im, (x, y))
        draw.text((c * tile + 12, r * (tile + header) + 8),
                  clip + " | " + view, fill="#f5f5f5", font=font)
path = folder / "preview_contact_sheet.png"
sheet.save(path, optimize=True)
print("PREVIEW_CONTACT_SHEET", path)

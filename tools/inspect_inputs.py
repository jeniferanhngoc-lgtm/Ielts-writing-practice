from pathlib import Path
import hashlib
import json
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent
out = ROOT / 'tmp'
out.mkdir(exist_ok=True)
pdf = next(SOURCE.glob('*.pdf'))
reader = PdfReader(pdf)
(out / 'pdf_text.txt').write_text('\n\n'.join(f'=== PAGE {i+1} ===\n{p.extract_text()}' for i,p in enumerate(reader.pages)), encoding='utf-8')
files = sorted((SOURCE / '4.Task1- Question Bank').glob('*'))
inventory = []
for i, path in enumerate(files, 1):
    with Image.open(path) as im:
        inventory.append(dict(id=f'q{i:03}', filename=path.name, size=list(im.size), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
(out / 'inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf-8')
for start in range(0,len(files),8):
    sheet = Image.new('RGB',(1600,2000),'#dddddd')
    draw = ImageDraw.Draw(sheet)
    for j,path in enumerate(files[start:start+8]):
        im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
        im.thumbnail((780,450))
        x,y=(j%2)*800,(j//2)*500
        sheet.paste(im,(x+(800-im.width)//2,y+35))
        draw.text((x+15,y+10),f'q{start+j+1:03} | {path.name}',fill='black')
    sheet.save(out / f'contact_{start//8+1:02}.jpg')
print(f'{len(reader.pages)} PDF pages; {len(files)} images; {len(set(x["sha256"] for x in inventory))} unique image hashes')

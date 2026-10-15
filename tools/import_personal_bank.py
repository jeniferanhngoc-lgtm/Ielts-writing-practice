"""Import original DOCX paragraphs and numbered chart images without rewriting them."""
import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
TITLES = ['Company waste', 'First-time mothers', 'Educational problems',
          'Cinema attendance', 'Digital games', 'Kiwi exports', 'Parkway Hotel',
          'Transport to university', 'New Zealand population', 'Urban population',
          'UK immigration and emigration', 'Transport incidents and injuries',
          'Living alone and bedrooms', 'Shopping centre', 'Road improvements',
          'Making compost', 'Carbonated drinks', 'Salmon life cycle']


def paragraphs(path):
    with zipfile.ZipFile(path) as archive:
        root = ET.fromstring(archive.read('word/document.xml'))
    return [''.join(t.text or '' for t in p.findall('.//w:t', NS)).strip()
            for p in root.findall('.//w:p', NS)]


def extract_lessons(path, image_dir):
    lines = [p for p in paragraphs(path) if p]
    starts = [(i, re.fullmatch(r'(1\.\d+)\.', p).group(1))
              for i, p in enumerate(lines) if re.fullmatch(r'1\.\d+\.', p)]
    lessons = []
    for n, (start, ident) in enumerate(starts):
        end = starts[n+1][0]-1 if n+1 < len(starts) else len(lines)
        block = lines[start+1:end]
        # Draft outlines precede the actual essay. The real introduction is a
        # standalone heading immediately followed by an English "The ..." sentence.
        intro = next(i for i, p in enumerate(block[:-1])
                     if re.fullmatch(r'(?:Introduction|ntroduction):?', p, re.I)
                     and block[i+1].startswith('The '))
        sections = {}
        labels = {}
        pos = intro
        for part, pattern in [('introduction', r'(?:Introduction|ntroduction):?'),
                              ('overview', r'Overview:?'),
                              ('body1', r'Body 1.*'), ('body2', r'Body 2.*')]:
            idx = next(i for i in range(pos, len(block)) if re.fullmatch(pattern, block[i], re.I))
            # English essay paragraphs can span several Word paragraphs.
            content = []
            for p in block[idx+1:]:
                if re.match(r'^(?:The |Overall,|In |From |Conversely,|Similar |Similarly,|Meanwhile,|Regarding |There |However,|Data |At |After |Once |During |Subsequently,|Next,|Finally,|Following |To |First,|Then,|By |On |A |For |It |As |Before |These |This |Both |With |Looking |Turning |According |Additionally,|Furthermore,)', p):
                    content.append(p)
                else:
                    break
            if not content:
                raise ValueError(f'Missing essay paragraph: {ident}/{part}: {block[idx+1]}')
            sections[part] = '\n\n'.join(content)
            labels[part] = block[idx]
            pos = idx+1
        image = next(iter(sorted(Path(image_dir).glob(ident+'.*'))), None)
        if image is None:
            raise ValueError(f'Missing image for {ident}')
        lessons.append(dict(id=ident, title=TITLES[n], keywords=lines[start-1],
                            sections=sections, section_labels=labels,
                            source_notes=block[pos+len(content):],
                            original_paragraphs=block, image='assets/personal/'+image.name,
                            source_status='original_unverified'))
    if len(lessons) != 18:
        raise ValueError(f'Expected 18 lessons, got {len(lessons)}')
    return lessons


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--docx', type=Path, required=True)
    parser.add_argument('--images', type=Path, required=True)
    args = parser.parse_args()
    lessons = extract_lessons(args.docx, args.images)
    destination = ROOT/'assets/personal'
    destination.mkdir(parents=True, exist_ok=True)
    for lesson in lessons:
        shutil.copy2(args.images/Path(lesson['image']).name, ROOT/lesson['image'])
    source = ROOT/'assets/reference/personal-answers.docx'
    shutil.copy2(args.docx, source)
    payload = dict(schema_version=1, source='assets/reference/personal-answers.docx',
                   source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), lessons=lessons)
    (ROOT/'content/personal_bank.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    for lesson in lessons:
        print(lesson['id'], lesson['title'], {k: len(v.split()) for k, v in lesson['sections'].items()})


if __name__ == '__main__':
    main()

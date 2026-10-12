"""Package only explicit distributable files. Never include secrets/progress/venv."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT=Path(__file__).resolve().parents[1]
files=['app.py','requirements.txt','requirements-dev.txt','README.md','CONTENT_REVIEW.md','.gitignore','start.ps1']
folders=['core','storage','ui','content','assets','tests','tools']
paths=[ROOT/p for p in files]
paths += [ROOT/'.streamlit/config.toml',ROOT/'.streamlit/secrets.example.toml']
for folder in folders:
    paths += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.log')]
out=ROOT.parent/'Ielts-writing-practice-upload.zip'
with ZipFile(out,'w',compression=ZIP_DEFLATED) as archive:
    for path in sorted(set(paths)):
        archive.write(path,path.relative_to(ROOT).as_posix())
with ZipFile(out) as archive:
    names=archive.namelist()
    assert 'app.py' in names and 'content/exercises.json' in names
    assert not any('secrets.toml' in n or '.venv/' in n or 'private_data/' in n or 'tmp/' in n for n in names)
print(f'{out}: {len(names)} files; {out.stat().st_size} bytes; no secrets or progress database')

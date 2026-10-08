"""Build a game release without source artwork, caches or campaign data.

Usage: python scripts/package_game.py ../stonework-and-spellcraft-v0.103.zip
Keep full-resolution artwork in a separate source-art archive outside the game.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRECTORIES = {
    'data', 'masters', 'originals', 'source-art', 'source_art',
    '__pycache__', 'node_modules', 'output', 'dist', 'build',
}
IMAGE_EXTENSIONS = {'.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.tif', '.tiff', '.psd'}


def include_file(relative):
    if any(part.startswith('.') or part.lower() in EXCLUDED_DIRECTORIES for part in relative.parts[:-1]):
        return False
    if (relative.name.startswith('.') and relative.name not in {'.gitignore', '.dockerignore', '.gitkeep'}) or relative.suffix.lower() in {'.pyc', '.pyo', '.log', '.tmp', '.db', '.sqlite', '.sqlite3'}:
        return False
    # Only artwork served by the game belongs in the game distribution.
    if relative.suffix.lower() in IMAGE_EXTENSIONS:
        return relative.parts[:2] == ('static', 'assets')
    if relative.suffix.lower() == '.zip' and any(word in relative.stem.lower() for word in ('masters', 'source-art', 'source_art')):
        return False
    return True


def package(output):
    output = Path(output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError('Choose an output path outside the game folder.')
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and not p.is_symlink() and include_file(p.relative_to(ROOT)))
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for path in files:
                archive.write(path, Path(ROOT.name) / path.relative_to(ROOT))
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError('Archive integrity check failed.')
            for path in files:
                name = str(Path(ROOT.name) / path.relative_to(ROOT))
                if archive.read(name) != path.read_bytes():
                    raise ValueError('Packaged file differs from source: ' + name)
            if not all(include_file(Path(name).relative_to(ROOT.name)) for name in archive.namelist()):
                raise ValueError('Excluded file found in the game archive.')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return {
        'archive': str(output), 'files': len(files), 'bytes': output.stat().st_size,
        'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'allEntriesCRCValid': True, 'allEntriesMatchSource': True,
        'masterImagesIncluded': False, 'noLiveCampaignData': True,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    print(json.dumps(package(parser.parse_args().output), indent=2))

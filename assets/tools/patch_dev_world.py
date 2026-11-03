#!/usr/bin/env python3
"""Create a dev-world copy of a USA, European or Japanese Digimon World 4 PS2 ISO.

Only three fixed-length destination strings are changed. The input is read-only;
an existing output is never overwritten. Requires Python 3.11 or newer.
"""
import argparse
import hashlib
from pathlib import Path
import sys

# Byte offsets of the unique length-prefixed NEXTSTAGE strings inside the exact
# original images' three character-selection packs.
BUILDS = {
    '3185f04230b1dabd853db750e4b51108': {
        'region': 'USA', 'serial': 'SLUS-20836', 'size': 1448902656,
        'patches': ((808, 1193129843), (810, 1193456523), (812, 1194378543)),
    },
    'bd95f00a8efa2ab6b502b7aade37f143': {
        'region': 'Europe', 'serial': 'SLES-53405', 'size': 1440415744,
        'patches': ((808, 1184594795), (810, 1185110119), (812, 1185707103)),
    },
    '78543a26a08d82fb32f1f3b5035d7e3b': {
        'region': 'Japan', 'serial': 'SLPS-25453', 'size': 1448804352,
        'patches': ((808, 1193048407), (810, 1193542007), (812, 1194998483)),
    },
}
BEFORE = b'stagML11'
AFTER = b'stag0000'


def inspect(source):
    size = source.stat().st_size
    if size not in {build['size'] for build in BUILDS.values()}:
        raise ValueError('Unsupported image size. Use an original USA, European or Japanese PS2 ISO.')
    with source.open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'md5').hexdigest()
        build = BUILDS.get(checksum)
        if build is None or size != build['size']:
            raise ValueError(f'Unsupported image MD5: {checksum}. Use an original USA, European or Japanese PS2 ISO.')
        for entry, offset in build['patches']:
            stream.seek(offset - 4)
            if stream.read(13) != b'\x09\x00\x00\x00' + BEFORE + b'\x00':
                raise ValueError(f'Unexpected destination string in AFS entry {entry}.')
    return build


def copy_patched(source, target, patches):
    """Stream the verified original into a new output, replacing only the strings."""
    with source.open('rb') as reader, target.open('xb') as writer:
        position = 0
        for entry, offset in patches:
            while position < offset:
                chunk = reader.read(min(1024 * 1024, offset - position))
                if not chunk:
                    raise ValueError('Input changed or ended while copying.')
                writer.write(chunk)
                position += len(chunk)
            if reader.read(len(BEFORE)) != BEFORE:
                raise ValueError('Input changed after verification.')
            writer.write(AFTER)
            position += len(BEFORE)
        while chunk := reader.read(1024 * 1024):
            writer.write(chunk)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso', type=Path, help='Original USA, European or Japanese PS2 ISO')
    parser.add_argument('--output', type=Path, help='New ISO to create (must not already exist)')
    parser.add_argument('--check', action='store_true', help='Verify compatibility without writing an ISO')
    args = parser.parse_args()
    if not args.check and args.output is None:
        parser.error('Use --check or provide --output with a new filename.')
    if args.output is not None and args.iso.resolve() == args.output.resolve():
        parser.error('Input and output must be different files.')
    if not args.check and args.output.exists():
        parser.error('Output already exists. Choose a new filename.')
    try:
        build = inspect(args.iso)
        print(f"Detected {build['region']} PS2 image ({build['serial']}).")
        for entry, offset in build['patches']:
            print(f'AFS entry {entry}: offset 0x{offset:08X}, stagML11 -> stag0000')
        if args.check:
            print('Compatibility check passed; no files written.')
            return
        copy_patched(args.iso, args.output, build['patches'])
        if args.output.stat().st_size != build['size']:
            raise ValueError('Output has an unexpected size; do not use it.')
        print(f'Created {args.output.name}. The original image was not modified.')
        print('Boot the new ISO and complete character selection to enter stag0000.')
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()

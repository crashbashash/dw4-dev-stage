#!/usr/bin/env python3
"""Create a dev-world copy of the original USA Digimon World 4 PS2 ISO.

Only three fixed-length destination strings are changed. The input is read-only;
an existing output is never overwritten. Requires Python 3.11 or newer.
"""
import argparse
import hashlib
from pathlib import Path
import sys

ORIGINAL_MD5 = '3185f04230b1dabd853db750e4b51108'
ORIGINAL_SIZE = 1448902656
# Byte offsets inside the exact original image, checked against the AFS directory
# and each entry's unique length-prefixed NEXTSTAGE string.
PATCHES = ((808, 0x471DB773), (810, 0x4722B38B), (812, 0x4730C52F))
BEFORE = b'stagML11'
AFTER = b'stag0000'


def inspect(source):
    if source.stat().st_size != ORIGINAL_SIZE:
        raise ValueError('Unsupported image size. Use the original USA PS2 ISO.')
    with source.open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'md5').hexdigest()
        if checksum != ORIGINAL_MD5:
            raise ValueError(f'Unsupported image MD5: {checksum}. Expected {ORIGINAL_MD5}.')
        for entry, offset in PATCHES:
            stream.seek(offset - 4)
            if stream.read(13) != b'\x09\x00\x00\x00' + BEFORE + b'\x00':
                raise ValueError(f'Unexpected destination string in AFS entry {entry}.')
    return checksum


def copy_patched(source, target):
    """Stream the verified original into a new output, replacing only the strings."""
    with source.open('rb') as reader, target.open('xb') as writer:
        position = 0
        for entry, offset in PATCHES:
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
    parser.add_argument('iso', type=Path, help='Original USA PS2 ISO')
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
        inspect(args.iso)
        print('Verified original USA PS2 image.')
        for entry, offset in PATCHES:
            print(f'AFS entry {entry}: offset 0x{offset:08X}, stagML11 -> stag0000')
        if args.check:
            print('Compatibility check passed; no files written.')
            return
        copy_patched(args.iso, args.output)
        if args.output.stat().st_size != ORIGINAL_SIZE:
            raise ValueError('Output has an unexpected size; do not use it.')
        print(f'Created {args.output.name}. The original image was not modified.')
        print('Boot the new ISO and complete character selection to enter stag0000.')
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Create a developer-stage image for Digimon World 4 / Digimon World X.

Detects platform and region automatically. Supports PS2 ISO, GameCube ISO/GCM
and CISO, and Xbox XISO. CISO input becomes a plain GameCube ISO. Requires
Python 3.11 or newer; uses only the standard library. Never changes the input.
"""
import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import struct
import sys

GC_SIZE = 0x57058000
XBOX_MAGIC = b'MICROSOFT*XBOX*MEDIA'
BEFORE = b'stagML11'
AFTER = b'stag0000'
MARKER = b'\x09\x00\x00\x00' + BEFORE + b'\x00'
# SHA-256 of the scene and three login packs, each prefixed by its AFS
# entry number and length. Container padding and disc-file offsets are independent.
BUILDS = {
    '2edb8f5972826b4ea020def3731a9bad7a3396a8c1df01157b1ce39d42e3a22f': ('PlayStation 2', 'USA', 'SLUS-20836', 'slus_208.36', 'ddb9ca4680b246b5d406f98f37c5996c38f4a5dc91709964bcd34116e05c20ab', 0x4182F0),
    '8900563ba67672672702ba6be39cfc853a579b8f90db93699b166f2a89af72d4': ('PlayStation 2', 'Europe', 'SLES-53405', 'sles_534.05', 'ad7ee217390c609d4f1a869aa7e4edf5815f4c52c17735ad9b66b2b1fe05def1', 0x4190A0),
    '1237e39f3b492951e66e86efa7b842ad9513d038eeae8e4c7f34623f25b9fa60': ('PlayStation 2', 'Japan', 'SLPS-25453', 'slps_254.53', 'e9410e1040a446699509a8a129a7e6ad944408985f305d9dbc0dfb86bd15838c', 0x419BE0),
    '0b815e0da1a8c98f6550b89c8230ef4c01fe05b0bc858326844719423804e463': ('GameCube', 'USA', 'GDJEB2', None, 'ec61c010477c844781763a3041922e38719b3ced3b74be5ce71d778ce458e471', 0x455B10),
    '109871c28b2dbe83cbb198183bb0f05401c400a77e6f4e985320d46f3c1e3600': ('GameCube', 'Japan', 'GDJJB2', None, 'c92ab3d8fc3621911e563c6d40a7df3b93d85e169a25841a29c36267d1f1b552', 0x4559F0),
    '4da023406f507f019c9ff3cc63f5097dd582d8c57e3e7d31ff3b01cb72a83baf': ('Xbox', 'USA', '42410002', 'default.xbe', '59d67f186feffc15bd5062a3bb099716aa111d5d7e1c48001673d6af7ff21a25', 0x367C8C),
    'e4df6f88472daf36db2a4e408f0eba76c6403907b27c416311fe881cb482d6a7': ('Xbox', 'Japan', '42410002', 'default.xbe', '9e5b8f53870ab5de09c2931139a06c299f222ebf8baf19fe8f2d2b4ade09b02f', 0x381DE4),
}

SPAWN_GUARDS = {
    ('PlayStation 2', 'USA'): ((2386114, 2147486688), (2386362, 2147484640)),
    ('PlayStation 2', 'Europe'): ((2362334, 2147486688), (2362582, 2147484640)),
    ('PlayStation 2', 'Japan'): (),
    ('GameCube', 'USA'): ((1574520, 2147486688), (1574768, 2147484640)),
    ('GameCube', 'Japan'): (),
    ('Xbox', 'USA'): ((1624028, 2147486688), (1624276, 2147484640)),
    ('Xbox', 'Japan'): (),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


# CISO layout reference: https://github.com/dolphin-emu/dolphin/blob/master/Source/Core/DiscIO/CISOBlob.h
class Disc:
    """Read a plain image or the logical sectors of a GameCube CISO."""
    def __init__(self, path):
        self.stream = Path(path).open('rb')
        try:
            self.original = os.fstat(self.stream.fileno())
            require(stat.S_ISREG(self.original.st_mode), 'Input must be a regular disc-image file.')
            self.size = self.original.st_size
            self.ciso_map = None
            self.format = 'ISO'
            head = self.physical(0, min(0x8000, self.size))
            if head[:4] == b'CISO':
                require(len(head) == 0x8000, 'Truncated CISO header.')
                self.block_size = struct.unpack_from('<I', head, 4)[0]
                require(0x8000 <= self.block_size <= 0x800000 and not self.block_size & (self.block_size - 1), 'Unsupported CISO block size.')
                require(set(head[8:]) <= {0, 1}, 'Invalid CISO block map.')
                self.ciso_map = []
                stored = 0
                for present in head[8:]:
                    self.ciso_map.append(stored if present else None)
                    stored += present
                require(0x8000 + stored * self.block_size <= self.size, 'Truncated CISO payload.')
                require(len(self.ciso_map) * self.block_size >= GC_SIZE, 'CISO map does not cover a GameCube disc.')
                self.size = GC_SIZE
                self.format = 'CISO'
            elif head[:3] in {b'RVZ', b'WIA'} or head[:4] == b'\x01\xc0\x0b\xb1':
                raise ValueError('Convert RVZ/WIA/GCZ to a plain GameCube ISO/GCM before patching.')
        except BaseException:
            self.stream.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.stream.close()

    def physical(self, offset, length):
        require(offset >= 0 and length >= 0 and offset + length <= self.original.st_size, 'Disc read is outside the input file.')
        self.stream.seek(offset)
        data = self.stream.read(length)
        require(len(data) == length, 'Input was truncated while reading.')
        return data

    def read(self, offset, length):
        require(offset >= 0 and length >= 0 and offset + length <= self.size, 'Disc extent is outside the image.')
        if self.ciso_map is None:
            return self.physical(offset, length)
        chunks = []
        while length:
            block, relative = divmod(offset, self.block_size)
            take = min(length, self.block_size - relative)
            stored = self.ciso_map[block]
            chunks.append(bytes(take) if stored is None else self.physical(0x8000 + stored * self.block_size + relative, take))
            offset += take
            length -= take
        return b''.join(chunks)

    def unchanged(self):
        current = os.fstat(self.stream.fileno())
        return (current.st_size, current.st_mtime_ns) == (self.original.st_size, self.original.st_mtime_ns)


def iso9660_files(disc):
    pvd = disc.read(16 * 2048, 2048)
    require(pvd[:7] == b'\x01CD001\x01', 'Invalid ISO9660 primary volume descriptor.')
    lba, size = struct.unpack_from('<I', pvd, 158)[0], struct.unpack_from('<I', pvd, 166)[0]
    require(34 <= size <= 1 << 20, 'Unsupported ISO9660 root directory size.')
    data = disc.read(lba * 2048, size)
    files = {}
    offset = 0
    while offset < len(data):
        length = data[offset]
        if not length:
            offset = (offset // 2048 + 1) * 2048
            continue
        require(length >= 34 and offset + length <= len(data), 'Invalid ISO9660 directory record.')
        record = data[offset:offset + length]
        offset += length
        require(33 + record[32] <= length, 'Invalid ISO9660 filename length.')
        name = record[33:33 + record[32]].decode('ascii').split(';')[0].lower()
        if not record[25] & 2:
            require(name not in files, 'Duplicate ISO9660 filename.')
            files[name] = (struct.unpack_from('<I', record, 2)[0] * 2048, struct.unpack_from('<I', record, 10)[0])
    return files


def gamecube_files(disc):
    header = disc.read(0, 0x440)
    require(header[0x1c:0x20] == b'\xc2\x33\x9f\x3d', 'Invalid GameCube disc header.')
    require(not header[0x200:0x208].startswith(b'NKIT'), 'Convert NKit to a plain GameCube ISO/GCM before patching.')
    fst_offset, fst_size = struct.unpack_from('>II', header, 0x424)
    require(12 <= fst_size <= 16 << 20, 'Invalid GameCube filesystem size.')
    fst = disc.read(fst_offset, fst_size)
    tag, parent, count = struct.unpack_from('>III', fst)
    require(tag == 0x01000000 and parent == 0 and 1 <= count <= fst_size // 12, 'Invalid GameCube filesystem root.')
    strings = fst[count * 12:]
    files = {}
    for i in range(1, count):
        tag, offset, size = struct.unpack_from('>III', fst, i * 12)
        require(tag >> 24 in (0, 1), 'Invalid GameCube filesystem entry.')
        if tag >> 24:
            continue
        name_offset = tag & 0xffffff
        require(name_offset < len(strings), 'GameCube filename is out of bounds.')
        terminator = strings.find(b'\x00', name_offset)
        require(terminator >= 0, 'Unterminated GameCube filename.')
        name = strings[name_offset:terminator].decode('ascii').lower()
        require(offset + size <= disc.size, 'GameCube file exceeds the disc.')
        if name == 'ndmw.afs':
            require(name not in files, 'Ambiguous GameCube archive filename.')
            files[name] = (offset, size)
    return files


def xbox_files(disc):
    descriptor = disc.read(32 * 2048, 2048)
    require(descriptor[:20] == XBOX_MAGIC and descriptor[-20:] == XBOX_MAGIC, 'Unsupported Xbox layout; use a game-partition XISO.')
    sector, size = struct.unpack_from('<II', descriptor, 20)
    require(14 <= size <= 1 << 20 and sector >= 33, 'Invalid Xbox root directory.')
    data = disc.read(sector * 2048, size)
    files, todo, seen = {}, [0], set()
    while todo:
        offset = todo.pop()
        require(offset not in seen and offset + 14 <= size, 'Invalid or cyclic Xbox directory tree.')
        seen.add(offset)
        left, right, sector, length, attributes, name_length = struct.unpack_from('<HHIIBB', data, offset)
        require(name_length > 0 and offset + 14 + name_length <= size, 'Invalid Xbox filename length.')
        name = data[offset + 14:offset + 14 + name_length].decode('ascii').lower()
        if not attributes & 0x10:
            require(name not in files and sector >= 33 and sector * 2048 + length <= disc.size, 'Invalid Xbox file extent or duplicate filename.')
            files[name] = (sector * 2048, length)
        todo.extend(pointer * 4 for pointer in (right, left) if pointer)
    return files


def identify(disc):
    header = disc.read(0, min(0x440, disc.size))
    if header[0x1c:0x20] == b'\xc2\x33\x9f\x3d':
        return 'GameCube', gamecube_files(disc), header[:6].decode('ascii')
    require(disc.ciso_map is None, 'CISO input must contain a GameCube image.')
    if disc.size >= 33 * 2048 and disc.read(32 * 2048, 20) == XBOX_MAGIC:
        disc.format = 'XISO'
        return 'Xbox', xbox_files(disc), None
    if disc.size >= 17 * 2048 and disc.read(16 * 2048 + 1, 5) == b'CD001':
        return 'PlayStation 2', iso9660_files(disc), None
    raise ValueError('Unrecognised image. Use PS2 ISO, GameCube ISO/GCM or CISO, or Xbox XISO.')


def inspect(disc):
    platform, files, disc_id = identify(disc)
    require('ndmw.afs' in files, 'The game archive NDMW.AFS is missing.')
    base, archive_size = files['ndmw.afs']
    require(base >= 0 and base + archive_size <= disc.size, 'Archive exceeds the image.')
    header = disc.read(base, 8)
    require(header[:4] == b'AFS\x00', 'Invalid NDMW.AFS header.')
    count = struct.unpack_from('<I', header, 4)[0]
    require(172 <= count <= 4096 and 8 + count * 8 <= archive_size, 'Invalid AFS entry table.')
    directory = disc.read(base + 8, count * 8)

    def entry(number):
        require(0 <= number < count, 'Stage file list references an invalid AFS entry.')
        offset, length = struct.unpack_from('<II', directory, number * 8)
        require(0 < length <= 64 << 20 and offset >= 8 + count * 8 and offset + length <= archive_size, 'Invalid AFS entry extent.')
        return base + offset, disc.read(base + offset, length)

    targets = []
    for number, name in ((137, b'stag0000'), (169, b'stagis11'), (170, b'stagis12'), (171, b'stagis13')):
        _, manifest = entry(number)
        require(name in manifest.lower(), 'The expected stage file list is missing.')
        references = re.findall(rb'\[0\.(\d+)\](?!/s)', manifest)
        require(len(references) == 1, 'Ambiguous scene reference in stage file list.')
        targets.append(int(references[0]))
    require(len(set(targets)) == 4, 'Scene and login packs must be distinct.')
    digest = hashlib.sha256()
    for index, number in enumerate(targets):
        offset, data = entry(number)
        digest.update(struct.pack('<II', number, len(data)))
        digest.update(data)
        if index:
            require(data.count(MARKER) == 1, 'Login destination is missing, ambiguous or already patched.')
    build = BUILDS.get(digest.hexdigest())
    require(build is not None and build[0] == platform, 'Unsupported release or altered developer-stage/login packs.')
    require(disc_id is None or disc_id == build[2], 'Disc ID does not match its game data.')
    if platform == 'GameCube':
        boot_offset = struct.unpack('>I', disc.read(0x420, 4))[0]
        header = disc.read(boot_offset, 0x100)
        offsets = struct.unpack_from('>18I', header, 0)
        sizes = struct.unpack_from('>18I', header, 0x90)
        ends = [offset + size for offset, size in zip(offsets, sizes) if size]
        require(ends and all(offset >= 0x100 for offset, size in zip(offsets, sizes) if size), 'Invalid GameCube DOL layout.')
        boot_size = max(ends)
    else:
        require(build[3] in files, 'Boot executable is missing.')
        boot_offset, boot_size = files[build[3]]
    require(0x100 <= boot_size <= 32 << 20, 'Unsupported executable size.')
    executable = disc.read(boot_offset, boot_size)
    require(hashlib.sha256(executable).hexdigest() == build[4], 'Unsupported, altered or already patched boot executable.')
    native_offset = build[5]
    require(executable[native_offset:native_offset + 9] == BEFORE + b'\x00', 'Native login destination is missing.')
    patches = [('Native login destination', boot_offset + native_offset, BEFORE, AFTER)]
    scene_offset, scene_data = entry(targets[0])
    for offset, expected in SPAWN_GUARDS[(platform, build[1])]:
        before = struct.pack('<I', expected)
        require(scene_data[offset:offset + 4] == before, 'Unexpected NPC visibility branch.')
        # JMPNE consumes two comparison operands. POP 2 has the same stack
        # effect and falls through, so NPCs spawn without writing save flags.
        patches.append(('Developer Stage NPC visibility', scene_offset + offset, before, struct.pack('<I', 5 | (2 << 6))))
    if platform == 'Xbox':
        require(executable[:4] == b'XBEH', 'Invalid XBE executable.')
        base, header_size = struct.unpack_from('<II', executable, 0x104)
        count, table_address = struct.unpack_from('<II', executable, 0x11c)
        table = table_address - base
        require(0 < count <= 256 and 0 <= table and table + count * 56 <= header_size <= len(executable), 'Invalid XBE section table.')
        changed = bytearray(executable)
        changed[native_offset:native_offset + 8] = AFTER
        found = 0
        for index in range(count):
            record = table + index * 56
            section_offset, section_size = struct.unpack_from('<II', executable, record + 12)
            require(section_offset + section_size <= len(executable), 'Invalid XBE section extent.')
            if section_offset <= native_offset and native_offset + 8 <= section_offset + section_size:
                old = hashlib.sha1(struct.pack('<I', section_size) + executable[section_offset:section_offset + section_size]).digest()
                require(old == executable[record + 36:record + 56], 'Invalid original XBE section digest.')
                new = hashlib.sha1(struct.pack('<I', section_size) + changed[section_offset:section_offset + section_size]).digest()
                patches.append(('XBE section digest', boot_offset + record + 36, old, new))
                found += 1
        require(found == 1, 'Native destination must belong to one XBE section.')
    require(disc.unchanged(), 'Input changed while identifying it.')
    return {'platform': build[0], 'region': build[1], 'serial': build[2], 'patches': sorted(patches, key=lambda row: row[1]), 'size': disc.size, 'format': disc.format}


def copy_patched(disc, target, plan):
    require(disc.unchanged(), 'Input changed after identification.')
    with target.open('xb') as writer:
        position = 0
        for label, offset, before, after in plan['patches']:
            require(len(before) == len(after) and offset >= position and offset + len(before) <= plan['size'], 'Invalid patch order or extent.')
            while position < offset:
                length = min(1024 * 1024, offset - position)
                writer.write(disc.read(position, length))
                position += length
            require(disc.read(position, len(before)) == before, 'Input changed after identification.')
            writer.write(after)
            position += len(before)
        while position < plan['size']:
            length = min(1024 * 1024, plan['size'] - position)
            writer.write(disc.read(position, length))
            position += length
        require(disc.unchanged(), 'Input changed while writing; discard the output.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path, help='Disc image; platform and region are detected from its contents')
    parser.add_argument('--output', type=Path, help='New ISO/GCM filename; must not already exist')
    parser.add_argument('--check', action='store_true', help='Show compatibility and patch plan without writing a file')
    args = parser.parse_args()
    if not args.check and args.output is None:
        parser.error('Use --check or provide --output with a new filename.')
    try:
        if args.output is not None:
            require(args.image.resolve() != args.output.resolve(), 'Input and output must be different files.')
            if not args.check:
                require(not args.output.exists(), 'Output already exists. Choose a new filename.')
                require(args.output.suffix.lower() in {'.iso', '.gcm'}, 'Use .iso or .gcm for the output; CISO input is expanded to plain ISO.')
        with Disc(args.image) as disc:
            plan = inspect(disc)
            print(f"Detected {plan['platform']} / {plan['region']} ({plan['serial']}); input format: {plan['format']}.")
            for label, offset, before, after in plan['patches']:
                print(f'{label}: image offset 0x{offset:08X}, {len(after)} bytes')
            if args.check:
                print('Compatibility check passed; no files written.')
                return
            require(plan['platform'] == 'GameCube' or args.output.suffix.lower() == '.iso', 'Use an .iso output filename for PS2 and Xbox.')
            copy_patched(disc, args.output, plan)
            require(args.output.stat().st_size == plan['size'], 'Unexpected output size; discard the output.')
        print(f'Created {args.output.name}. The original image was not modified.')
        print('Boot the new image and complete character selection to enter stag0000.')
    except (OSError, ValueError, struct.error) as error:
        print(f'Error: {error}', file=sys.stderr)
        raise SystemExit(1)


if __name__ == '__main__':
    main()

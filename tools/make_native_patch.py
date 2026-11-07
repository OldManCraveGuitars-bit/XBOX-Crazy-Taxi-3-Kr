"""Create a data-only copy/literal patch; requires the user's original and patched ISO.

The generated gzip stream contains offsets, lengths and changed data. It is
decoded by ordinary managed C# code, without executable extraction or subprocesses.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct

SOURCE_SHA = '63042c8c6abdf6e645214b47dffa8b9695b151a24c99ba2f18a513a4ef76cc26'
TARGET_SHA = '71f18581106d3bc0f22ada87a06011a065fd941fafed82c660c382edd49f5fa8'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def files(path):
    """Read the XDVDFS tree only; no extraction or changes to either ISO."""
    result = {}
    with path.open('rb') as stream:
        stream.seek(0x10000)
        header = stream.read(2048)
        assert header[:20] == header[-20:] == b'MICROSOFT*XBOX*MEDIA'
        visited_dirs = set()

        def directory(sector, length, parent):
            assert sector not in visited_dirs
            visited_dirs.add(sector)
            stream.seek(sector * 2048)
            data = stream.read(length)
            seen = set()

            def node(offset):
                assert offset not in seen and offset + 14 <= length
                seen.add(offset)
                left, right, start, size, attrs, nlen = struct.unpack_from('<HHIIBB', data, offset)
                name = data[offset + 14:offset + 14 + nlen].decode('ascii')
                assert name and name not in ('.', '..') and '/' not in name and '\\' not in name
                rel = parent + name
                if left:
                    node(left * 4)
                if attrs & 0x10:
                    directory(start, size, rel + '/')
                else:
                    result[rel] = (start * 2048, size)
                if right:
                    node(right * 4)

            if length:
                node(0)

        directory(*struct.unpack_from('<II', header, 20), '')
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('patches/CT3-Korean-v1.0.ct3patch'))
    args = parser.parse_args()
    assert digest(args.source) == SOURCE_SHA, 'Unexpected source'
    assert digest(args.target) == TARGET_SHA, 'Unexpected target'
    assert not args.output.exists(), 'Do not overwrite an existing patch'
    source_files, target_files = files(args.source), files(args.target)
    assert source_files.keys() == target_files.keys()
    stats = dict(copy_bytes=0, literal_bytes=0, zero_bytes=0, operations=0,
                 identical_files=0, changed_files=0)

    with args.source.open('rb') as source, args.target.open('rb') as target, args.output.open('xb') as raw:
        with gzip.GzipFile(fileobj=raw, mode='wb', filename='', mtime=0, compresslevel=9) as out:
            out.write(b'CT3KRP01' + struct.pack('<qq', args.source.stat().st_size, args.target.stat().st_size)
                      + bytes.fromhex(SOURCE_SHA) + bytes.fromhex(TARGET_SHA))

            def copy(offset, length):
                if length:
                    out.write(b'\x00' + struct.pack('<qI', offset, length))
                    stats['copy_bytes'] += length
                    stats['operations'] += 1

            def literal(data):
                if data:
                    if not any(data):
                        out.write(b'\x02' + struct.pack('<I', len(data)))
                        stats['zero_bytes'] += len(data)
                    else:
                        out.write(b'\x01' + struct.pack('<I', len(data)) + data)
                        stats['literal_bytes'] += len(data)
                    stats['operations'] += 1

            position = 0
            for name, (offset, length) in sorted(target_files.items(), key=lambda item: item[1][0]):
                target.seek(position)
                literal(target.read(offset - position))
                target.seek(offset)
                after = target.read(length)
                old_offset, old_length = source_files[name]
                source.seek(old_offset)
                before = source.read(old_length)
                if before == after:
                    copy(old_offset, length)
                    stats['identical_files'] += 1
                else:
                    stats['changed_files'] += 1
                    # Source blocks are compared by exact bytes; no hash collision can
                    # introduce a mistaken match. Reuse original texture/XBE data.
                    index = {}
                    for i in range(0, max(0, len(before) - 63), 16):
                        index.setdefault(before[i:i + 64], i)
                    cursor = pending = 0
                    while cursor + 64 <= len(after):
                        match = index.get(after[cursor:cursor + 64])
                        if match is None:
                            cursor += 1
                            continue
                        count = 64
                        maximum = min(len(before) - match, len(after) - cursor)
                        while count + 4096 <= maximum and before[match + count:match + count + 4096] == after[cursor + count:cursor + count + 4096]:
                            count += 4096
                        while count < maximum and before[match + count] == after[cursor + count]:
                            count += 1
                        literal(after[pending:cursor])
                        copy(old_offset + match, count)
                        cursor += count
                        pending = cursor
                    literal(after[pending:])
                position = offset + length
            target.seek(position)
            literal(target.read())
            out.write(b'\xff')
    assert sum(stats[k] for k in ('copy_bytes', 'literal_bytes', 'zero_bytes')) == args.target.stat().st_size
    stats.update(bytes=args.output.stat().st_size, sha256=digest(args.output),
                 source_sha256=SOURCE_SHA, output_sha256=TARGET_SHA)
    args.output.with_suffix('.json').write_text(json.dumps(stats, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()

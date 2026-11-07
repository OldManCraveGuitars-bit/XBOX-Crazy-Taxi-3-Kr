# CT3KRP01 data patch

The executable contains one gzip-compressed data resource, `CT3.patch`. The
compressed resource's SHA-256 is compiled into Program.cs and checked before
decoding. It never contains or extracts an executable or library.

The decompressed header uses little-endian integers:

| Field | Size |
| --- | --- |
| ASCII `CT3KRP01` | 8 bytes |
| Expected source ISO size | Int64 |
| Expected output ISO size | Int64 |
| Source SHA-256 | 32 bytes |
| Output SHA-256 | 32 bytes |

Commands follow sequentially. They contain no paths or execution instructions.

| Opcode | Data | Meaning |
| --- | --- | --- |
| `0x00` | Int64 source offset + UInt32 length | Copy from the original ISO |
| `0x01` | UInt32 length + literal bytes | Append changed data |
| `0x02` | UInt32 length | Append zero-filled bytes |
| `0xFF` | None | End; exact output size required |

Source/output bounds, command counts, EOF and the final ISO hash are validated.
Data is written to a newly created `.partial` ISO in the output directory. Only
a fully verified output is renamed to the requested, previously unused path.

`tools/make_native_patch.py` can reproduce the data patch when the supported
source and target ISOs are supplied. It requires Python 3.11+ for the build
tool only. Python is not used by the distributed EXE. The EXE itself builds
with `build.cmd` (or `build.ps1`) and the Windows .NET Framework C# compiler.

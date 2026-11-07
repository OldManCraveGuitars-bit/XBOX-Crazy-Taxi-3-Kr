The offline patcher includes these components. License texts are bundled here
and inside the executable. Game data is not covered by these software licenses.

| Component | Version | License | Upstream |
| --- | --- | --- | --- |
| Python / Tkinter runtime | 3.13 | PSF; Tcl/Tk notices in Python distribution | https://www.python.org/ |
| PyInstaller bootloader | 6.22.3 | GPL with bootloader exception | https://pyinstaller.org/ |
| xdelta3 | 3.2.1 | Apache-2.0 | https://github.com/jmacd/xdelta/tree/v3.2.1 |
| liblzma (inside upstream xdelta binary) | upstream build | 0BSD | https://tukaani.org/xz/ |
| BLAKE3 (inside upstream xdelta binary) | upstream build | CC0 / Apache-2.0 | https://github.com/BLAKE3-team/BLAKE3 |

xdelta3 copyright Joshua MacDonald and contributors.
This software includes code from XZ Utils. Copyright the XZ Utils authors and contributors.
BLAKE3 copyright the BLAKE3 authors.

The xdelta3 executable is unmodified from the upstream Windows x86-64 v3.2.1
release. Its SHA-256 is recorded in patches/manifest.json.

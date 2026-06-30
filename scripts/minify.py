"""
Produce minified copies of build/AdobeDC.admx and build/en-US/AdobeDC.adml for
packaging into release zips. Strips XML comments and insignificant
inter-element whitespace (pure-whitespace text/tail nodes), which is what
ElementTree drops naturally on a parse/serialize round-trip. Text content of
leaf elements (e.g. <string id="..._Explain"> bodies, which rely on embedded
newlines for paragraph formatting in the GPMC properties pane) is untouched,
since that text is never pure whitespace.

The source files in build/ are left exactly as they are -- this only writes
new *.min.admx / *.min.adml files for the release packaging step.

Usage: python scripts/minify.py [output_dir]
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent.parent
ADMX = ROOT / "build" / "AdobeDC.admx"
ADML = ROOT / "build" / "en-US" / "AdobeDC.adml"

# Both files declare this as the default (unprefixed) namespace. Without
# registering it, ElementTree invents an "ns0:" prefix on every tag when
# re-serializing -- XML-equivalent, but not worth risking against a GPO/Intune
# parser that may not be fully namespace-prefix-agnostic.
ET.register_namespace("", "http://schemas.microsoft.com/GroupPolicy/2006/07/PolicyDefinitions")


def strip_insignificant_whitespace(elem: ET.Element) -> None:
    if elem.text is not None and elem.text.strip() == "":
        elem.text = None
    if elem.tail is not None and elem.tail.strip() == "":
        elem.tail = None
    for child in elem:
        strip_insignificant_whitespace(child)


def minify(src: Path, dst: Path) -> tuple[int, int]:
    tree = ET.parse(src)
    root = tree.getroot()
    strip_insignificant_whitespace(root)
    tree.write(dst, encoding="utf-8", xml_declaration=True)
    return src.stat().st_size, dst.stat().st_size


def main() -> int:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist"
    admx_out = out_dir / "AdobeDC.admx"
    adml_out = out_dir / "en-US" / "AdobeDC.adml"
    admx_out.parent.mkdir(parents=True, exist_ok=True)
    adml_out.parent.mkdir(parents=True, exist_ok=True)

    over_limit = False
    for src, dst, label in ((ADMX, admx_out, "ADMX"), (ADML, adml_out, "ADML")):
        before, after = minify(src, dst)
        kb_before, kb_after = before / 1024, after / 1024
        b64_after = after * 4 / 3 / 1024
        print(
            f"{label}: {kb_before:.1f} KB -> {kb_after:.1f} KB minified "
            f"({b64_after:.1f} KB base64-encoded)"
        )
        if b64_after > 1024:
            print(
                f"ERROR: {label} base64-encoded size ({b64_after:.1f} KB) exceeds "
                f"Intune's 1024 KB upload limit even after minification",
                file=sys.stderr,
            )
            over_limit = True

    return 1 if over_limit else 0


if __name__ == "__main__":
    sys.exit(main())

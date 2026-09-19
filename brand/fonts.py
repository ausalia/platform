"""Downloads the brand typefaces (all SIL Open Font License, from the Google Fonts
repository) and cuts static instances from the variable fonts, because reportlab
cannot pick a weight from a variable font. Output: build/fonts/."""
import sys
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT = Path(__file__).resolve().parent / "build" / "fonts"
RAW = "https://github.com/google/fonts/raw/main/ofl"

STATIC = {  # file -> path under ofl/
    "IBMPlexMono-Regular.ttf": "ibmplexmono/IBMPlexMono-Regular.ttf",
    "IBMPlexMono-Medium.ttf": "ibmplexmono/IBMPlexMono-Medium.ttf",
    "IBMPlexMono-SemiBold.ttf": "ibmplexmono/IBMPlexMono-SemiBold.ttf",
    # Poppins is only used by the logo analysis report, to match its reference layout
    "Poppins-Regular.ttf": "poppins/Poppins-Regular.ttf",
    "Poppins-Medium.ttf": "poppins/Poppins-Medium.ttf",
    "Poppins-SemiBold.ttf": "poppins/Poppins-SemiBold.ttf",
    "Poppins-Bold.ttf": "poppins/Poppins-Bold.ttf",
}
VARIABLE = {  # source, [(output, axes)]
    "SpaceGrotesk-VF.ttf": ("spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf", [
        ("SpaceGrotesk-Medium.ttf", {"wght": 500}), ("SpaceGrotesk-Bold.ttf", {"wght": 700})]),
    "Inter-VF.ttf": ("inter/Inter%5Bopsz%2Cwght%5D.ttf", [
        ("Inter-Regular.ttf", {"wght": 400, "opsz": 14}), ("Inter-Medium.ttf", {"wght": 500, "opsz": 14}),
        ("Inter-SemiBold.ttf", {"wght": 600, "opsz": 14})]),
}

def fetch(rel, dest):
    if dest.exists():
        return
    print("downloading", dest.name)
    urllib.request.urlretrieve(f"{RAW}/{rel}", dest)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, rel in STATIC.items():
        fetch(rel, OUT / name)
    for src, (rel, instances) in VARIABLE.items():
        fetch(rel, OUT / src)
        for out, axes in instances:
            if not (OUT / out).exists():
                print("cutting", out)
                instancer.instantiateVariableFont(TTFont(OUT / src), axes, inplace=False).save(OUT / out)

if __name__ == "__main__":
    sys.exit(main())

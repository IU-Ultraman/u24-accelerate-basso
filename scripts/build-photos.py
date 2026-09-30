#!/usr/bin/env python3
"""Build web-ready team headshots and meeting photos from the originals.

Originals live in assets/APRICOT Team photos/, assets/BSO-AD/, assets/ODFA/,
assets/PHASES/ and assets/July*.jpg. They are camera/press originals (some over
10 MB), so they are not committed or deployed; this script derives the small,
uniform files the site actually loads:

    assets/images/team/<slug>.jpg        400x400, square, JPEG q82
    assets/images/meetings/<date>.jpg    max 1800px wide, JPEG q78

Headshots are cropped to a square whose side is the short edge of the original,
centred horizontally and biased toward the top (faces sit above centre in a
headshot). FOCUS_OVERRIDES nudges the crop for photos where the subject is not
centred. SLIDE_CROPS first reapplies a crop someone already chose for a photo,
for originals that were pulled out of a slide deck. Re-run after adding
originals:

    python3 scripts/build-photos.py
"""
import pathlib
import sys

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT_TEAM = ASSETS / "images" / "team"
OUT_MEET = ASSETS / "images" / "meetings"

AVATAR_PX = 400   # cap: never larger than this
AVATAR_MIN_PX = 192  # floor: never upscale a small original past this
AVATAR_Q = 82
MEETING_MAX_W = 1800
MEETING_Q = 78

# original file (relative to assets/) -> person's name exactly as the team card shows it
HEADSHOTS = {
    # --- APRICOT ---------------------------------------------------------
    "APRICOT Team photos/Susan Michie.jpg": "Susan Michie",
    "APRICOT Team photos/William Hogan.jpg": "William Hogan",
    "APRICOT Team photos/MARTA MARQUES.png": "Marta Marques",
    "APRICOT Team photos/Robert West.jpg": "Robert West",
    "APRICOT Team photos/Marie Johnston.jpg": "Marie Johnston",
    "APRICOT Team photos/Alex Rothman.jpg": "Alex Rothman",
    "APRICOT Team photos/Maya Braun.jpg": "Maya Braun",
    "APRICOT Team photos/Paulina Schenk.jpg": "Paulina Schenk",
    "APRICOT Team photos/Carolina Silva.jpg": "Carolina Silva",
    "APRICOT Team photos/Micaela Santilli.jpg": "Micaela Santilli",
    # --- BSO-AD ----------------------------------------------------------
    "BSO-AD/Cui Tao.png": "Cui Tao",
    "BSO-AD/Jiang Bian.png": "Jiang Bian",
    "BSO-AD/Fang Li.png": "Fang Li",
    "BSO-AD/Haifang Li.png": "Haifang Li",
    "BSO-AD/Yue Yu.jpg": "Yue Yu",
    "BSO-AD/Weiguo Cao.png": "Weiguo Cao",
    "BSO-AD/Rakesh Kumar.jpg": "Rakesh Kumar",
    "BSO-AD/Issac H. Clark.jpg": "Isaac H. Clark",  # supplied file misspells "Isaac"
    "BSO-AD/Xing He.jpg": "Xing He",
    "BSO-AD/Xuguang Ai.jpg": "Xuguang Ai",
    "BSO-AD/Yuhang Jiang.jpg": "Yuhang Jiang",
    # --- ODFA ------------------------------------------------------------
    # Bill Duncan's headshot comes from the PHASES slide below: it is the same
    # photograph as "ODFA/duncan headshot.jpg" at 486px instead of 278px.
    "ODFA/McNeil_Daniel_W._Headshot_2024.jpg": "Dan McNeil",
    "ODFA/Olga Ensz Head Shot.jpg": "Olga Ensz",
    "ODFA/Astha Singhal.jpg": "Astha Singhal",
    "ODFA/BRENDA HEATON_002_SOD_MAY 13, 2025.jpg": "Brenda Heaton",
    "ODFA/Alex Diehl.jpg": "Alex Diehl",
    "ODFA/Corinne-Huggins-Manley- professional pic.jpeg": "Corinne Huggins-Manley",
    "ODFA/Finn Wilson.jpg": "Finn Wilson",
    "ODFA/Michelle Cooper.jpg": "Michelle Cooper",
    # --- PHASES ----------------------------------------------------------
    # Extracted from the PHASES team's headshot slide ("PHASES headshots.pptx",
    # one slide, each photo captioned with the person's name). Files are named
    # by the slide caption; the value is the name on the site's team card.
    "PHASES/John Beverley.png": "John Beverley",
    "PHASES/Bill Duncan.png": "Bill Duncan",
    "PHASES/Oliver He.png": "Yongqun He",  # "Oliver" is Yongqun He's English name
    "PHASES/Julie Bowker.png": "Julie Bowker",
    "PHASES/Hollen Reischer.png": "Hollen Reischer",
    "PHASES/Damayanthi Jesudas.png": "Damayanthi Jesudas",
    "PHASES/Jie Zheng.png": "Jie Zheng",
    "PHASES/Regina Hurley.jpg": "Regina Hurley",
    "PHASES/Maxime Jublou.jpg": "Maxime Jublou",
    "PHASES/Jeremy Ravenel.png": "Jeremy Ravenel",
}

# Headshots supplied for people who do not appear on any team roster on the site.
# Left unbuilt on purpose - adding a face needs a name, role and affiliation.
UNMATCHED = []

# slug -> (x_bias, y_bias) in 0..1 over the unused margin. Default (0.5, 0.12):
# horizontally centred, biased toward the top.
FOCUS_OVERRIDES = {
    "corinne-huggins-manley": (0.10, 0.12),  # landscape frame, subject left of centre
}
DEFAULT_FOCUS = (0.5, 0.12)

# slug -> (left, top, right, bottom) fractions trimmed off the original before
# the square crop. These are the crops the slide author applied in PowerPoint
# (<a:srcRect> on the picture), copied exactly so the photo is framed the way
# its owner chose rather than from the raw, uncropped file.
SLIDE_CROPS = {
    "regina-hurley": (0.16673, 0.22475, 0.16068, 0.0),  # raw file is mostly library
    "julie-bowker": (0.0, 0.0, 0.0, 0.17756),
}

MEETINGS = {
    "July 11 2025.jpg": "2025-07-11",
    "July 17 2026.jpg": "2026-07-17",
}


def slugify(name):
    keep = [c.lower() if c.isalnum() else "-" for c in name]
    slug = "".join(keep)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def load_rgb(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)  # honour camera orientation
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGB", im.size, (255, 255, 255))
        flat.paste(im, mask=im.split()[-1])
        return flat
    return im.convert("RGB")


def trim(im, fractions):
    l, t, r, b = fractions
    w, h = im.size
    return im.crop((round(w * l), round(h * t), round(w * (1 - r)), round(h * (1 - b))))


def square_crop(im, focus):
    w, h = im.size
    side = min(w, h)
    fx, fy = focus
    left = round((w - side) * fx)
    top = round((h - side) * fy)
    return im.crop((left, top, left + side, top + side))


def build_headshots():
    OUT_TEAM.mkdir(parents=True, exist_ok=True)
    # Two originals for one person would silently overwrite each other.
    slugs = [slugify(p) for p in HEADSHOTS.values()]
    dupes = sorted({x for x in slugs if slugs.count(x) > 1})
    if dupes:
        raise SystemExit(f"more than one original maps to: {', '.join(dupes)}")
    built, missing = [], []
    for rel, person in sorted(HEADSHOTS.items(), key=lambda kv: kv[1]):
        src = ASSETS / rel
        if not src.exists():
            missing.append(rel)
            continue
        slug = slugify(person)
        im = load_rgb(src)
        orig = im.size
        if slug in SLIDE_CROPS:
            im = trim(im, SLIDE_CROPS[slug])
        im = square_crop(im, FOCUS_OVERRIDES.get(slug, DEFAULT_FOCUS))
        # Small originals are common here; upscaling them to a uniform 400px
        # only invents blur, so clamp the target to the source's own size with
        # a floor that still looks sharp at the 96px modal on a 2x screen.
        side = im.size[0]
        target = min(AVATAR_PX, max(AVATAR_MIN_PX, side))
        upscaled = target > side
        im = im.resize((target, target), Image.LANCZOS)
        dest = OUT_TEAM / f"{slug}.jpg"
        im.save(dest, "JPEG", quality=AVATAR_Q, optimize=True, progressive=True)
        built.append((person, slug, orig, target, dest.stat().st_size, upscaled))
    return built, missing


def build_meetings():
    OUT_MEET.mkdir(parents=True, exist_ok=True)
    built, missing = [], []
    for rel, stem in sorted(MEETINGS.items(), key=lambda kv: kv[1]):
        src = ASSETS / rel
        if not src.exists():
            missing.append(rel)
            continue
        im = load_rgb(src)
        orig = im.size
        if im.width > MEETING_MAX_W:
            im = im.resize(
                (MEETING_MAX_W, round(im.height * MEETING_MAX_W / im.width)),
                Image.LANCZOS,
            )
        dest = OUT_MEET / f"{stem}.jpg"
        im.save(dest, "JPEG", quality=MEETING_Q, optimize=True, progressive=True)
        built.append((stem, orig, im.size, dest.stat().st_size))
    return built, missing


def main():
    heads, head_missing = build_headshots()
    meets, meet_missing = build_meetings()

    print(f"headshots: {len(heads)} built -> {OUT_TEAM.relative_to(ROOT)}/")
    for person, slug, orig, out, size, upscaled in heads:
        flag = "  (small original, upscaled)" if upscaled else ""
        print(f"  {person:20s} {slug + '.jpg':26s} {orig[0]}x{orig[1]:<5} -> {out}px {size // 1024:3d} KB{flag}")

    print(f"\nmeeting photos: {len(meets)} built -> {OUT_MEET.relative_to(ROOT)}/")
    for stem, orig, new, size in meets:
        print(f"  {stem}.jpg  {orig[0]}x{orig[1]} -> {new[0]}x{new[1]}  {size // 1024} KB")

    if UNMATCHED:
        print(f"\n{len(UNMATCHED)} headshot(s) not built - no matching team card on the site:")
        for rel in UNMATCHED:
            print(f"  {rel}")

    if head_missing or meet_missing:
        print("\nMISSING originals:", file=sys.stderr)
        for rel in head_missing + meet_missing:
            print(f"  {rel}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

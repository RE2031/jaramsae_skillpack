#!/usr/bin/env python3
"""Verify that the renderer produced the promised editable and PNG artifacts."""
import argparse, json, struct, sys
from pathlib import Path

def png_size(path):
    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("invalid PNG")
    return struct.unpack(">II", header[16:24])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    issues, checked = [], []
    required = [
        out / "editable/index.html", out / "editable/style.css",
        out / "editable/feed.json", out / "preview.html",
        out / "captions.md", out / "sources.md", out / "review-report.json"
    ]
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            issues.append(f"missing/empty: {path.relative_to(out)}")
    try:
        feed = json.loads((out / "editable/feed.json").read_text(encoding="utf-8"))
        expected = sum(len(post["slides"]) for post in feed["posts"])
        pngs = sorted((out / "png").glob("post-*-slide-*.png"))
        if len(pngs) != expected:
            issues.append(f"expected {expected} slide PNGs, found {len(pngs)}")
        for path in pngs:
            try:
                size = png_size(path)
                if size != (1080, 1350):
                    issues.append(f"{path.name}: expected 1080x1350, got {size[0]}x{size[1]}")
                else:
                    checked.append(path.name)
            except Exception as exc:
                issues.append(f"{path.name}: {exc}")
        html = (out / "editable/index.html").read_text(encoding="utf-8")
        if html.count('class="slide ') != expected:
            issues.append("HTML slide count does not match feed.json")
        report = json.loads((out / "review-report.json").read_text(encoding="utf-8"))
        if report.get("errors"):
            issues.append("renderer reported layout or image errors")
        if not pngs:
            issues.append("no individual slide PNGs were generated")
        preview = (out / "preview.html").read_text(encoding="utf-8")
        if preview.count("<img ") != expected + (0 if feed.get("body_only",False) else len(feed["posts"])):
            issues.append("preview image count does not match covers + all slides")
        if 'src="png/' in preview or 'href="png/' in preview:
            issues.append("preview still contains fragile relative PNG paths")
        if preview.count("data:image/png;base64,") < expected + (0 if feed.get("body_only",False) else len(feed["posts"])):
            issues.append("preview does not embed all PNG images")
    except Exception as exc:
        issues.append(f"could not inspect render output: {exc}")
    result = {
        "passed": not issues,
        "output_directory": str(out),
        "expected_slides": expected if "expected" in locals() else None,
        "verified_pngs": len(checked),
        "issues": issues
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues else 1

if __name__ == "__main__":
    raise SystemExit(main())

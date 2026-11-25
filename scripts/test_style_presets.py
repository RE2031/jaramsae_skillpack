#!/usr/bin/env python3
"""Lightweight consistency checks for the supported visual style presets."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
schema = json.loads((ROOT / "schemas/feed.schema.json").read_text(encoding="utf-8"))
preset = json.loads((ROOT / "references/styles/bold-photo-editorial.json").read_text(encoding="utf-8"))
css = (ROOT / "templates/style.css").read_text(encoding="utf-8")
renderer = (ROOT / "scripts/render.py").read_text(encoding="utf-8")

styles = schema["properties"]["style"]["enum"]
assert "bold-photo-editorial" in styles, "bold-photo-editorial missing from JSON schema"
assert "editorial-hybrid" in styles, "editorial-hybrid alternative must remain available"
assert preset["name"] == "bold-photo-editorial", "preset name mismatch"
assert ".preset-bold-photo-editorial" in css, "bold photo editorial CSS class missing"
assert "bold-photo-editorial" in renderer and "image_kind" in renderer and "image_credit" in renderer, "renderer photo validation missing"
assert preset["visual_balance"]["photo"] > preset["visual_balance"]["text"], "photo-led balance expected"
assert preset["composition"]["headline"], "headline composition missing"
print("STYLE_PRESET_CHECKS_PASSED: bold-photo-editorial and editorial-hybrid are configured.")

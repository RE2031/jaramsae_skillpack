#!/usr/bin/env python3
"""Run preflight, renderer and artifact verification as one fail-fast pipeline."""
import argparse, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def run(command):
    print("\n>>>", " ".join(map(str, command)), flush=True)
    return subprocess.run(command, cwd=ROOT).returncode

def main():
    parser = argparse.ArgumentParser(description="Jaramsae Instagram content render pipeline")
    parser.add_argument("input", type=Path, help="AI-authored feed JSON")
    parser.add_argument("--out", required=True, type=Path, help="New output directory")
    parser.add_argument("--browser", help="Optional Chromium executable path")
    args = parser.parse_args()
    source = args.input if args.input.is_absolute() else (Path.cwd() / args.input)
    output = args.out if args.out.is_absolute() else (Path.cwd() / args.out)
    if not source.is_file():
        parser.error(f"input JSON not found: {source}")
    if output.exists():
        parser.error(f"output directory already exists; choose a new path: {output}")
    commands = [
        [sys.executable, str(ROOT / "scripts/preflight.py")],
        [sys.executable, str(ROOT / "scripts/render.py"), str(source), "--out", str(output)]
    ]
    if args.browser:
        commands[1] += ["--browser", args.browser]
    commands.append([sys.executable, str(ROOT / "scripts/quality_check.py"), "--out", str(output)])
    for command in commands:
        code = run(command)
        if code:
            print(f"\nPIPELINE_FAILED (exit {code}). Fix the issue above; do not report success.")
            return code
    print(f"\nPIPELINE_SUCCESS: editable HTML/CSS and individual slide PNGs verified at {output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

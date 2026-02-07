#!/usr/bin/env python3
import argparse
import json
import random
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

def load_config(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"Config parse error in {path}: {e}")
    return {
             "images_dir": "~/pictures",
             "order": "random",
             "low_threshold":  3.2,
             "plugged_in_threshold": 4.7,
             "last_image": None
           }

def choose_image(images, order, last_image):
        if order == "alphabetical":
                images = sorted(images, key=lambda p: p.name.lower())
        elif order == "date_added":
                images = sorted(images, key=lambda p: p.stat().st_mtime)
        elif order == "random":
                if len(images) > 1 and last_image:
                        images = [p for p in images if str(p) != last_image]
                return random.choice(images)
        if last_image:
                for i, p in enumerate(images):
                        if str(p) == last_image:
                                return images[(i + 1) % len(images)]
        return images[0]

def main():
        # Load defaults from config
        config_path = Path(__file__).resolve().parent / "config.json"
        config = load_config(config_path)

        # Script Argument setup
        p = argparse.ArgumentParser(description="E-ink photo frame manager")

        p.add_argument("--images-dir", default=None, help="Folder containing images")
        p.add_argument("--order", choices=["alphabetical", "date_added", "random"], default=None, help="Order to show the files on the screen")
        p.add_argument("--low-threshold", type=float, default=None, help="Voltage that counts as 'low'")

        args = p.parse_args()

        # Get all valid images
        images_dir = Path(args.images_dir or config.get("images_dir")).expanduser()
        valid_ext = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
        images = [p for p in images_dir.rglob("*") if p.is_file() and p.suffix.lower() in valid_ext]

        if not images:
                print(f"No images found in {images_dir}", file=sys.stderr)
                images = [Path(__file__).resolve().parent / "default.jpg"]

        # Get battery status
        script_dir = os.path.join(os.path.expanduser('~'), 'eink-pictures', 'check_battery.sh')
        check_battery = subprocess.run([script_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        battery = check_battery.stdout.strip()
        voltage = None
        if args.low_threshold is not None:
                low_threshold = args.low_threshold
        else:
                low_threshold = config.get("low_threshold", 3.2)

        if battery and "VOLTAGE=" in battery:
                voltage = float(battery.split("=", 1)[1])

        low_battery = False
        if voltage is not None and voltage <= low_threshold:
                low_battery = True

        # Choose image to show
        order = args.order or config.get("order")
        new_image = choose_image(images, order, config.get("last_image"))
        config["last_image"] = str(new_image)
        config_path.write_text(json.dumps(config, indent=2))

        # Show image on screen
        show_script_dir = os.path.join(os.path.expanduser('~'), 'eink-pictures', 'run_show_image.sh')
        cmd = [show_script_dir, str(new_image)]
        if low_battery:
                cmd += ["--battery"]
        subprocess.run(cmd)

if __name__ == "__main__":
        main()

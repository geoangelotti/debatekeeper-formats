#!/usr/bin/env python
"""Updates the list in formats.json. Should be run after any updates to formats, and the result
committed to the repository."""

import argparse
import json
from lxml import etree
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("formats_dir", nargs="?", default=Path("formats"), type=Path)
parser.add_argument("-O", "--output-file", default="formats.json")
parser.add_argument("--add-errors", action="store_true",
    help="Adds some erroneous entries to test error conditions in the app")
args = parser.parse_args()

if not args.formats_dir.is_dir():
    print(f"{formats_dir} is not a directory")
    exit(1)

validator = etree.RelaxNG(etree.parse("schema-2.2.rng"))

formats = []

for child in args.formats_dir.iterdir():
    if child.suffix != ".xml":
        print(f"skipping {child}")
        continue

    child_root = etree.parse(open(child))

    if not validator.validate(child_root):
        err = validator.error_log.last_error
        print(f"Validation error in {child.name}, line {err.line}: {err.message}")

    info = child_root.find("info")
    formats.append({
        "filename": child.name,
        "name": child_root.find("name").text,
        "url": f"https://formats.debatekeeper.czlee.nz/formats/{child.name}",
        "version": int(child_root.find("version").text),
        "regions": [e.text for e in info.findall("region")],
        "levels": [e.text for e in info.findall("level")],
        "used-ats": [e.text for e in info.findall("used-at")],
        "description": info.find("description").text,
    })

formats.sort(key=lambda f: f['name'])

if args.add_errors:
    formats.extend([{
        "filename": "nosuchfile.xml",
        "name": "No such file",
        "url": "https://formats.debatekeeper.czlee.nz/formats/nosuchfile.xml",
        "version": 1,
        "regions": ["Nowhere"],
        "levels": ["None"],
        "used-ats": ["Nowhere"],
        "description": "Test entry to check what it does when the file doesn't exist"
      },
      {
        "filename": "wronghost.xml",
        "name": "Wrong host",
        "url": "https://czlee.github.io/debatekeeper-formats/formats/wronghost.xml",
        "version": 1,
        "regions": ["Nowhere"],
        "levels": ["None"],
        "used-ats": ["Nowhere"],
        "description": "Test entry to check what it does when the host is different to what's expected"
    }])

with open(args.output_file, "w") as fp:
    json.dump(formats, fp, indent=2)

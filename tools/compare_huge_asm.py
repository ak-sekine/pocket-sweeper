#!/usr/bin/env python3
"""Compare generated and hUGETracker ASM by semantic-looking labelled sections."""
import argparse
import re
from pathlib import Path

SECTION = re.compile(r"^(?P<label>[A-Za-z_][A-Za-z0-9_]*)(?:::|:)$")

def sections(path):
    result, current, lines = {}, None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = SECTION.match(line.strip())
        if match:
            if current is not None: result[current] = lines
            current, lines = match.group("label"), []
        elif current is not None:
            lines.append(line.strip())
    if current is not None: result[current] = lines
    return result

def normalize(lines):
    return [re.sub(r";.*$", "", line).strip() for line in lines if line.strip() and not line.lstrip().startswith(";")]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("generated")
    parser.add_argument("export")
    args = parser.parse_args()
    generated, exported = sections(args.generated), sections(args.export)
    labels = sorted(set(generated) | set(exported))
    for label in labels:
        left, right = normalize(generated.get(label, [])), normalize(exported.get(label, []))
        if label.endswith("_loop_metadata"):
            status = "hUGETracker標準Exportに存在しない独自拡張"
        elif label not in generated or label not in exported:
            status = "比較不能"
        elif left == right:
            status = "一致"
        else:
            status = "表記上の差異または再生動作に影響する不一致"
        print(f"{status}\t{label}\tgenerated={len(left)} export={len(right)}")

if __name__ == "__main__":
    main()

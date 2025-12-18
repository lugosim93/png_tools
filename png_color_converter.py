import argparse
import os
from typing import Optional, Tuple

import numpy as np
from PIL import Image


DEFAULT_SOURCE = (0, 0, 0)
DEFAULT_TARGET = (6, 145, 15)


def parse_color(color_str: str) -> Tuple[int, int, int]:
    s = color_str.strip()
    if s.startswith("#"):
        s = s[1:]
    if all(c in "0123456789abcdefABCDEF" for c in s) and len(s) == 6:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
        return (r, g, b)
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
    else:
        parts = s.split()
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            "Color must be in #RRGGBB or 'R,G,B' (0-255) format"
        )
    try:
        r, g, b = (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Color components must be integers between 0 and 255"
        )
    for v in (r, g, b):
        if v < 0 or v > 255:
            raise argparse.ArgumentTypeError(
                "Color components must be in the range 0-255"
            )
    return (r, g, b)


def convert_png_color(
    input_path: str,
    output_path: Optional[str] = None,
    source_color: Tuple[int, int, int] = DEFAULT_SOURCE,
    target_color: Tuple[int, int, int] = DEFAULT_TARGET,
    tolerance: float = 0.30,
    metric: str = "euclidean",
) -> str:
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = f"{base}_converted.png"

    with Image.open(input_path) as im:
        if im.mode not in ("RGBA", "RGB"):
            im = im.convert("RGBA")
        elif im.mode == "RGB":
            im = im.convert("RGBA")

        arr = np.array(im)

    rgb = arr[..., :3].astype(np.float32)
    alpha = arr[..., 3]

    src = np.array(source_color, dtype=np.float32)
    diff = rgb - src

    if metric == "euclidean":
        dist = np.linalg.norm(diff, axis=-1)
        max_dist = np.sqrt(3.0) * 255.0
        norm = dist / max_dist
        mask = norm <= float(tolerance)
    elif metric == "channel":
        thr = float(tolerance) * 255.0
        mask = np.all(np.abs(diff) <= thr, axis=-1)
    else:
        raise ValueError("metric must be 'euclidean' or 'channel'")

    non_transparent = alpha > 0
    mask = mask & non_transparent

    arr[mask, :3] = target_color

    out = Image.fromarray(arr, mode="RGBA")
    out.save(output_path, format="PNG")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert pixels near a source color to a target color in a PNG. "
            "Similarity is determined by a selectable metric: 'euclidean' or 'channel'."
        ),
        epilog=(
            "Color formats: #RRGGBB or 'R,G,B'.\n"
            "Tolerance: 0.0 (only exact source) .. 1.0 (all pixels).\n\n"
            "Examples:\n"
            "  python png_converter.py input.png --source 0,0,0 --target 6,145,15\n"
            "  python png_converter.py input.png --source #000000 --target #06910F -t 0.30\n"
            "  python png_converter.py input.png -s 0,0,0 --target 6,145,15 -t 0.2 -m channel\n"
            "  python png_converter.py input.png -s \"12,12,12\" --target #00FF00 -o out.png\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("input", help="Path to input PNG file")
    parser.add_argument(
        "-o",
        "--output",
        help="Path to output PNG file (default: <input>_converted.png)",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--source",
        type=parse_color,
        default=DEFAULT_SOURCE,
        help="Source color to replace near (default: 0,0,0)",
    )
    parser.add_argument(
        "--target",
        type=parse_color,
        default=DEFAULT_TARGET,
        help="Target color to apply (default: 6,145,15)",
    )
    parser.add_argument(
        "-t",
        "--tolerance",
        type=float,
        default=0.30,
        help=(
            "Similarity threshold as a fraction between 0 and 1 (default: 0.30).\n"
            "For metric=euclidean, it's normalized RGB distance. For metric=channel,\n"
            "it's per-channel absolute difference normalized by 255."
        ),
    )
    parser.add_argument(
        "-m",
        "--metric",
        choices=["euclidean", "channel"],
        default="euclidean",
        help=(
            "Similarity metric: 'euclidean' (normalized RGB distance) or 'channel'\n"
            "(per-channel threshold). Default: euclidean."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_path = convert_png_color(
        input_path=args.input,
        output_path=args.output,
        source_color=args.source,
        target_color=args.target,
        tolerance=args.tolerance,
        metric=args.metric,
    )
    print(f"Saved converted image to: {out_path}")


if __name__ == "__main__":
    main()


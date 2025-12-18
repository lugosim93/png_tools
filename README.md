# png_tools
PNG image converting tool, such as color replacement


## png_color_converter.py

usage: `png_color_converter.py [-h] [-o OUTPUT] [-s SOURCE] [--target TARGET] [-t TOLERANCE] [-m {euclidean,channel}] input`

### Convert pixels near a source color to a target color in a PNG. Similarity is determined by a selectable metric: 'euclidean' or 'channel'.

```
positional arguments:
  input                 Path to input PNG file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to output PNG file (default: <input>_converted.png)
  -s SOURCE, --source SOURCE
                        Source color to replace near (default: 0,0,0)
  --target TARGET       Target color to apply (default: 6,145,15)
  -t TOLERANCE, --tolerance TOLERANCE
                        Similarity threshold as a fraction between 0 and 1 (default: 0.30).
                        For metric=euclidean, it's normalized RGB distance. For metric=channel,
                        it's per-channel absolute difference normalized by 255.
  -m {euclidean,channel}, --metric {euclidean,channel}
                        Similarity metric: 'euclidean' (normalized RGB distance) or 'channel'
                        (per-channel threshold). Default: euclidean.

Color formats: #RRGGBB or 'R,G,B'.
Tolerance: 0.0 (only exact source) .. 1.0 (all pixels).

Examples:
  python png_color_converter.py input.png --source 0,0,0 --target 6,145,15
  python png_color_converter.py input.png --source #000000 --target #06910F -t 0.30
  python png_color_converter.py input.png -s 0,0,0 --target 6,145,15 -t 0.2 -m channel
  python png_color_converter.py input.png -s "12,12,12" --target #00FF00 -o out.png
 
```
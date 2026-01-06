
from __future__ import annotations

from pathlib import Path

from PIL import Image


def webp_to_png(input_path: str | Path, output_path: str | Path) -> None:
	"""Convert a .webp image to .png with alpha preserved.

	Args:
		input_path: Source .webp file path.
		output_path: Target .png file path.
	"""

	input_path = Path(input_path)
	output_path = Path(output_path)

	if not input_path.exists():
		raise FileNotFoundError(f"Input file not found: {input_path}")

	output_path.parent.mkdir(parents=True, exist_ok=True)

	with Image.open(input_path) as image:
		# For transparency, ensure RGBA.
		# (If the source has no alpha, this still produces a valid PNG.)
		if image.mode != "RGBA":
			image = image.convert("RGBA")
		image.save(output_path, format="PNG")


def main(argv: list[str] | None = None) -> int:
	import argparse

	parser = argparse.ArgumentParser(description="Convert a .webp image to .png (preserve alpha).")
	parser.add_argument("input", help="Input .webp path")
	parser.add_argument("output", help="Output .png path")
	args = parser.parse_args(argv)

	webp_to_png(args.input, args.output)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

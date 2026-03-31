import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data.utils import load_config
from src.main import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Wildfire Risk MVP pipeline."
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a custom config.yaml (default: config/config.yaml)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config) if args.config else load_config()
    output_path = run_pipeline(config)
    print(f"\nPipeline complete. Open your map:\n  {output_path}")


if __name__ == "__main__":
    main()

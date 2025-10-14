"""
Main entry point for Snake of Despair.
Launches the game with CLI argument parsing.
"""

import argparse
import sys
from typing import Optional

from .game import Game
from .config import Config


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Snake of Despair - A horror twist on Snake",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m snake_of_despair
  python -m snake_of_despair --seed 42 --reduced-scare
  python -m snake_of_despair --difficulty hard --window 1280x720
  python -m snake_of_despair --mute --debug
        """
    )
    
    parser.add_argument(
        "--seed", 
        type=int, 
        help="Random seed for deterministic gameplay"
    )
    parser.add_argument(
        "--reduced-scare", 
        action="store_true",
        help="Enable reduced scare mode for accessibility"
    )
    parser.add_argument(
        "--difficulty", 
        choices=["easy", "normal", "hard"],
        default="normal",
        help="Game difficulty level"
    )
    parser.add_argument(
        "--window", 
        type=str,
        default="960x720",
        help="Window size (WIDTHxHEIGHT)"
    )
    parser.add_argument(
        "--mute", 
        action="store_true",
        help="Disable all audio"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug overlay"
    )
    
    return parser.parse_args()


def parse_window_size(window_str: str) -> tuple[int, int]:
    """Parse window size string into width, height tuple."""
    try:
        width, height = map(int, window_str.split('x'))
        return width, height
    except ValueError:
        print(f"Invalid window size format: {window_str}. Use WIDTHxHEIGHT (e.g., 960x720)")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    try:
        args = parse_args()
        
        # Parse window size
        width, height = parse_window_size(args.window)
        
        # Create config
        config = Config(
            seed=args.seed,
            reduced_scare=args.reduced_scare,
            difficulty=args.difficulty,
            window_size=(width, height),
            mute=args.mute,
            debug=args.debug
        )
        
        # Create and run game
        game = Game(config)
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting game: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

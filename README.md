# Snake of Despair

A compact, high-tension horror twist on the classic Snake game with an adaptive "fear-injection" system that triggers screamers at peak tension moments, plus accessibility features for a "Reduced scare" mode.

## 🎮 Game Overview

**Snake of Despair** combines the familiar Snake gameplay with psychological horror elements. As you play, the game monitors your tension through various factors (proximity to walls, tail, speed, etc.) and triggers sudden audio/visual effects when tension peaks. The game includes comprehensive accessibility options to ensure it's playable by everyone.

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/snake-of-despair.git
   cd snake-of-despair
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```bash
   python -m snake_of_despair
   ```

### System Requirements

- **Python:** 3.11 or 3.12 (recommended)
- **OS:** Windows, macOS, or Linux
- **RAM:** 512MB minimum
- **Storage:** 50MB for game files

## 🎯 Gameplay

### Controls
- **Movement:** WASD or Arrow Keys
- **Pause:** ESC key
- **Menu Navigation:** Arrow Keys + Enter

### Game Loop
1. **Classic Snake:** Move around the grid, eat apples, grow longer
2. **Tension Building:** Risk factors increase tension meter
3. **Fear Injection:** High tension triggers sudden effects
4. **Survival:** Avoid collisions while managing fear

### Tension System
The game monitors several factors to build tension:
- **Wall Proximity:** Getting close to edges
- **Tail Proximity:** Nearly touching your own tail
- **Speed:** Moving faster increases risk
- **Score Streaks:** Consecutive apples without mistakes
- **Time Without Apple:** Long periods without food
- **Cornering:** Frequent direction changes

## ⚙️ Command Line Options

```bash
python -m snake_of_despair [options]

Options:
  --seed N                    Set random seed for deterministic gameplay
  --reduced-scare            Enable reduced scare mode for accessibility
  --difficulty {easy,normal,hard}  Set difficulty level
  --window WIDTHxHEIGHT      Set window size (default: 960x720)
  --mute                     Disable all audio
  --debug                    Enable debug overlay
```

### Examples
```bash
# Normal gameplay
python -m snake_of_despair

# Deterministic gameplay with reduced scare mode
python -m snake_of_despair --seed 42 --reduced-scare

# Hard difficulty with larger window
python -m snake_of_despair --difficulty hard --window 1280x720

# Silent debug mode
python -m snake_of_despair --mute --debug
```

## 🛡️ Accessibility Features

### Reduced Scare Mode
Enable with `--reduced-scare` or through the settings menu:

- **Volume Limits:** Caps audio volume and peak levels
- **Gentle Effects:** Replaces harsh screamers with mild notifications
- **Muted Colors:** Uses softer color palette
- **Longer Transitions:** Slower, gentler visual effects
- **Flash Reduction:** Limits bright flashes and strobing

### Content Warnings
The game includes warnings for:
- Horror content and jump scares
- Flashing lights (epilepsy warning)
- Sudden loud noises

### Accessibility Settings
- **High Contrast Mode:** Enhanced visibility
- **Large Text:** Bigger UI elements
- **Motion Reduction:** Minimizes camera shake and movement
- **Screen Reader Support:** Compatible with assistive technologies

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=snake_of_despair --cov-report=html

# Run specific test files
pytest tests/test_snake.py
pytest tests/test_tension.py
pytest tests/test_screamers.py
```

### Test Coverage
The test suite covers:
- **Snake Logic:** Movement, growth, collision detection
- **Tension System:** Contributions, decay, trigger policies
- **Screamer System:** Effect scheduling, cooldowns, safety
- **UI Components:** Menu navigation, settings
- **Accessibility:** Safety filters, reduced scare mode

## 📊 Tension Model & Trigger Policy

### Tension Calculation
The tension system uses weighted contributions from multiple sources:

```
Tension = Σ(Source_Value × Weight × Decay_Factor)
```

**Source Weights:**
- Wall Proximity: 2.0x
- Tail Proximity: 3.0x  
- Speed Factor: 1.0x
- Score Streak: 0.5x
- Time Without Apple: 0.3x
- Last Second Turn: 2.0x
- Cornering: 1.5x

### Trigger Policy
Screamers trigger when:
1. Tension exceeds dynamic threshold (75% + jitter)
2. Cooldown period has elapsed (10 seconds)
3. Rate limit not exceeded (3 per minute)

### Decay System
Tension naturally decays over time:
- Base decay rate: 0.5 points/second
- Faster decay during calm periods
- Slower decay during high tension

## 🎨 Asset Management

### Placeholder Assets
The game generates fallback assets if files are missing:

**Audio Assets (`assets/audio/`):**
- `scream.wav` - Screamer audio effect
- `beep.wav` - Notification sound
- `tension.wav` - Tension building sound

**Image Assets (`assets/images/`):**
- `flash_overlay.png` - Flash effect overlay
- `screamer_image.png` - Screamer visual effect
- `overlay.png` - General overlay effect

**Video Assets (`assets/video/`):**
- `screamer_clip.mp4` - Short screamer video
- `tension_build.mp4` - Tension building sequence

### Asset Requirements
- **Audio:** WAV/OGG/MP3, 22050Hz+, <2 seconds
- **Images:** PNG with transparency, 100x100 to 400x400px
- **Video:** MP4/AVI, 1-3 seconds, <5MB

### Licensing
All placeholder assets are generated at runtime and are safe to use. For production, replace with properly licensed media files.

## 🐛 Known Limitations

### Performance
- **Frame Rate:** Target 60 FPS on modest hardware
- **Memory Usage:** ~100MB typical usage
- **CPU Usage:** Single-threaded, moderate CPU usage

### Platform Limitations
- **Colab:** Pygame windows not supported in Google Colab
- **Headless:** Requires display for full functionality
- **Mobile:** Not optimized for touch controls

### Audio/Video
- **Format Support:** Limited to common formats
- **Synchronization:** Audio/video sync may vary by system
- **Latency:** Audio latency depends on system configuration

## 🔧 Development

### Project Structure
```
snake_of_despair/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point
├── game.py              # Main game loop and state machine
├── snake.py             # Snake model and grid logic
├── apple.py             # Apple spawn and management
├── tension.py           # Tension meter and contributions
├── screamers.py         # Fear injection system
├── ui.py                # Menus, HUD, and overlays
├── assets.py            # Asset loading and fallbacks
├── config.py            # Configuration and constants
├── colors.py            # Color management
├── safety.py            # Accessibility and safety features
├── logging_utils.py     # Event logging and telemetry
└── telemetry.py         # Session metrics collection

tests/
├── test_snake.py        # Snake logic tests
├── test_tension.py      # Tension system tests
└── test_screamers.py   # Screamer system tests

assets/
├── audio/              # Audio files
├── images/             # Image files
└── video/              # Video files
```

### Adding New Features
1. **Core Logic:** Add to appropriate module (snake.py, tension.py, etc.)
2. **UI Elements:** Add to ui.py or create new UI module
3. **Effects:** Extend screamers.py with new effect types
4. **Accessibility:** Update safety.py with new safety features
5. **Tests:** Add comprehensive tests for new functionality

### Code Style
- **Formatting:** Use `black` for code formatting
- **Linting:** Use `flake8` for style checking
- **Type Hints:** Use `mypy` for type checking
- **Documentation:** Include docstrings for all public functions

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests before committing
pytest

# Format code
black snake_of_despair/ tests/

# Type check
mypy snake_of_despair/
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Kaulan Serzhanuly** - *kaulan.serzhanuly@sjsu.edu*
- **Danila Kharitonenkov** - *danila.kharitonenkov@sjsu.edu*

**Course:** CS 122 (Fall 2025)  
**Institution:** San Jose State University

## 🙏 Acknowledgments

- **Pygame Community** for the excellent game development framework
- **Open Source Contributors** for inspiration and tools
- **Accessibility Advocates** for guidance on inclusive design
- **CS 122 Instructors** for project guidance and feedback

## 📚 Additional Resources

### Documentation
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Python Game Development](https://realpython.com/pygame-a-primer/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Community
- [Pygame Discord](https://discord.gg/pygame)
- [Python Game Development Reddit](https://reddit.com/r/pygame)
- [Game Development Stack Overflow](https://stackoverflow.com/questions/tagged/pygame)

---

**⚠️ Content Warning:** This game contains horror elements including sudden sounds, visual effects, and jump scares. Use reduced scare mode if you have sensitivity to these elements.

**🎮 Enjoy the game and remember: The real horror is losing your high score!**

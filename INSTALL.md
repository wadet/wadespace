# Wade Space - Installation Guide

## System Requirements

- Python 3.8 or higher
- pip package manager
- Virtual environment support

## Installation Steps

### 1. Create Virtual Environment

```bash
cd /home/wadet/workspace/wadespace
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python3 -c "from src.game_engine import GameEngine; print('✓ Installation successful')"
```

## Running the Game

### Start the Game

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the game
python -m src.main
```

### Run Tests

```bash
source venv/bin/activate
python -m pytest tests/test_core.py -v
```

## Required Packages

The game requires only these packages:
- **numpy** >= 1.21.0 - Numerical computing
- **python-dotenv** >= 1.0.0 - Environment configuration
- **pytest** >= 7.0.0 - Testing framework

## Optional Packages (Future Phases)

For upcoming features:
- **pygame** - Graphics UI (Phase 2)
- **openai** - AI integration (Phase 3)

These can be added when needed using:
```bash
pip install pygame openai
```

## Troubleshooting

### Virtual Environment Not Activating

Make sure you're in the correct directory and run:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Package Installation Fails

Try upgrading pip first:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Import Errors When Running Game

Ensure your virtual environment is activated. You should see `(venv)` at the start of your terminal prompt.

### Tests Won't Run

Make sure pytest is installed:
```bash
pip install pytest
python -m pytest tests/test_core.py -v
```

## Next Steps

1. Read `GETTING_STARTED.md` for gameplay guide
2. Read `README.md` for feature overview
3. Read `ARCHITECTURE.md` for technical details
4. Run `python -m src.main` to play!

---

**Status**: ✅ Ready to play!

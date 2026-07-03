# 🌌 Async Space Action Game (TUI)
A fast-paced retro space arcade game built entirely inside the terminal. This project showcases cooperative multitasking 
and asynchronous programming in Python using native coroutines (generators driven by hand-crafted event-loops) inside a 
curses text interface.


## 📌 Table of Contents
- [⚙️ Tech Stack](#-tech-stack)
- [📁 Project Structure](#-project-structure)
- [🛠️ Installation & Setup](#-installation--setup)
- [🚀 Quick Start Guide](#-quick-start-guide)
- [🎮 Controls](#-controls)


## ⚙️ Tech Stack
- Language: Python 3.10+
- TUI Framework: Native `curses` library
- Async Model: Cooperative multitasking via Python coroutines (async / await syntax)
- Operating System: Linux, macOS, or Windows (via WSL 2)


## 📁 Project Structure
```text
.
├── frames/              # Directory holding raw ASCII art animations
│   ├── obstacles/       # ASCII art of obstacles
│   └── ship/            # Spaceship engine flame animation frames   
├── curses_tools.py      # Core text-processing tools (drawing frames, boundaries)
├── controls.py          # Non-blocking user keyboard inputs configuration
├── animations.py        # Asynchronous game entities behaviors (stars, ship, fire)
├── physics.py           # Handles spaceship inertia, deceleration, and smooth motion physics
└── main.py              # Main game setup, state management, and orchestration loop
```


## 🛠️ Installation & Setup
### 1. Clone the repository:
```bash
git clone https://github.com/VictoriaL-dev/terminal-space-game.git
cd terminal-space-game
```

### 2. Set up a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate # on Windows
source venv/bin/activate # on Linux / macOS
```

### 3. Platform-specific setup:
#### Linux / macOS:
You are good to go! Python's standard library includes the `curses` module by default.

#### Windows:
> ⚠️ **Note:** The native `curses` module is not supported natively on Windows.

To play this game on Windows, you must choose one of the following options:
1) **Run inside [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install) (Recommended):**<br>
Open your Linux shell within Windows Subsystem for Linux and execute the project there.
2) **Install [Windows Port](https://pypi.org/project/windows-curses/):**<br> 
Alternatively, you can patch your Windows python environment by installing the unofficial `windows-curses` port:
    ```bash
    pip install windows-curses
    ```


## 🚀 Quick Start Guide
#### 1. Open your terminal window.
#### 2. Maximize your terminal size or ensure it is open wide enough to fit the canvas and the ship frames.
#### 3. Launch the game by executing the main script:
```bash
python3 main.py
```


## 🎮 Controls
- `▲` / `▼` / `◄` / `►` (Arrow Keys): Fly your spaceship smoothly across the night sky.
- `Ctrl + C`: Gracefully quit the game loop and return terminal behavior back to normal.

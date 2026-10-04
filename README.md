# Kitchen Rush

A colorful Python desktop cooking game: three stations, hungry guests, perfect serves, streak bonuses, and a kitchen that improves after every shift. Original food illustrations are drawn in code using Tkinter Canvas. No downloads, accounts, paid APIs, or external artwork are needed.

## Play

Install Python 3.10 or newer with Tkinter, then run:

```bash
python3 game.py
```

On Windows, use `py game.py`. On this Mac, double-click `Play Kitchen Rush.command`, or open `game.py` in your Python IDE and run it. Keep the project files together.

Tkinter comes with the standard Python installers for macOS and Windows. On Linux it may need your distribution's `python3-tk` package. Check availability with `python3 -m tkinter`.

## The rules

- Open the kitchen. Your first shift lasts 70 seconds.
- Guests arrive with a dish request and a patience bar. Match the tickets to your three stations.
- Click a station (or press 1, 2, 3) to begin cooking.
- When it turns green, tap it again to serve the matching guest with the shortest remaining wait.
- Serve within the first 1.7 seconds of readiness for a perfect bonus. Fresh serves and patient guests earn extra tips.
- Keep serving to build a streak and increase the score multiplier, up to 2×.
- Food left ready for too long becomes overdone. Tap to clear the station, then tap again to restart. Overdone food resets your streak but does not cost reputation.
- A guest who runs out of patience leaves, costing one reputation star and resetting your streak. Lose all five and the run ends.
- After each completed shift, buy upgrades with earned coins. Quick hands reduces cook time; Cozy corner adds patience; Warming shelf extends the ready window.
- Start the next shift for faster guest arrivals and one restored reputation star. Unfinished orders at closing do not count as missed guests.

## Controls

| Action | Control |
|---|---|
| Burger station | Click / 1 / A |
| Noodle station | Click / 2 / S |
| Salad station | Click / 3 / D |
| Pause / resume | P / Space / Escape |
| Instructions | H / How to play button |
| Toggle cue sounds | M / Sound button |
| Start / next shift / retry | Enter |

The game automatically pauses when its window loses focus. Instructions also freeze gameplay. Sound cues use your operating system's bell, so their sound/volume depend on system settings.

## Records and saves

Personal best score, furthest shift and most dishes served are stored in `saves/records.json`. Records are saved after shifts, game over, returning to the menu, and closing the window. A saved record is not a resumable run: starting from the menu starts a fresh kitchen. Saves are local and excluded from Git.

## Test

```bash
python3 -m unittest discover -s tests -v
```

The tests cover cooking, timing, stale food, urgent-order selection, reputation, shifts, upgrades, scoring and record persistence. They do not open the desktop window. The game is designed for a keyboard/mouse and a window at least 880×620.

## Project map

- `engine.py`: game rules and simulation; no GUI imports.
- `game.py`: Tkinter Canvas drawings, mouse/keyboard input, animation, menus and pause.
- `progress.py`: resilient local record storage.
- `tests/`: deterministic rule tests.
- `LEARNING_GUIDE.md`: how to rebuild it from Python fundamentals.

This is a desktop game, not a browser game. GitHub visitors can download the source and run it with Python. Standalone signed Windows/macOS executables would be a separate packaging step; none are included or claimed tested here.

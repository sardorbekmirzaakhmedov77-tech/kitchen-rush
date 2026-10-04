# From Python lessons to a playable game

Kitchen Rush uses concepts from Angela Yu's Python course: functions, loops, dictionaries, classes, Tkinter, events, file handling and exceptions. The polish comes from combining them into a game, not from a special AI framework.

## Rebuild it in small steps

1. Make a Tkinter window with a Canvas and draw three rectangles for stations.
2. Bind a click to print the chosen station. Add keys 1, 2 and 3.
3. Create a Station class with idle, cooking, ready and burned states.
4. Use `root.after` to update the screen without blocking the event loop. Never use `sleep` in a button callback.
5. Use `time.monotonic` to measure elapsed time. A recipe should take the same time on different computers.
6. Add Order objects with a dish and patience value. Draw a bar that shrinks as patience decreases.
7. Match ready dishes to orders. Add coins, points and reputation.
8. Add shifts and upgrade levels. Keep the game rules in a module independent of the screen.
9. Store personal records in JSON. Handle missing or broken files gracefully.
10. Add color, food drawings, animation, sound cues and readable instructions.
11. Test the rules without running the GUI. A seeded random generator makes tests repeatable.

## Ideas to learn from the code

| Python concept | Example |
|---|---|
| Dictionaries | Recipe cook times, dish prices and upgrade definitions |
| Classes / dataclasses | Kitchen, Station and Order |
| State machines | Cooking → ready → served or burned |
| List processing | Choosing the most urgent matching guest |
| Callbacks | Buttons and keyboard bindings |
| Event loop | `root.after(33, self.loop)` |
| Time | A bounded simulation update with a monotonic clock |
| File handling | Atomic replacement of the JSON record file |
| Testing | Temporary folders and deterministic game scenarios |

The course gives you the foundations, but game balancing, responsive Canvas layout, simulation testing and atomic file replacement are extra practice. Read one function, change one rule, and play the result.

Good first modifications: add a fourth dish, a practice shift with unlimited patience, a color theme, or a new upgrade. Start with the engine tests before changing the interface.

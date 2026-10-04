#!/bin/zsh
cd -- "${0:A:h}"
python3 game.py
if [[ $? -ne 0 ]]; then
  echo "The game could not start. Check that Python 3 and Tkinter are installed."
  read -r "reply?Press Return to close."
fi

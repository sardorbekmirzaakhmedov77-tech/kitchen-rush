"""Headless render smoke checks: exercise every screen without opening a window."""
import unittest
from unittest.mock import MagicMock
from engine import Kitchen
from game import GameApp

class ScreenTests(unittest.TestCase):
    def test_all_screens_accept_each_station_state(self):
        app=GameApp.__new__(GameApp)
        app.canvas=MagicMock(); app.root=MagicMock(); app.scale=1
        app.hover=(-1,-1); app.buttons=[]; app.sound=True
        app.game=Kitchen(42); app.clock=1; app.notice=''; app.notice_until=0
        app.records={'score':100,'shift':2,'served':3}; app.particles=[]
        app.background(); app.draw_menu()
        for state in ('idle','cooking','ready','burned'):
            for s in app.game.stations:
                s.phase=state; s.duration=5; s.elapsed=1
            app.draw_game()
        app.draw_break(); app.draw_over(); app.draw_overlay(); app.draw_overlay(True)
        self.assertTrue(app.canvas.create_text.called)

if __name__=='__main__': unittest.main()

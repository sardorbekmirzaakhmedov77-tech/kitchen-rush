import tempfile
import unittest
from pathlib import Path
from engine import Kitchen, COOK_TIME
import progress

class KitchenTests(unittest.TestCase):
    def setUp(self): self.g = Kitchen(seed=42)
    def ready(self, station=0):
        self.g.work(station); self.g.tick(self.g.stations[station].duration+.01)
    def test_start_has_two_orders_and_three_stations(self):
        self.assertEqual(len(self.g.orders),2); self.assertEqual(len(self.g.stations),3)
        self.assertEqual(self.g.reputation,5)
    def test_cooking_and_perfect_serve(self):
        self.ready(); self.assertEqual(self.g.stations[0].phase,'ready')
        self.assertTrue(self.g.work(0)); self.assertEqual(self.g.served,1)
        self.assertGreater(self.g.score,100); self.assertGreater(self.g.wallet,24)
        self.assertEqual(self.g.stations[0].phase,'idle')
        self.assertEqual(self.g.events[-1][0],'perfect')
    def test_early_tap_does_not_serve(self):
        self.g.work(0); self.g.tick(1); self.assertFalse(self.g.work(0)); self.assertEqual(self.g.served,0)
    def test_no_matching_order(self):
        self.ready(1); self.g.orders=[o for o in self.g.orders if o.dish!='noodles']
        self.assertFalse(self.g.work(1)); self.assertEqual(self.g.stations[1].phase,'ready')
    def test_burn_and_clear(self):
        self.ready(); self.g.tick(self.g.ready_window+.1)
        self.assertEqual(self.g.stations[0].phase,'burned'); self.assertEqual(self.g.burned,1)
        self.g.work(0); self.assertEqual(self.g.stations[0].phase,'idle')
        self.g.work(0); self.assertEqual(self.g.stations[0].phase,'cooking')
    def test_missed_guest_costs_reputation(self):
        self.g.orders[0].remaining=.2; self.g.combo=4; self.g.tick(.3)
        self.assertEqual(self.g.reputation,4); self.assertEqual(self.g.missed,1); self.assertEqual(self.g.combo,0)
    def test_serve_most_urgent_match(self):
        self.g.add_order('burger'); urgent=self.g.orders[-1]; urgent.remaining=7
        self.ready(); self.g.work(0)
        self.assertNotIn(urgent,self.g.orders); self.assertTrue(any(o.dish=='burger' for o in self.g.orders))
    def test_end_when_reputation_empty(self):
        self.g.reputation=1; self.g.orders[0].remaining=.1; self.g.tick(1)
        self.assertEqual(self.g.state,'over'); remaining=self.g.remaining
        self.g.tick(10); self.assertEqual(self.g.remaining,remaining)
        self.assertFalse(self.g.work(0))
    def test_shift_break_and_recovery(self):
        self.g.remaining=.2; self.g.reputation=3; self.g.tick(.3)
        self.assertEqual(self.g.state,'break'); self.assertEqual(self.g.orders,[])
        self.assertTrue(self.g.next_shift()); self.assertEqual(self.g.shift,2)
        self.assertEqual(self.g.reputation,4); self.assertEqual(len(self.g.orders),2)
    def test_upgrade_payment_and_limit(self):
        self.g.wallet=1000; self.assertFalse(self.g.buy('speed'))
        self.g.state='break'; old=self.g.wallet; cost=self.g.cost('speed')
        self.assertTrue(self.g.buy('speed')); self.assertEqual(self.g.wallet,old-cost)
        self.g.buy('speed'); self.g.buy('speed'); old=self.g.wallet
        self.assertFalse(self.g.buy('speed')); self.assertEqual(self.g.wallet,old)
    def test_upgrade_effects(self):
        self.g.levels=dict(speed=2,patience=2,window=2)
        self.g.work(0); self.assertAlmostEqual(self.g.stations[0].duration,COOK_TIME['burger']*.76)
        self.g.add_order('burger'); self.assertEqual(self.g.orders[-1].patience,46)
        self.assertEqual(self.g.ready_window,8)
    def test_cannot_buy_without_money(self):
        self.g.state='break'; self.assertFalse(self.g.buy('window')); self.assertEqual(self.g.levels['window'],0)
    def test_max_five_orders(self):
        for i in range(20): self.g.add_order()
        self.assertEqual(len(self.g.orders),5)
    def test_combo_multiplier(self):
        self.ready(); self.g.work(0); self.ready(2); self.g.work(2)
        self.assertEqual(self.g.combo,2); self.assertEqual(self.g.best_combo,2)
    def test_bounded_time_step_equivalence(self):
        a=Kitchen(1); b=Kitchen(1); a.work(0); b.work(0)
        a.tick(8)
        for _ in range(160): b.tick(.05)
        self.assertEqual(a.stations[0].phase,b.stations[0].phase)
        self.assertAlmostEqual(a.remaining,b.remaining)
        self.assertEqual([o.dish for o in a.orders],[o.dish for o in b.orders])
    def test_record_round_trip_and_high_score(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'nested'/'records.json'
            self.g.score=400; self.g.shift=3; self.assertTrue(progress.save(self.g,path))
            self.g.score=10; self.g.shift=1; progress.save(self.g,path)
            self.assertEqual(progress.load(path)['score'],400); self.assertEqual(progress.load(path)['shift'],3)
    def test_corrupt_record_is_recoverable(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'records.json'; path.write_text('not json')
            self.assertEqual(progress.load(path)['score'],0)
            self.assertTrue(progress.save(self.g,path))
    def test_invalid_station_ignored(self):
        self.assertFalse(self.g.work(-1)); self.assertFalse(self.g.work(3))

if __name__=='__main__': unittest.main()

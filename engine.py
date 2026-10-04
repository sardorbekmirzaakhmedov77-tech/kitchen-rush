"""Kitchen Rush rules, independent of graphics. All time is simulation time."""
from dataclasses import dataclass
import random

DISHES = ('burger', 'noodles', 'salad')
LABELS = {'burger': 'Sunset burger', 'noodles': 'Golden noodles', 'salad': 'Garden bowl'}
COOK_TIME = {'burger': 5.0, 'noodles': 4.2, 'salad': 3.4}
PRICES = {'burger': 24, 'noodles': 21, 'salad': 18}
UPGRADES = {'speed': ('Quick hands', 'Prep time −12% per level', 65),
            'patience': ('Cozy corner', 'Guests wait 5s longer per level', 55),
            'window': ('Warming shelf', 'Ready window +1.5s per level', 50)}

@dataclass
class Order:
    id: int
    dish: str
    customer: str
    patience: float
    remaining: float

@dataclass
class Station:
    dish: str
    phase: str = 'idle'
    elapsed: float = 0.0
    duration: float = 0.0

class Kitchen:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.shift = 1
        self.wallet = 0
        self.score = 0
        self.served = 0
        self.missed = 0
        self.burned = 0
        self.combo = 0
        self.best_combo = 0
        self.reputation = 5
        self.levels = dict.fromkeys(UPGRADES, 0)
        self.stations = [Station(d) for d in DISHES]
        self.orders = []
        self.serial = 0
        self.events = []
        self.state = 'playing'
        self.remaining = 70.0
        self.spawn_in = 5.0
        self.shift_served = 0
        self.shift_cash = 0
        self.shift_missed = 0
        self.add_order('burger')
        self.add_order('salad')

    def emit(self, kind, text):
        self.events.append((kind, text))

    def add_order(self, dish=None):
        if len(self.orders) >= 5:
            return
        self.serial += 1
        patience = max(19, 36 - (self.shift-1)*2) + self.levels['patience']*5
        self.orders.append(Order(self.serial, dish or self.rng.choice(DISHES),
            self.rng.choice(['Milo', 'Luna', 'Kai', 'Nora', 'Theo', 'Jules', 'Alex', 'Remy']), patience, patience))

    @property
    def ready_window(self):
        return 5 + self.levels['window']*1.5

    def work(self, index):
        if self.state != 'playing' or index not in range(3):
            return False
        station = self.stations[index]
        if station.phase in ('idle', 'burned'):
            if station.phase == 'burned':
                station.phase = 'idle'; station.elapsed = 0
                self.emit('info', 'Station cleared. Tap again to cook.')
                return True
            station.phase = 'cooking'; station.elapsed = 0
            station.duration = COOK_TIME[station.dish] * (1 - .12*self.levels['speed'])
            self.emit('info', LABELS[station.dish] + ' is on the way!')
            return True
        if station.phase == 'ready':
            matches = [o for o in self.orders if o.dish == station.dish]
            if not matches:
                self.emit('info', 'No guest needs this dish yet. Keep it warm!')
                return False
            order = min(matches, key=lambda o: o.remaining)
            fresh = station.elapsed <= 1.7
            self.combo += 1; self.best_combo = max(self.best_combo, self.combo)
            multiplier = 1 + min(self.combo-1, 4)*.25
            tip = round(10 * order.remaining/order.patience) + (5 if fresh else 0)
            coins = PRICES[station.dish] + tip
            points = round((100 + tip*3)*multiplier)
            self.wallet += coins; self.shift_cash += coins; self.score += points
            self.served += 1; self.shift_served += 1
            self.orders.remove(order)
            station.phase = 'idle'; station.elapsed = 0
            self.emit('perfect' if fresh else 'serve',
                      f'{"PERFECT! " if fresh else "Served! "}+{coins} coins · +{points} points')
            return True
        self.emit('info', 'Still cooking… wait for the green light.')
        return False

    def tick(self, dt):
        if self.state != 'playing' or dt <= 0:
            return
        # Process bounded steps so large updates behave like ordinary frames.
        while dt > 0 and self.state == 'playing':
            step = min(dt, .05, self.remaining)
            dt -= step
            self.remaining = max(0, self.remaining-step)
            for station in self.stations:
                if station.phase == 'cooking':
                    station.elapsed += step
                    if station.elapsed >= station.duration:
                        station.elapsed -= station.duration
                        station.phase = 'ready'
                        self.emit('ready', LABELS[station.dish] + ' is ready — serve it!')
                elif station.phase == 'ready':
                    station.elapsed += step
                    if station.elapsed >= self.ready_window:
                        station.phase = 'burned'; self.burned += 1; self.combo = 0
                        self.emit('burn', 'Oops, overdone! Tap the station to clear it.')
            for order in self.orders[:]:
                order.remaining -= step
                if order.remaining <= 0:
                    self.orders.remove(order)
                    self.missed += 1; self.shift_missed += 1
                    self.reputation -= 1; self.combo = 0
                    self.emit('miss', order.customer + ' left hungry. You can turn this around!')
            if self.reputation <= 0:
                self.reputation = 0; self.state = 'over'
                self.emit('over', 'Kitchen closed. Every great chef starts somewhere.')
                break
            self.spawn_in -= step
            if self.spawn_in <= 0 and self.remaining > 10:
                self.add_order()
                self.spawn_in = max(3.6, 7.6-self.shift*.5) + self.rng.uniform(-.8,.8)
            if self.remaining <= .000001:
                self.remaining = 0; self.state = 'break'
                self.orders.clear()
                for s in self.stations: s.phase = 'idle'; s.elapsed = 0
                self.emit('break', 'Shift complete! Take a breath and upgrade your kitchen.')

    def cost(self, key):
        return UPGRADES[key][2] + self.levels[key]*40

    def buy(self, key):
        if self.state != 'break' or key not in UPGRADES or self.levels[key] >= 3:
            return False
        cost = self.cost(key)
        if self.wallet < cost:
            self.emit('info', 'Save a few more coins for this upgrade.')
            return False
        self.wallet -= cost; self.levels[key] += 1
        self.emit('buy', UPGRADES[key][0] + ' upgraded!')
        return True

    def next_shift(self):
        if self.state != 'break': return False
        self.shift += 1; self.remaining = 70; self.spawn_in = 4
        self.shift_served = self.shift_cash = self.shift_missed = 0
        self.reputation = min(5, self.reputation+1)
        self.state = 'playing'
        self.add_order(); self.add_order()
        self.emit('info', 'New shift! One reputation star restored.')
        return True

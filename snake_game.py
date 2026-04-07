from kivy.uix.widget import Widget
from kivy.graphics import Line, Ellipse, Color, Rectangle
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.core.window import Window
import random
import math

class SnakeGame(Widget):
    grid_size = NumericProperty(20)
    speed = NumericProperty(0.08)
    
    BRAINROT_MEMES = [
        "🧠 OK", "💀 DEAD", "🔥 SIGMA", "🤡 NPC", "🌀 SPINNING",
        "⚡ FRIED", "🎪 CIRCUS", "💩 SLOP", "👁️ UNHINGED", "🎭 PSYCHO",
        "🚀 MARS", "🌊 SLOP OCEAN", "😵 VERTIGO", "🎸 BOTTOM", "🔮 CURSED"
    ]
    
    POWER_UPS = {
        "SPEED": {"mult": 2.0, "color": (1, 1, 0), "label": "⚡"},
        "SLOW": {"mult": 0.3, "color": (0.5, 0.5, 1), "label": "🐢"},
        "GHOST": {"ghost": True, "color": (1, 0, 1), "label": "👻"},
        "POINTS": {"mult": 3, "color": (1, 0.5, 0), "label": "💰"},
        "CHAOS": {"chaos": True, "color": (1, 0, 0), "label": "🌀"}
    }
    
    def __init__(self, mode="CLASSIC", ad_helper=None, **kwargs):
        super().__init__(**kwargs)
        self.size = Window.size
        self.mode = mode
        self.ad_helper = ad_helper
        
        # Game state
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.spawn_food()
        self.power_ups = []
        self.enemies = []
        self.walls = []
        self.game_over = False
        
        # Score
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.brain_damage = 0
        
        # Ad tracking
        self.moves_since_ad = 0
        self.ad_cooldown = 50
        
        # Rendering
        self.meme_counter = 0
        self.screen_shake = 0
        self.particles = []
        self.active_effects = {}
        
        # Time attack
        self.time_left = 60
        
        # Mode setup
        self._init_mode()
        
        # Input
        Window.bind(on_keyboard=self.on_keyboard)
        Window.bind(on_touch_down=self.on_touch_down)
        Window.bind(on_touch_move=self.on_touch_move)
        
        self.touch_start = None
        
        # Game loop
        Clock.schedule_interval(self.update, self.speed)
        Clock.schedule_interval(self._render, 0.016)
    
    def _init_mode(self):
        if self.mode == "CLASSIC":
            self.speed = 0.08
            self.powerup_chance = 0.003
        elif self.mode == "TIME_ATTACK":
            self.speed = 0.1
            Clock.schedule_interval(self._tick_time, 1)
            self.powerup_chance = 0.008
        elif self.mode == "CHAOS":
            self.speed = 0.06
            self.powerup_chance = 0.025
        elif self.mode == "SURVIVAL":
            self.speed = 0.1
            self.powerup_chance = 0.001
            self._gen_walls()
            self._spawn_enemy()
    
    def _tick_time(self, dt):
        if not self.game_over:
            self.time_left -= 1
            if self.time_left <= 0:
                self.game_over = True
    
    def _gen_walls(self):
        max_x = int(self.width // self.grid_size)
        max_y = int(self.height // self.grid_size)
        
        for _ in range(random.randint(4, 6)):
            wx = random.randint(5, max_x - 5)
            wy = random.randint(5, max_y - 5)
            length = random.randint(4, 7)
            direction = random.choice([(1, 0), (0, 1)])
            
            for i in range(length):
                x = wx + direction[0] * i
                y = wy + direction[1] * i
                if 0 <= x < max_x and 0 <= y < max_y and (x, y) not in self.snake:
                    self.walls.append((x, y))
    
    def _spawn_enemy(self):
        max_x = int(self.width // self.grid_size)
        max_y = int(self.height // self.grid_size)
        
        for _ in range(min(len(self.enemies) + 1, 3)):
            pos = self._random_free_pos()
            if pos:
                self.enemies.append({
                    "pos": list(pos),
                    "dir": random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]),
                    "counter": 0
                })
    
    def _random_free_pos(self):
        max_x = int(self.width // self.grid_size)
        max_y = int(self.height // self.grid_size)
        
        for _ in range(10):
            pos = (random.randint(0, max_x - 1), random.randint(0, max_y - 1))
            if pos not in self.snake and pos != self.food and pos not in self.walls:
                return pos
        return None
    
    def on_touch_down(self, touch):
        self.touch_start = (touch.x, touch.y)
        return True
    
    def on_touch_move(self, touch):
        if not self.touch_start:
            return True
        
        dx = touch.x - self.touch_start[0]
        dy = touch.y - self.touch_start[1]
        
        if abs(dx) > abs(dy) and abs(dx) > 40:
            new_dir = (1, 0) if dx > 0 else (-1, 0)
            if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
                self.next_direction = new_dir
                self.touch_start = (touch.x, touch.y)
        elif abs(dy) > abs(dx) and abs(dy) > 40:
            new_dir = (0, 1) if dy > 0 else (0, -1)
            if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
                self.next_direction = new_dir
                self.touch_start = (touch.x, touch.y)
        
        return True
    
    def on_keyboard(self, window, key, scancode, codepoint, modifier):
        key_map = {273: (0, 1), 274: (0, -1), 275: (1, 0), 276: (-1, 0)}
        
        if scancode in key_map:
            new_dir = key_map[scancode]
            if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
                self.next_direction = new_dir
            return True
        return False
    
    def spawn_food(self):
        pos = self._random_free_pos()
        return pos if pos else (5, 5)
    
    def update(self, dt):
        if self.game_over:
            return
        
        # Check for ad display
        self.moves_since_ad += 1
        if self.moves_since_ad >= self.ad_cooldown and self.ad_helper:
            self.ad_helper.show_interstitial()
            self.moves_since_ad = 0
        
        # Update enemies
        if self.mode == "SURVIVAL":
            for enemy in self.enemies:
                enemy["counter"] += 1
                if enemy["counter"] > 12:
                    enemy["dir"] = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                    enemy["counter"] = 0
                
                max_x = int(self.width // self.grid_size)
                max_y = int(self.height // self.grid_size)
                nx = (enemy["pos"][0] + enemy["dir"][0]) % max_x
                ny = (enemy["pos"][1] + enemy["dir"][1]) % max_y
                enemy["pos"] = [nx, ny]
                
                if tuple(enemy["pos"]) == self.snake[0]:
                    self.game_over = True
                    return
        
        self.meme_counter += 1
        self.brain_damage = min(100, self.brain_damage + random.choice([0, 0, 0, 1]))
        
        # Power-up spawn
        if random.random() < self.powerup_chance:
            pos = self._random_free_pos()
            if pos:
                self.power_ups.append({
                    "pos": pos,
                    "type": random.choice(list(self.POWER_UPS.keys()))
                })
        
        # Move
        self.direction = self.next_direction
        
        if self.active_effects.get("chaos"):
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        
        # Adjust speed based on effects
        current_speed = self.speed
        if "speed_mult" in self.active_effects:
            current_speed /= self.active_effects["speed_mult"]
        
        head_x, head_y = self.snake[0]
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]
        
        max_x = int(self.width // self.grid_size)
        max_y = int(self.height // self.grid_size)
        
        # Ghost mode wraps
        if self.active_effects.get("ghost"):
            new_x = new_x % max_x
            new_y = new_y % max_y
        else:
            if new_x < 0 or new_x >= max_x or new_y < 0 or new_y >= max_y:
                self.game_over = True
                return
        
        # Wall collision
        if (new_x, new_y) in self.walls:
            self.game_over = True
            return
        
        # Self collision
        if (new_x, new_y) in self.snake[1:]:
            self.game_over = True
            return
        
        self.snake.insert(0, (new_x, new_y))
        
        # Food
        if (new_x, new_y) == self.food:
            mult = self.active_effects.get("points_mult", 1)
            self.score += int(10 * mult)
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self._particles((new_x, new_y), (1, 0.5, 0))
            self.food = self.spawn_food()
        else:
            self.snake.pop()
            self.combo = 0
        
        # Power-ups
        for pu in self.power_ups[:]:
            if (new_x, new_y) == pu["pos"]:
                self._activate_pu(pu["type"])
                self.power_ups.remove(pu)
        
        self.screen_shake = max(0, self.screen_shake - 0.15)
        
        # Clean particles
        for p in self.particles[:]:
            p["age"] += dt
            if p["age"] > 0.6:
                self.particles.remove(p)
    
    def _activate_pu(self, ptype):
        if ptype not in self.POWER_UPS:
            return
        
        pu = self.POWER_UPS[ptype]
        self.screen_shake = 8
        
        duration = 10  # seconds
        
        if ptype == "SPEED":
            self.active_effects["speed_mult"] = 2.0
            Clock.schedule_once(lambda dt: self.active_effects.pop("speed_mult", None), duration)
        elif ptype == "SLOW":
            self.active_effects["speed_mult"] = 0.3
            Clock.schedule_once(lambda dt: self.active_effects.pop("speed_mult", None), duration)
        elif ptype == "GHOST":
            self.active_effects["ghost"] = True
            Clock.schedule_once(lambda dt: self.active_effects.pop("ghost", None), duration)
        elif ptype == "POINTS":
            self.active_effects["points_mult"] = 3
            Clock.schedule_once(lambda dt: self.active_effects.pop("points_mult", None), duration)
        elif ptype == "CHAOS":
            self.active_effects["chaos"] = True
            Clock.schedule_once(lambda dt: self.active_effects.pop("chaos", None), duration)
        
        self._particles(self.snake[0], pu["color"], 12)
    
    def _particles(self, pos, color, count=8):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 4)
            self.particles.append({
                "pos": [pos[0] * self.grid_size, pos[1] * self.grid_size],
                "vel": (math.cos(angle) * speed, math.sin(angle) * speed),
                "color": color,
                "age": 0,
                "size": random.uniform(2, 6)
            })
    
    def get_brain_status(self):
        if self.brain_damage >= 90:
            status = "💀"
        elif self.brain_damage >= 75:
            status = "🌀"
        elif self.brain_damage >= 50:
            status = "🔥"
        elif self.brain_damage >= 25:
            status = "⚡"
        else:
            status = "🧠"
        
        if self.mode == "TIME_ATTACK":
            return f"{status} {self.time_left}s"
        
        return status
    
    def _render(self, *args):
        self.canvas.clear()
        
        with self.canvas:
            Color(0.04, 0.04, 0.06)
            Rectangle(size=self.size, pos=self.pos)
            
            shake = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
            
            # Grid
            Color(0.12, 0.12, 0.16)
            for i in range(0, int(self.width), int(self.grid_size)):
                Line(points=[i + shake, 0, i + shake, self.height], width=0.3)
            for i in range(0, int(self.height), int(self.grid_size)):
                Line(points=[0, i + shake, self.width, i + shake], width=0.3)
            
            # Walls
            if self.walls:
                Color(0.4, 0.15, 0.15)
                for wall in self.walls:
                    wx = wall[0] * self.grid_size + shake
                    wy = wall[1] * self.grid_size + shake
                    Rectangle(pos=(wx, wy), size=(self.grid_size - 1, self.grid_size - 1))
            
            # Snake
            for i, seg in enumerate(self.snake):
                x = seg[0] * self.grid_size + shake
                y = seg[1] * self.grid_size + shake
                
                if i == 0:
                    Color(0, 1, 0.4)
                    Ellipse(pos=(x + 1, y + 1), size=(self.grid_size - 2, self.grid_size - 2))
                else:
                    intensity = max(0.4, 1 - (i / max(len(self.snake), 1)))
                    Color(0, intensity * 0.6, intensity * 0.2)
                    Ellipse(pos=(x + 2, y + 2), size=(self.grid_size - 4, self.grid_size - 4))
            
            # Enemies
            if self.enemies:
                Color(1, 0.1, 0.1)
                for enemy in self.enemies:
                    ex = enemy["pos"][0] * self.grid_size + shake
                    ey = enemy["pos"][1] * self.grid_size + shake
                    Ellipse(pos=(ex + 2, ey + 2), size=(self.grid_size - 4, self.grid_size - 4))
            
            # Food
            fx = self.food[0] * self.grid_size + shake
            fy = self.food[1] * self.grid_size + shake
            pulse = 0.7 + 0.25 * math.sin(self.meme_counter * 0.08)
            Color(1, pulse * 0.4, 0.05)
            Ellipse(pos=(fx + 2, fy + 2), size=(self.grid_size - 4, self.grid_size - 4))
            
            # Power-ups
            for pu in self.power_ups:
                px = pu["pos"][0] * self.grid_size + shake
                py = pu["pos"][1] * self.grid_size + shake
                effect = self.POWER_UPS[pu["type"]]
                
                scale = 0.7 + 0.3 * math.sin(self.meme_counter * 0.12)
                size = self.grid_size * scale
                offset = (self.grid_size - size) / 2
                
                Color(*effect["color"])
                Ellipse(pos=(px + offset, py + offset), size=(size, size))
            
            # Particles
            for p in self.particles:
                px = p["pos"][0] + shake
                py = p["pos"][1]
                alpha = 1 - (p["age"] / 0.6)
                Color(p["color"][0], p["color"][1], p["color"][2], alpha)
                Ellipse(pos=(px, py), size=(p["size"], p["size"]))
                
                p["pos"][0] += p["vel"][0] * 0.016
                p["pos"][1] += p["vel"][1] * 0.016
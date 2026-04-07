#!/usr/bin/env python3
"""
Text-based simulation of Brainrot-Snake game logic
Shows how the game works without GUI
"""

import random
import time
import os
import sys

class TextSnakeSimulator:
    def __init__(self, width=20, height=15):
        self.width = width
        self.height = height
        self.grid_size = 1  # For text, each cell is 1 char
        
        # Game state
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.direction = (1, 0)  # right
        self.next_direction = (1, 0)
        self.food = self.spawn_food()
        self.power_ups = []
        self.game_over = False
        
        # Score
        self.score = 0
        self.combo = 0
        self.brain_damage = 0
        
        # Effects
        self.active_effects = {}
        self.speed = 0.3  # seconds between moves
        
        # Mode
        self.mode = "CLASSIC"
        self.time_left = 60 if self.mode == "TIME_ATTACK" else None
        
        # Power-up settings
        self.powerup_chance = 0.01  # Lower for demo
        
        print("🧠 BRAINROT SNAKE - Text Simulation 🐍")
        print("=" * 40)
        print("Controls: w/a/s/d (up/left/down/right), q=quit")
        print("Watch the snake move and collect food!")
        print()

    def spawn_food(self):
        """Spawn food at random location"""
        while True:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if pos not in self.snake:
                return pos
    
    def get_brain_status(self):
        """Get brainrot status emoji"""
        if self.brain_damage >= 90:
            return "💀"
        elif self.brain_damage >= 75:
            return "🌀"
        elif self.brain_damage >= 50:
            return "🔥"
        elif self.brain_damage >= 25:
            return "⚡"
        else:
            return "🧠"
    
    def render(self):
        """Render the game board as text"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Create grid
        grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw snake
        for i, seg in enumerate(self.snake):
            if 0 <= seg[0] < self.width and 0 <= seg[1] < self.height:
                if i == 0:
                    grid[seg[1]][seg[0]] = '🟢'  # Head
                else:
                    grid[seg[1]][seg[0]] = '🟩'  # Body
        
        # Draw food
        if 0 <= self.food[0] < self.width and 0 <= self.food[1] < self.height:
            grid[self.food[1]][self.food[0]] = '🍎'
        
        # Draw power-ups
        for pu in self.power_ups:
            pos = pu["pos"]
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height:
                effect = {
                    "SPEED": "⚡",
                    "SLOW": "🐢", 
                    "GHOST": "👻",
                    "POINTS": "💰",
                    "CHAOS": "🌀"
                }.get(pu["type"], "?")
                grid[pos[1]][pos[0]] = effect
        
        # Print grid
        for row in grid:
            print(''.join(row))
        
        # Print status
        status = f"Score: {self.score} | Combo: {self.combo} | Brain: {self.get_brain_status()}"
        if self.time_left:
            status += f" | Time: {self.time_left}s"
        
        effects = []
        if "speed_mult" in self.active_effects:
            effects.append("⚡SPEED")
        if "slow_mult" in self.active_effects:
            effects.append("🐢SLOW")
        if "ghost" in self.active_effects:
            effects.append("👻GHOST")
        if "points_mult" in self.active_effects:
            effects.append("💰POINTS")
        if "chaos" in self.active_effects:
            effects.append("🌀CHAOS")
        
        if effects:
            status += f" | Active: {', '.join(effects)}"
        
        print(status)
        print()
    
    def update(self):
        """Update game state"""
        if self.game_over:
            return
        
        # Update time
        if self.time_left:
            self.time_left -= 1
            if self.time_left <= 0:
                self.game_over = True
                return
        
        # Brain damage
        self.brain_damage = min(100, self.brain_damage + random.choice([0, 0, 0, 1]))
        
        # Spawn power-ups
        if random.random() < self.powerup_chance:
            pos = self.spawn_food()  # Reuse logic
            if pos:
                self.power_ups.append({
                    "pos": pos,
                    "type": random.choice(["SPEED", "SLOW", "GHOST", "POINTS", "CHAOS"])
                })
        
        # Move
        self.direction = self.next_direction
        
        if "chaos" in self.active_effects:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        
        head_x, head_y = self.snake[0]
        new_x = head_x + self.direction[0]
        new_y = head_y + self.direction[1]
        
        # Ghost mode wraps
        if "ghost" in self.active_effects:
            new_x = new_x % self.width
            new_y = new_y % self.height
        else:
            if new_x < 0 or new_x >= self.width or new_y < 0 or new_y >= self.height:
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
            self.food = self.spawn_food()
            print(f"🍎 Food eaten! +{int(10 * mult)} points")
        else:
            self.snake.pop()
            self.combo = 0
        
        # Power-ups
        for pu in self.power_ups[:]:
            if (new_x, new_y) == pu["pos"]:
                self.activate_powerup(pu["type"])
                self.power_ups.remove(pu)
    
    def activate_powerup(self, ptype):
        """Activate a power-up"""
        print(f"🎁 Power-up collected: {ptype}!")
        
        duration = 5  # Shorter for demo
        
        if ptype == "SPEED":
            self.active_effects["speed_mult"] = 2.0
            # In real game, this would schedule removal
        elif ptype == "SLOW":
            self.active_effects["speed_mult"] = 0.3
        elif ptype == "GHOST":
            self.active_effects["ghost"] = True
        elif ptype == "POINTS":
            self.active_effects["points_mult"] = 3
        elif ptype == "CHAOS":
            self.active_effects["chaos"] = True
        
        # For demo, remove after duration (simplified)
        # In real game, Clock.schedule_once would handle this
    
    def run(self):
        """Run the simulation"""
        moves = 0
        max_moves = 50  # Limit for demo
        
        try:
            while not self.game_over and moves < max_moves:
                self.render()
                self.update()
                moves += 1
                
                # Auto-move for demo (no input needed)
                # Change direction occasionally to avoid walls
                if moves % 10 == 0:
                    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    # Avoid reversing into self
                    current_opposite = (-self.direction[0], -self.direction[1])
                    possible_dirs = [d for d in directions if d != current_opposite]
                    self.next_direction = random.choice(possible_dirs)
                
                time.sleep(0.2)  # Faster for demo
        
        except KeyboardInterrupt:
            pass
        
        self.render()
        print("\n🎮 Simulation Complete!")
        print(f"Final Score: {self.score}")
        print(f"Max Combo: {self.combo}")
        print(f"Brain Status: {self.get_brain_status()}")
        print(f"Moves: {moves}")

def main():
    # Make stdin non-blocking for input
    import termios
    import tty
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(sys.stdin.fileno())
        simulator = TextSnakeSimulator()
        simulator.run()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
import tkinter as tk
import random
from PIL import Image, ImageTk

class RPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏫 Útěk ze školy")
        self.tile_size = 80
        self.canvas = None
        self.map_width = random.randint(5, 10)
        self.map_height = random.randint(5, 10)

        self.difficulty = "střední"
        self.total_grades_required = 5
        self.grades_collected = 0
        self.lives = 3
        self.score = 0
        self.paused = False
        self.turn_counter = 0

        self.player_position = (0, 0)
        self.monster_position = (self.map_width // 2, self.map_height // 2)
        self.teacher_position = (self.map_width - 1, self.map_height - 1)

        self.images = {}
        self.load_images()
        self.canvas_images = {}  

        self.show_main_menu()

    def load_images(self):
        def safe_load(name, file, size):
            try:
                img = Image.open(file).resize(size)
                return ImageTk.PhotoImage(img)
            except:
                return None

        self.images['player'] = safe_load('player', 'player.png', (60, 60))
        self.images['monster'] = safe_load('monster', 'monster.png', (60, 60))
        self.images['teacher'] = safe_load('teacher', 'ucitel.png', (60, 60))
        self.images['grade'] = safe_load('grade', 'grade.png', (40, 40))

    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="🏫 Útěk ze školy", font=("Arial", 40, "bold")).pack(pady=50)
        tk.Button(self.root, text="▶️ Spustit hru", font=("Arial", 24), command=self.start_game).pack(pady=20)
        tk.Button(self.root, text="⚙️ Nastavení obtížnosti", font=("Arial", 24), command=self.select_difficulty).pack(pady=20)
        tk.Button(self.root, text="🚪 Ukončit", font=("Arial", 24), command=self.root.destroy).pack(pady=20)

    def select_difficulty(self):
        win = tk.Toplevel(self.root)
        win.title("Obtížnost")
        win.geometry("300x200")
        win.transient(self.root)
        win.grab_set()
        tk.Label(win, text="Vyber obtížnost:", font=("Arial", 18)).pack(pady=20)
        for diff in ["lehká", "střední", "těžká"]:
            tk.Button(win, text=diff.capitalize(), font=("Arial", 14),
                      command=lambda d=diff: self.set_difficulty(d, win)).pack(pady=5)

    def set_difficulty(self, difficulty, window):
        self.difficulty = difficulty
        window.destroy()

    def start_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.root, width=self.map_width * self.tile_size,
                                height=self.map_height * self.tile_size)
        self.canvas.pack()
        tk.Button(self.root, text="⏸ Pauza", command=self.toggle_pause).pack()

        self.grades_collected = 0
        self.lives = 3
        self.score = 0
        self.turn_counter = 0
        self.player_position = (0, 0)
        self.monster_position = (self.map_width // 2, self.map_height // 2)

        self.spawn_grades()
        self.root.bind("<Key>", self.handle_keypress)
        self.draw_entities()

    def spawn_grades(self):
        positions = [(x, y) for x in range(self.map_width) for y in range(self.map_height)
                     if (x, y) not in [self.player_position, self.monster_position, self.teacher_position]]
        self.grade_positions = random.sample(positions, min(self.total_grades_required, len(positions)))

    def toggle_pause(self):
        self.paused = not self.paused

    def handle_keypress(self, event):
        if self.paused:
            return

        dx, dy = 0, 0
        if event.keysym == "Up":
            dy = -1
        elif event.keysym == "Down":
            dy = 1
        elif event.keysym == "Left":
            dx = -1
        elif event.keysym == "Right":
            dx = 1
        else:
            return

        x, y = self.player_position
        new_x = max(0, min(self.map_width - 1, x + dx))
        new_y = max(0, min(self.map_height - 1, y + dy))
        self.player_position = (new_x, new_y)


        if self.player_position in self.grade_positions:
            self.grade_positions.remove(self.player_position)
            self.grades_collected += 1
            self.score += 10

        if self.player_position == self.monster_position:
            self.lives -= 1
            self.score -= 20
            if self.lives <= 0:
                self.show_game_over()
                return

        if self.player_position == self.teacher_position and self.grades_collected >= self.total_grades_required:
            self.score += 50
            self.show_victory()
            return

        self.turn_counter += 1
        if self.should_monster_move():
            self.move_monster()

        self.draw_entities()

    def should_monster_move(self):
        if self.difficulty == "lehká":
            return self.turn_counter % 3 == 0
        elif self.difficulty == "střední":
            return self.turn_counter % 2 == 0
        else:  
            return True

    def move_monster(self):
        px, py = self.player_position
        mx, my = self.monster_position
        dx, dy = px - mx, py - my

        if abs(dx) > abs(dy):
            mx += 1 if dx > 0 else -1
        else:
            my += 1 if dy > 0 else -1

        mx = max(0, min(self.map_width - 1, mx))
        my = max(0, min(self.map_height - 1, my))
        self.monster_position = (mx, my)

        if self.monster_position == self.player_position:
            self.lives -= 1
            self.score -= 20
            if self.lives <= 0:
                self.show_game_over()

    def draw_entities(self):
        self.canvas.delete("all")
        self.canvas_images.clear()
        for x in range(self.map_width):
            for y in range(self.map_height):
                color = "#666" if (x + y) % 2 == 0 else "#444"
                self.canvas.create_rectangle(x * self.tile_size, y * self.tile_size,
                                             (x + 1) * self.tile_size, (y + 1) * self.tile_size,
                                             fill=color, outline="gray")

        def draw_entity(x, y, img, fallback_color):
            if img:
                self.canvas_images[(x, y)] = self.canvas.create_image(
                    x * self.tile_size + 40, y * self.tile_size + 40, image=img
                )
            else:
                self.canvas.create_oval(x * self.tile_size + 20, y * self.tile_size + 20,
                                        x * self.tile_size + 60, y * self.tile_size + 60,
                                        fill=fallback_color)

        for gx, gy in self.grade_positions:
            draw_entity(gx, gy, self.images['grade'], 'yellow')

        px, py = self.player_position
        draw_entity(px, py, self.images['player'], 'blue')

        mx, my = self.monster_position
        draw_entity(mx, my, self.images['monster'], 'red')

        tx, ty = self.teacher_position
        draw_entity(tx, ty, self.images['teacher'], 'green')

        self.canvas.create_text(10, 10, anchor="nw",
                                text=f"📄 Známky: {self.grades_collected}/{self.total_grades_required}   ❤️ Životy: {self.lives}   ⭐ Skóre: {self.score}",
                                font=("Arial", 14), fill="white")

    def show_game_over(self):
        self.root.unbind("<Key>")
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="💀 Konec hry!", font=("Arial", 36), fg="red").pack(pady=50)
        tk.Label(self.root, text=f"Skóre: {self.score}", font=("Arial", 24)).pack(pady=10)
        tk.Button(self.root, text="🔁 Hrát znovu", font=("Arial", 24), command=self.start_game).pack(pady=20)
        tk.Button(self.root, text="↩️ Hlavní menu", font=("Arial", 24), command=self.show_main_menu).pack(pady=10)

    def show_victory(self):
        self.root.unbind("<Key>")
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="🏆 Vyhrál jsi!", font=("Arial", 36), fg="green").pack(pady=50)
        tk.Label(self.root, text=f"Skóre: {self.score}", font=("Arial", 24)).pack(pady=10)
        tk.Button(self.root, text="🔁 Hrát znovu", font=("Arial", 24), command=self.start_game).pack(pady=20)
        tk.Button(self.root, text="↩️ Hlavní menu", font=("Arial", 24), command=self.show_main_menu).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGApp(root)
    root.mainloop()

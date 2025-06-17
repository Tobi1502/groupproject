import tkinter as tk
import random
from PIL import Image, ImageTk
from playsound import playsound
import threading
import datetime
from collections import deque

class RPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏫 Útěk ze školy")
        self.root.attributes('-fullscreen', True)
        self.tile_size = 64
        self.canvas = None
        self.difficulty = "střední"
        self.total_grades_required = 5
        self.grades_collected = 0
        self.lives = 3
        self.score = 0
        self.paused = False
        self.turn_counter = 0
        self.sound_on = True
        self.level = 1
        self.images = {}
        self.canvas_images = {}
        self.obstacles = set()

        self.load_images()
        self.show_main_menu()

    def load_images(self):
        def safe_load(name, file, size):
            try:
                img = Image.open(file).resize(size)
                return ImageTk.PhotoImage(img)
            except:
                print(f"[!] Nelze načíst {file}, použije se náhradní tvar.")
                return None

        self.images['player'] = safe_load('player', 'player.png', (50, 50))
        self.images['monster'] = safe_load('monster', 'monster.png', (50, 50))
        self.images['teacher'] = safe_load('teacher', 'ucitel.png', (50, 50))
        self.images['grade'] = safe_load('grade', 'grade.png', (30, 30))

    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="🏫 Útěk ze školy", font=("Arial", 40, "bold")).pack(pady=50)
        tk.Button(self.root, text="▶️ Spustit hru", font=("Arial", 24), command=self.start_game).pack(pady=20)
        tk.Button(self.root, text="⚙️ Obtížnost", font=("Arial", 24), command=self.select_difficulty).pack(pady=20)
        tk.Button(self.root, text=f"🔊 Zvuk: {'Zapnutý' if self.sound_on else 'Vypnutý'}", font=("Arial", 24), command=self.toggle_sound).pack(pady=20)
        tk.Button(self.root, text="📜 Zobrazit skóre", font=("Arial", 24), command=self.show_score_file).pack(pady=20)
        tk.Button(self.root, text="🚪 Ukončit", font=("Arial", 24), command=self.root.destroy).pack(pady=20)

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.show_main_menu()

    def select_difficulty(self):
        win = tk.Toplevel(self.root)
        win.title("Obtížnost")
        win.geometry("400x400")
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
        self.map_width = min(15, 9 + self.level)
        self.map_height = min(15, 9 + self.level)
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
        self.teacher_position = (self.map_width - 1, self.map_height - 1)
        self.monster_position = (self.map_width // 2, self.map_height // 2)
        self.canvas_images = {}

        self.generate_valid_obstacles()
        self.spawn_grades()
        self.root.bind("<Key>", self.handle_keypress)
        self.draw_entities()

    def generate_valid_obstacles(self):
        while True:
            all_pos = [(x, y) for x in range(self.map_width) for y in range(self.map_height)
                       if (x, y) not in [self.player_position, self.teacher_position, self.monster_position]]
            self.obstacles = set(random.sample(all_pos, min(len(all_pos), 20 + self.level * 2)))
            if self.is_path_clear():
                break

    def is_path_clear(self):
        queue = deque([self.player_position])
        visited = set()
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == self.teacher_position:
                return True
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                    if (nx, ny) not in visited and (nx, ny) not in self.obstacles:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return False

    def spawn_grades(self):
        positions = [(x, y) for x in range(self.map_width) for y in range(self.map_height)
                     if (x, y) not in [self.player_position, self.monster_position, self.teacher_position]
                     and (x, y) not in self.obstacles]
        self.grade_positions = random.sample(positions, min(self.total_grades_required, len(positions)))

    def toggle_pause(self):
        self.paused = not self.paused

    def play_sound(self, file):
        if self.sound_on:
            threading.Thread(target=playsound, args=(file,), daemon=True).start()

    def handle_keypress(self, event):
        if self.paused:
            return

        dx, dy = 0, 0
        if event.keysym == "Up": dy = -1
        elif event.keysym == "Down": dy = 1
        elif event.keysym == "Left": dx = -1
        elif event.keysym == "Right": dx = 1
        else: return

        x, y = self.player_position
        new_x = max(0, min(self.map_width - 1, x + dx))
        new_y = max(0, min(self.map_height - 1, y + dy))

        if (new_x, new_y) in self.obstacles:
            self.canvas.create_text(self.canvas.winfo_width()//2, self.canvas.winfo_height()-30,
                                    text="🚪 Tyto dveře jsou zavřené!", font=("Arial", 16), fill="orange")
            return

        self.player_position = (new_x, new_y)

        if self.player_position in self.grade_positions:
            self.grade_positions.remove(self.player_position)
            self.grades_collected += 1
            self.score += 10
            self.play_sound("paper.mp3")

        if self.player_position == self.monster_position:
            self.lives -= 1
            self.score -= 20
            self.play_sound("fall.mp3")
            if self.lives <= 0:
                self.play_sound("explosion.mp3")
                self.save_score()
                self.show_game_over()
                return

        if self.player_position == self.teacher_position and self.grades_collected >= self.total_grades_required:
            self.score += 50
            self.play_sound("drum.mp3")
            self.save_score()
            self.show_level_complete()
            return

        self.turn_counter += 1
        if self.should_monster_move():
            self.move_monster()

        self.draw_entities()

    def should_monster_move(self):
        if self.difficulty == "lehká": return self.turn_counter % 3 == 0
        if self.difficulty == "střední": return self.turn_counter % 2 == 0
        return True

    def move_monster(self):
        px, py = self.player_position
        mx, my = self.monster_position
        dx, dy = px - mx, py - my
        if abs(dx) > abs(dy): mx += 1 if dx > 0 else -1
        else: my += 1 if dy > 0 else -1
        if (0 <= mx < self.map_width and 0 <= my < self.map_height and (mx, my) not in self.obstacles):
            self.monster_position = (mx, my)
        if self.monster_position == self.player_position:
            self.lives -= 1
            self.score -= 20
            self.play_sound("explosion.mp3")
            if self.lives <= 0:
                self.save_score()
                self.show_game_over()

    def draw_entities(self):
        self.canvas.delete("all")
        self.canvas_images.clear()
        for x in range(self.map_width):
            for y in range(self.map_height):
                color = "#666" if (x + y) % 2 == 0 else "#444"
                if (x, y) in self.obstacles:
                    color = "#222"
                self.canvas.create_rectangle(x * self.tile_size, y * self.tile_size,
                                             (x + 1) * self.tile_size, (y + 1) * self.tile_size,
                                             fill=color, outline="gray")

        def draw(x, y, img, fallback):
            if img:
                self.canvas_images[(x, y)] = self.canvas.create_image(
                    x * self.tile_size + 32, y * self.tile_size + 32, image=img)
            else:
                self.canvas.create_oval(x * self.tile_size + 16, y * self.tile_size + 16,
                                        x * self.tile_size + 48, y * self.tile_size + 48,
                                        fill=fallback)

        for gx, gy in self.grade_positions:
            draw(gx, gy, self.images['grade'], 'yellow')

        draw(*self.player_position, self.images['player'], 'blue')
        draw(*self.monster_position, self.images['monster'], 'red')
        draw(*self.teacher_position, self.images['teacher'], 'green')

        self.canvas.create_text(10, 10, anchor="nw",
            text=f"🧾 Známky: {self.grades_collected}/{self.total_grades_required}  ❤️ Životy: {self.lives}  ⭐ Skóre: {self.score}",
            font=("Arial", 14), fill="white")

    def show_level_complete(self):
        self.root.unbind("<Key>")
        for widget in self.root.winfo_children(): widget.destroy()
        tk.Label(self.root, text=f"✅ Úroveň {self.level} dokončena!", font=("Arial", 36), fg="green").pack(pady=50)
        tk.Label(self.root, text=f"Skóre: {self.score}", font=("Arial", 24)).pack(pady=10)
        tk.Button(self.root, text="➡️ Pokračovat", font=("Arial", 24), command=self.next_level).pack(pady=20)
        tk.Button(self.root, text="↩️ Hlavní menu", font=("Arial", 24), command=self.show_main_menu).pack(pady=10)

    def next_level(self):
        self.level += 1
        self.total_grades_required += 1
        self.start_game()

    def save_score(self):
        try:
            with open("skore.txt", "a", encoding="utf-8") as f:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{now}] Skóre: {self.score}\n")
        except Exception as e:
            print("Chyba při ukládání skóre:", e)

    def show_score_file(self):
        win = tk.Toplevel(self.root)
        win.title("Skóre")
        win.geometry("400x400")
        text = tk.Text(win, font=("Arial", 12))
        text.pack(expand=True, fill="both")
        try:
            with open("skore.txt", "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except FileNotFoundError:
            text.insert("1.0", "Zatím žádné skóre nebylo uloženo.")

    def show_game_over(self):
        self.root.unbind("<Key>")
        for widget in self.root.winfo_children(): widget.destroy()
        tk.Label(self.root, text="💀 Konec hry!", font=("Arial", 36), fg="red").pack(pady=50)
        tk.Label(self.root, text=f"Skóre: {self.score}", font=("Arial", 24)).pack(pady=10)
        tk.Button(self.root, text="🔁 Hrát znovu", font=("Arial", 24), command=self.start_game).pack(pady=20)
        tk.Button(self.root, text="↩️ Hlavní menu", font=("Arial", 24), command=self.show_main_menu).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGApp(root)
    root.mainloop()

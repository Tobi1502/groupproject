import tkinter as tk
import random, os, json, threading
from tkinter import messagebox
from collections import deque
from PIL import Image, ImageTk
from playsound import playsound

class RPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏫 Útěk ze školy")
        self.root.attributes('-fullscreen', True)

        self.tile_size = 64
        self.map_size = 10
        self.difficulty = "střední"
        self.level = 1
        self.lives = 3
        self.total_grades_required = 5
        self.grades_collected = 0
        self.score = 0
        self.sound_on = True
        self.volume = 100
        self.paused = False
        self.turn_counter = 0

        self.profile_file = "profil.json"
        self.scores_file = "skore.json"
        self.player_name = ""
        self.player_skin = "Malej Vorel"
        self.profile_data = {}
        self.scores = {}
        self.konami_code = ['up','up','down','down','left','right','left','right','b','a']
        self.konami_index = 0

        self.images = {}
        self.load_images()
        self.load_profile()
        self.ask_for_name()

    def load_images(self):
        def load(file, size):
            try:
                return ImageTk.PhotoImage(Image.open(file).resize(size))
            except Exception as e:
                print(f"❌ Nelze načíst {file}: {e}")
                return None

        self.images['player'] = load('player.png', (54, 54))
        self.images['monster'] = load('monster.png', (54, 54))
        self.images['teacher'] = load('ucitel.png', (48, 48))
        self.images['grade'] = load('grade.png', (32, 32))
        self.images['jumpscare'] = load('jumpscare.png', (800, 600))
  

    def ask_for_name(self):
        def submit():
            name = entry.get().strip()
            if not name:
                return
            self.player_name = name
            if name not in self.profile_data:
                self.profile_data[name] = {"level": 1, "skin": "default", "total_score": 0, "last_score": 0}
            if name not in self.scores:
                self.scores[name] = []
            self.save_profile()
            top.destroy()
            self.show_main_menu()

        top = tk.Toplevel(self.root)
        top.geometry("300x150+300+300")
        top.grab_set()
        top.focus_force()
        tk.Label(top, text="Zadej jméno:", font=("Arial", 14)).pack(pady=10)
        entry = tk.Entry(top, font=("Arial", 14))
        entry.pack()
        tk.Button(top, text="OK", command=submit).pack(pady=10)
        entry.focus()

    def load_profile(self):
        if os.path.exists(self.profile_file):
            with open(self.profile_file, "r", encoding="utf-8") as f:
                self.profile_data = json.load(f)
        if os.path.exists(self.scores_file):
            with open(self.scores_file, "r", encoding="utf-8") as f:
                self.scores = json.load(f)

    def save_profile(self):
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(self.profile_data, f, indent=2)
        with open(self.scores_file, "w", encoding="utf-8") as f:
            json.dump(self.scores, f, indent=2)

    def show_main_menu(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text=f"🏫 Útěk ze školy – {self.player_name}", font=("Arial", 26)).pack(pady=20)
        tk.Button(self.root, text="▶️ Spustit hru", font=("Arial", 20), command=self.start_game).pack(pady=10)
        tk.Button(self.root, text="🎽 Vybrat vzhled", font=("Arial", 20), command=self.choose_skin).pack(pady=10)
        tk.Button(self.root, text="⚙️ Nastavit obtížnost", font=("Arial", 20), command=self.choose_difficulty).pack(pady=10)
        tk.Button(self.root, text="📊 Statistiky hráče", font=("Arial", 20), command=self.show_stats).pack(pady=10)
        tk.Button(self.root, text="🎚️ Nastavení zvuku", font=("Arial", 20), command=self.sound_settings).pack(pady=10)
        tk.Button(self.root, text="🚪 Ukončit", font=("Arial", 20), command=self.root.destroy).pack(pady=20)

    def choose_skin(self):
        win = tk.Toplevel(self.root)
        win.title("Skin")
        tk.Label(win, text="Vyber si skin:", font=("Arial", 14)).pack(pady=10)
        def set_skin(skin):
            self.player_skin = skin
            self.profile_data[self.player_name]["skin"] = skin
            self.save_profile()
            win.destroy()
        tk.Button(win, text="🔵 Vorel", command=lambda: set_skin("Malej Vorel")).pack(pady=5)
        if self.level >= 10:
            tk.Button(win, text="⚫ Toby", command=lambda: set_skin("bilej cigan")).pack(pady=5)
        if self.level >= 25:
            tk.Button(win, text="⚙️ Satrick", command=lambda: set_skin("cigan")).pack(pady=5)

    def sound_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Zvuk")
        tk.Label(win, text="Hlasitost:", font=("Arial", 14)).pack()
        slider = tk.Scale(win, from_=0, to=100, orient="horizontal")
        slider.set(self.volume)
        slider.pack()
        tk.Button(win, text="Uložit", command=lambda: self.set_volume(slider.get(), win)).pack(pady=10)

    def set_volume(self, vol, win):
        self.volume = vol
        win.destroy()

    def show_stats(self):
        prof = self.profile_data.get(self.player_name, {})
        msg = (
            f"🎽 Skin: {prof.get('skin','default')}\n"
            f"🧭 Úroveň: {prof.get('level',1)}\n"
            f"⭐ Celkové skóre: {prof.get('total_score',0)}\n"
            f"🕹️ Poslední výsledek: {prof.get('last_score',0)}"
        )
        messagebox.showinfo("📊 Statistiky hráče", msg)

    def choose_difficulty(self):
        win = tk.Toplevel(self.root)
        win.title("Výběr obtížnosti")
        tk.Label(win, text="Vyber obtížnost:", font=("Arial", 14)).pack(pady=10)

        difficulties = ["lehká", "střední", "těžká", "extrémní", "král baráže"]

        for diff in difficulties:
            tk.Button(
                win, text=diff.capitalize(), font=("Arial", 12),
                command=lambda d=diff: self.set_difficulty(d, win)
            ).pack(pady=5)

    def set_difficulty(self, diff, win):
        self.difficulty = diff
        win.destroy()

    def start_game(self):
        self.level = self.profile_data[self.player_name]["level"]
        self.player_skin = self.profile_data[self.player_name]["skin"]
        self.lives = 3
        self.score = 0
        self.grades_collected = 0
        self.turn_counter = 0
        self.map_size = min(10 + self.level, 15)
        self.total_grades_required = 5 + self.level

        self.root.unbind("<Key>")
        self.root.bind("<Key>", self.handle_keypress)

        self.generate_map()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.canvas = tk.Canvas(self.root, width=self.map_size * self.tile_size,
                                height=self.map_size * self.tile_size, bg="black")
        self.canvas.pack()
        tk.Button(self.root, text="⏸ Pauza", command=self.pause_game).pack()
        self.draw_map()
    
    def generate_map(self):
        self.player_position = (0, 0)
        self.teacher_position = (self.map_size - 1, self.map_size - 1)
        self.monster_position = (self.map_size // 2, self.map_size // 2)
        self.blocked = set()

        while True:
            self.blocked.clear()
            for _ in range(self.map_size * 2):
                x = random.randint(0, self.map_size - 1)
                y = random.randint(0, self.map_size - 1)
                if (x, y) not in [self.player_position, self.teacher_position]:
                    self.blocked.add((x, y))
            if self.path_exists(self.player_position, self.teacher_position):
                break

        self.grade_positions = []
        while len(self.grade_positions) < self.total_grades_required:
            pos = (random.randint(0, self.map_size - 1), random.randint(0, self.map_size - 1))
            if pos not in self.blocked and pos not in self.grade_positions and pos != self.player_position and pos != self.teacher_position:
                self.grade_positions.append(pos)

    def path_exists(self, start, goal):
        q = deque([start])
        visited = set()
        while q:
            current = q.popleft()
            if current == goal:
                return True
            visited.add(current)
            x, y = current
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.map_size and 0 <= ny < self.map_size:
                    if (nx, ny) not in visited and (nx, ny) not in self.blocked:
                        q.append((nx, ny))
        return False

    def draw_map(self):
        self.canvas.delete("all")
        for x in range(self.map_size):
            for y in range(self.map_size):
                color = "#444" if (x + y) % 2 == 0 else "#222"
                if (x, y) in self.blocked:
                    color = "#662222"
                self.canvas.create_rectangle(
                    x * self.tile_size, y * self.tile_size,
                    (x+1) * self.tile_size, (y+1) * self.tile_size,
                    fill=color, outline="gray"
                )

        for gx, gy in self.grade_positions:
            if self.images.get('grade'):
                self.canvas.create_image(
                    gx * self.tile_size + 32, gy * self.tile_size + 32,
                    image=self.images['grade']
                )
            else:
                self.canvas.create_oval(
                    gx * self.tile_size + 24, gy * self.tile_size + 24,
                    gx * self.tile_size + 40, gy * self.tile_size + 40,
                    fill="yellow", outline="white"
                )

    def draw_map(self):
        self.canvas.delete("all")
        for x in range(self.map_size):
            for y in range(self.map_size):
              color = "#444" if (x + y) % 2 == 0 else "#222"
              if (x, y) in self.blocked:
                color = "#662222"
              self.canvas.create_rectangle(
                x * self.tile_size, y * self.tile_size,
                (x + 1) * self.tile_size, (y + 1) * self.tile_size,
                fill=color, outline="gray"
              )
        for gx, gy in self.grade_positions:
            if self.images.get('grade'):
              self.canvas.create_image(
                gx * self.tile_size + self.tile_size // 2,
                gy * self.tile_size + self.tile_size // 2,
                image=self.images['grade']
               )
            else:
                self.canvas.create_oval(
                    gx * self.tile_size + 24, gy * self.tile_size + 24,
                    gx * self.tile_size + 40, gy * self.tile_size + 40,
                    fill="yellow", outline="white"
                )
        px, py = self.player_position
        if self.images.get('player'):
            self.canvas.create_image(
                px * self.tile_size + self.tile_size // 2,
                py * self.tile_size + self.tile_size // 2,
                image=self.images['player']
           )
        else:
            self.canvas.create_oval(
                px * self.tile_size + 10, py * self.tile_size + 10,
                px * self.tile_size + 54, py * self.tile_size + 54,
                fill="blue", outline="white", width=2
             )
        mx, my = self.monster_position
        if self.images.get('monster'):
            self.canvas.create_image(
                mx * self.tile_size + self.tile_size // 2,
                my * self.tile_size + self.tile_size // 2,
                image=self.images['monster']
            )
        else:
            self.canvas.create_oval(
                mx * self.tile_size + 10, my * self.tile_size + 10,
                mx * self.tile_size + 54, my * self.tile_size + 54,
                fill="red", outline="black", width=2
            )
        tx, ty = self.teacher_position
        if self.images.get('teacher'):
            self.canvas.create_image(
                tx * self.tile_size + self.tile_size // 2,
                ty * self.tile_size + self.tile_size // 2,
                image=self.images['teacher']
            )
        else:
            self.canvas.create_rectangle(
                tx * self.tile_size + 20, ty * self.tile_size + 20,
                tx * self.tile_size + 44, ty * self.tile_size + 44,
                fill="white", outline="black"
            )
        self.canvas.create_text(
            10, 10, anchor="nw",
            text=f"📄 {self.grades_collected}/{self.total_grades_required}   ❤️ {self.lives}   ⭐ {self.score}",
            font=("Arial", 14), fill="white"
        )
    def handle_keypress(self, event):
        if self.paused: return
        key = event.keysym.lower()

        if key == self.konami_code[self.konami_index].lower():
            self.konami_index += 1
            if self.konami_index == len(self.konami_code):
                self.konami_index = 0
                self.trigger_jumpscare()
                return
        else:
            self.konami_index = 0

        dx, dy = 0, 0
        if key == "up": dy = -1
        elif key == "down": dy = 1
        elif key == "left": dx = -1
        elif key == "right": dx = 1
        else: return

        x, y = self.player_position
        nx, ny = x + dx, y + dy
        if 0 <= nx < self.map_size and 0 <= ny < self.map_size:
            if (nx, ny) not in self.blocked:
                self.player_position = (nx, ny)
                self.turn_counter += 1

                if self.player_position in self.grade_positions:
                    self.grade_positions.remove(self.player_position)
                    self.grades_collected += 1
                    self.score += 10

                if self.player_position == self.teacher_position and self.grades_collected >= self.total_grades_required:
                    self.level += 1
                    self.profile_data[self.player_name]["level"] = self.level
                    self.profile_data[self.player_name]["total_score"] += self.score
                    self.profile_data[self.player_name]["last_score"] = self.score
                    self.save_profile()

                    messagebox.showinfo("🏆", f"level dokončen! Skóre: {self.score}")
                    self.start_game()
                    return

                self.move_monster()
                if self.player_position == self.monster_position:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.profile_data[self.player_name]["last_score"] = self.score
                        self.save_profile()
                        messagebox.showerror("💀", "Příšera tě dostala!")
                        self.show_main_menu()
                        return

        self.draw_map()
        
    def move_monster(self):
        moves = {
            "lehká": 1 if self.turn_counter % 3 == 0 else 0,
            "střední": 1 if self.turn_counter % 2 == 0 else 0,
            "těžká": 1,
            "extrémní": 2,
            "král baráže": 3
        }.get(self.difficulty, 1)

        for _ in range(moves):
            path = self.bfs(self.monster_position, self.player_position)
            if path and len(path) > 1:
                self.monster_position = path[1]

    def bfs(self, start, goal):
        q = deque([(start, [start])])
        visited = set()
        while q:
            current, path = q.popleft()
            if current == goal:
                return path
            visited.add(current)
            x, y = current
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                next_pos = (nx, ny)
                if 0 <= nx < self.map_size and 0 <= ny < self.map_size:
                    if next_pos not in visited and next_pos not in self.blocked:
                        q.append((next_pos, path + [next_pos]))
        return []

    def pause_game(self):
        self.paused = True
        win = tk.Toplevel(self.root)
        win.title("⏸ Pauza")
        tk.Label(win, text="Hra je pozastavena", font=("Arial", 14)).pack(pady=10)
        tk.Button(win, text="▶️ Pokračovat", command=lambda: self.resume_game(win)).pack(pady=5)
        tk.Button(win, text="🎚️ Zvuk", command=self.sound_settings).pack(pady=5)
        tk.Button(win, text="↩️ Menu", command=lambda: [win.destroy(), self.show_main_menu()]).pack(pady=5)

    def resume_game(self, win):
        self.paused = False
        win.destroy()

    def trigger_jumpscare(self):
        win = tk.Toplevel(self.root)
        win.attributes('-fullscreen', True)
        win.configure(bg='black')
        if self.images.get('jumpscare'):
            label = tk.Label(win, image=self.images['jumpscare'], bg='black')
            label.image = self.images['jumpscare']
        else:
            label = tk.Label(win, text="😱 JUMPSCARE!", font=("Arial", 60), fg="red", bg="black")
        label.pack(expand=True)
        if self.sound_on and os.path.exists("jumpscare.mp3"):
            threading.Thread(target=lambda: playsound("jumpscare.mp3"), daemon=True).start()
        self.root.after(3000, win.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    app = RPGApp(root)
    root.mainloop()

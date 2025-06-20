# 🏫 Školní RPG: Útěk před monstrem v1.1

Tato hra je jednoduché 2D RPG vytvořené v Pythonu pomocí knihovny `tkinter`. Tvým cílem je nasbírat známky, vyhnout se monstru a dojít k učiteli, který tě zachrání.

---

## ▶️ Jak spustit hru

1. Ujisti se, že máš Python 3.7+.
2. Do terminálu napiš:

   ```bash
   pip install playsound pillow
   python skola_final.py

🎮 Ovládání

▶️ Pohyb: šipky

⏸ Pauza: P

❌ Ukončení: Esc

⚙️ Funkce hry

👣 Pohyb postavy po mapě (5×5)

👹 Monstrum tě pronásleduje každé 2 tahy

📄 Sbírání známek (počet si můžeš nastavit)

👨‍🏫 Výhra: nasbíráš všechny známky a dojdeš k učiteli

💀 Prohra: přijdou ti všechny životy

🎚️ Výběr obtížnosti (lehká, střední, těžká)

💾 Automatické uložení nastavení do settings.txt

🧠 Nastavení obtížnosti

Update v2

Popis 

Nové funkce:
🧩 Generování mapy s překážkami, které zajišťují, že každá mapa je dohratelná.

🌌 Fullscreen režim pro lepší zážitek.

🕹️ Pět obtížností:

Lehká (příšera se hýbe 1× za 3 tahy),

Střední (1× za 2 tahy),

Těžká (každý tah),

Extrémní (2× za tah hráče),

Král baráže (3× za tah hráče).

👹 Chytrý pohyb příšery pomocí algoritmu BFS (vyhýbá se překážkám a sleduje hráče).

🎨 Skinsystém: Základní, Ninja (od lvl 10), Robot (od lvl 25).

📈 Statistiky hráče – úroveň, skóre, poslední výsledek.

📁 Ukládání profilu a skóre (profil.json, skore.json).

📄 Sbírání známek jako podmínka pro dokončení úrovně.

⏸️ Pauza s možností:

Pokračovat ve hře,

Otevřít nastavení zvuku,

Návrat do hlavního menu.

🎚️ Ovládání hlasitosti pomocí slideru.

🔊 Zvuky ve formátu MP3: buben, výbuch, pád, známka, jumpscare.

💀 Jumpscare

🧠 Každý level se zvyšuje obtížností a známkami.

🐞 Opravy chyb:
✅ Vyřešeno: bílé okno při spuštění kvůli překrytému vstupnímu oknu.

✅ Opraven problém s tím, že se postavy nehýbaly po návratu do menu.

✅ Opraveno zpoždění při pohybu nahoru.

✅ Opraven tk.messagebox → správně importováno jako from tkinter import messagebox.

✅ Správně se zobrazují obrázky postav a známek.



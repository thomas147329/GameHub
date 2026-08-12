import random
import tkinter as tk

WIDTH, HEIGHT = 700, 500
root = tk.Tk()
root.title("Space Dodge")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#050816", highlightthickness=0)
canvas.pack()

player = canvas.create_polygon(350, 450, 335, 480, 365, 480, fill="#66c0f4")
keys = set()
ast = []
score = 0
running = True

for _ in range(7):
    x = random.randint(20, WIDTH - 20)
    y = random.randint(-500, 0)
    ast.append(canvas.create_oval(x, y, x + 24, y + 24, fill="#e6e6e6", outline=""))

score_text = canvas.create_text(15, 15, anchor="nw", fill="white", font=("Helvetica", 16, "bold"), text="Score: 0")


def key_down(event):
    keys.add(event.keysym.lower())


def key_up(event):
    keys.discard(event.keysym.lower())


def game_over():
    global running
    running = False
    canvas.create_text(WIDTH / 2, HEIGHT / 2, fill="white", font=("Helvetica", 32, "bold"), text=f"GAME OVER\nScore: {score}")


def update():
    global score
    if not running:
        return
    dx = (-7 if "left" in keys or "a" in keys else 0) + (7 if "right" in keys or "d" in keys else 0)
    canvas.move(player, dx, 0)
    px = canvas.coords(player)
    if px[0] < 0:
        canvas.move(player, -px[0], 0)
    if px[2] > WIDTH:
        canvas.move(player, WIDTH - px[2], 0)

    pbox = canvas.bbox(player)
    for obj in ast:
        canvas.move(obj, 0, 5)
        box = canvas.bbox(obj)
        if box[1] > HEIGHT:
            x = random.randint(20, WIDTH - 20)
            canvas.coords(obj, x, -30, x + 24, -6)
            score += 1
        if box and not (box[2] < pbox[0] or box[0] > pbox[2] or box[3] < pbox[1] or box[1] > pbox[3]):
            game_over()
    canvas.itemconfig(score_text, text=f"Score: {score}")
    root.after(30, update)


root.bind("<KeyPress>", key_down)
root.bind("<KeyRelease>", key_up)
root.focus_force()
update()
root.mainloop()

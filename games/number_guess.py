import random
import tkinter as tk

root = tk.Tk()
root.title("Number Guess")
root.geometry("420x300")
root.configure(bg="#171a21")

state = {"number": random.randint(1, 100)}

label = tk.Label(root, text="Guess a number from 1 to 100", bg="#171a21", fg="white", font=("Helvetica", 16))
label.pack(pady=30)
entry = tk.Entry(root, font=("Helvetica", 18), justify="center")
entry.pack()
result = tk.Label(root, text="", bg="#171a21", fg="#66c0f4", font=("Helvetica", 14))
result.pack(pady=20)

def guess():
    try:
        value = int(entry.get())
    except ValueError:
        result.config(text="Enter a number!")
        return
    if value < state["number"]:
        result.config(text="Too low!")
    elif value > state["number"]:
        result.config(text="Too high!")
    else:
        result.config(text="You got it! New number generated.")
        state["number"] = random.randint(1, 100)
        entry.delete(0, tk.END)

tk.Button(root, text="GUESS", command=guess, bg="#66c0f4", fg="#101820", bd=0, padx=25, pady=8).pack()
root.mainloop()

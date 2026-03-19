import tkinter as tk
from tkinter import messagebox

from password_generator.core import (
    build_pool_config,
    PasswordSpec,
    CharacterConfig,
    generate_passwords
)


def generate():
    try:
        length = int(length_entry.get())
        count = int(count_entry.get())
        mode = mode_entry.get().lower()

        if mode not in {"a", "n", "s", "an", "as", "ns", "ans"}:
            raise ValueError("Invalid mode")

        pool_config = build_pool_config(exclude_ambiguous_var.get())

        password_specs = [
            PasswordSpec(length=length, mode=mode)
            for _ in range(count)
        ]

        character_configs = [CharacterConfig() for _ in range(count)]

        passwords = generate_passwords(
            password_specs,
            character_configs,
            pool_config
        )

        output_box.delete("1.0", tk.END)
        for i, pwd in enumerate(passwords, 1):
            output_box.insert(tk.END, f"{i}: {pwd}\n")

    except Exception as e:
        messagebox.showerror("Error", str(e))


# Window
app = tk.Tk()
app.title("Secure Password Generator")
app.geometry("400x400")

# Inputs
tk.Label(app, text="Password Length").pack()
length_entry = tk.Entry(app)
length_entry.insert(0, "12")
length_entry.pack()

tk.Label(app, text="Number of Passwords").pack()
count_entry = tk.Entry(app)
count_entry.insert(0, "1")
count_entry.pack()

tk.Label(app, text="Mode (a, n, s, an, ans)").pack()
mode_entry = tk.Entry(app)
mode_entry.insert(0, "ans")
mode_entry.pack()

exclude_ambiguous_var = tk.BooleanVar()
tk.Checkbutton(app, text="Exclude ambiguous characters", variable=exclude_ambiguous_var).pack()

# Button
tk.Button(app, text="Generate Passwords", command=generate).pack(pady=10)

# Output
output_box = tk.Text(app, height=10)
output_box.pack()

app.mainloop()
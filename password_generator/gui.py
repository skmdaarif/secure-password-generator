import os
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "passwd-icon.png")

from password_generator.core import (
    build_password_specs,
    build_pool_config,
    generate_passwords,
    CharacterConfig
)

# ===== COLORS =====
BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#22c55e"
TEXT = "#e2e8f0"
SUBTLE = "#94a3b8"
BUTTON = "#16a34a"


# ================= PASSWORD STRENGTH =================
def evaluate_strength(password):
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if any(c.islower() for c in password): score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(not c.isalnum() for c in password): score += 1

    if score <= 2:
        return "Weak", "#ef4444"
    elif score <= 4:
        return "Medium", "#facc15"
    else:
        return "Strong", "#22c55e"


# ================= SPLASH =================
class SplashScreen:
    def __init__(self, root, duration=2000):
        self.root = root
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg=BG)

        width, height = 400, 250
        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)
        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(self.splash, text="🔐 Secure-Password-Generator",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=40)

        tk.Label(self.splash, text="Launching secure generator...",
                 bg=BG, fg=SUBTLE).pack()

        self.root.after(duration, self.close)

    def close(self):
        self.splash.destroy()
        self.root.deiconify()


# ================= GUI =================
class PasswordGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure-Password-Generator")
        self.root.geometry("520x720")
        self.root.configure(bg=BG)

        self.passwords = []
        self.show_passwords = True

        try:
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        except:
            pass

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=BG, background=BG, foreground=TEXT)
        style.map("TCombobox",
                  fieldbackground=[("readonly", BG)],
                  foreground=[("readonly", TEXT)])

        tk.Label(root, text="🔐 Secure-Password-Generator",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=15)

        self.card = tk.Frame(root, bg=CARD)
        self.card.pack(padx=20, pady=10, fill="both", expand=True)

        self.make_row("Number of Passwords:", "count", "1")

        # ===== LENGTH =====
        self.length_type = tk.StringVar(value="fixed")

        frame_type = tk.Frame(self.card, bg=CARD)
        frame_type.pack(pady=10)

        tk.Radiobutton(frame_type, text="Fixed", variable=self.length_type,
                       value="fixed", command=self.toggle_length,
                       bg=CARD, fg=TEXT).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(frame_type, text="Range", variable=self.length_type,
                       value="range", command=self.toggle_length,
                       bg=CARD, fg=TEXT).pack(side=tk.LEFT, padx=10)

        self.length_container = tk.Frame(self.card, bg=CARD)
        self.length_container.pack(pady=5)

        self.frame_fixed = tk.Frame(self.length_container, bg=CARD)
        self.frame_fixed.pack()
        self.make_row("Length:", "length", "12", parent=self.frame_fixed)

        self.frame_range = tk.Frame(self.length_container, bg=CARD)

        tk.Label(self.frame_range, text="Min:", bg=CARD, fg=TEXT).pack(side=tk.LEFT)
        self.min_length = tk.Entry(self.frame_range, width=5, bg=BG, fg=TEXT)
        self.min_length.insert(0, "8")
        self.min_length.pack(side=tk.LEFT)

        tk.Label(self.frame_range, text="Max:", bg=CARD, fg=TEXT).pack(side=tk.LEFT)
        self.max_length = tk.Entry(self.frame_range, width=5, bg=BG, fg=TEXT)
        self.max_length.insert(0, "20")
        self.max_length.pack(side=tk.LEFT)

        # ===== MODE =====
        frame_mode = tk.Frame(self.card, bg=CARD)
        frame_mode.pack(pady=10)

        tk.Label(frame_mode, text="Mode:", bg=CARD, fg=TEXT).pack(side=tk.LEFT)

        self.mode = ttk.Combobox(frame_mode,
                                 values=["a", "n", "s", "an", "as", "ns", "ans"],
                                 state="readonly")
        self.mode.current(6)
        self.mode.pack(side=tk.LEFT, padx=10)

        self.mode.bind("<<ComboboxSelected>>", self.update_character_fields)

        # ===== ADVANCED =====
        self.advanced = tk.BooleanVar()

        tk.Checkbutton(self.card,
                       text="Advanced Character Rules",
                       variable=self.advanced,
                       command=self.toggle_advanced,
                       bg=CARD,
                       fg=SUBTLE).pack(pady=5)

        self.advanced_container = tk.Frame(self.card, bg=CARD)
        self.char_frame = tk.Frame(self.advanced_container, bg=CARD)

        # IMPORTANT → store ROW FRAMES
        self.upper_row, self.min_upper = self.make_small_input("Min Upper:", "0")
        self.lower_row, self.min_lower = self.make_small_input("Min Lower:", "0")
        self.numeric_row, self.min_numeric = self.make_small_input("Min Numeric:", "0")
        self.special_row, self.min_special = self.make_small_input("Min Special:", "0")

        # ===== BUTTON =====
        self.generate_button = tk.Button(
            self.card,
            text="Generate Password",
            command=self.generate,
            bg=BUTTON,
            fg="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        self.generate_button.pack(pady=15)

        # ===== OUTPUT =====
        self.output = tk.Text(self.card, height=6, bg=BG, fg=ACCENT)
        self.output.pack(padx=10, pady=10, fill="both")

        self.strength_label = tk.Label(self.card, text="Strength: -", bg=CARD, fg=SUBTLE)
        self.strength_label.pack()
        
        tk.Button(self.card, text="👁 Toggle Visibility",
          command=self.toggle_visibility,
          fg="#0f172a", bg="#334155").pack(pady=5)
        
        tk.Button(self.card, text="Copy",
          command=self.copy,
          fg="#0f172a", bg="#334155").pack(pady=5)

    # ================= HELPERS =================
    def make_row(self, label, attr, default, parent=None):
        parent = parent or self.card
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(pady=5)

        tk.Label(frame, text=label, bg=CARD, fg=TEXT).pack(side=tk.LEFT)
        entry = tk.Entry(frame, bg=BG, fg=TEXT)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT, padx=10)

        setattr(self, attr, entry)

    def make_small_input(self, label, default):
        frame = tk.Frame(self.char_frame, bg=CARD)
        entry = tk.Entry(frame, width=5, bg=BG, fg=TEXT)

        tk.Label(frame, text=label, bg=CARD, fg=TEXT).pack(side=tk.LEFT)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT, padx=5)

        return frame, entry

    # ================= LOGIC =================
    def toggle_length(self):
        if self.length_type.get() == "fixed":
            self.frame_range.pack_forget()
            self.frame_fixed.pack()
        else:
            self.frame_fixed.pack_forget()
            self.frame_range.pack()

    def toggle_advanced(self):
        if self.advanced.get():
            self.advanced_container.pack(before=self.generate_button, pady=5)
            self.char_frame.pack()
            self.update_character_fields()
        else:
            self.advanced_container.pack_forget()

    def update_character_fields(self, event=None):
        mode = self.mode.get()

        # hide all
        for widget in self.char_frame.winfo_children():
            widget.pack_forget()

        if "a" in mode:
            self.upper_row.pack(pady=2)
            self.lower_row.pack(pady=2)

        if "n" in mode:
            self.numeric_row.pack(pady=2)

        if "s" in mode:
            self.special_row.pack(pady=2)

    def generate(self):
        try:
            count = int(self.count.get())
            mode = self.mode.get()

            if self.length_type.get() == "fixed":
                specs = build_password_specs(count,
                                             fixed_length=int(self.length.get()),
                                             cli_mode=mode)
            else:
                specs = build_password_specs(
                    count,
                    min_length=int(self.min_length.get()),
                    max_length=int(self.max_length.get()),
                    cli_mode=mode
                )

            pool = build_pool_config(False)

            if self.advanced.get():
                configs = [
                    CharacterConfig(
                        upper=int(self.min_upper.get()),
                        lower=int(self.min_lower.get()),
                        numeric=int(self.min_numeric.get()),
                        special=int(self.min_special.get())
                    )
                    for _ in specs
                ]
            else:
                configs = [CharacterConfig() for _ in specs]

            self.passwords = generate_passwords(specs, configs, pool)
            self.show_passwords = True

            self.display_passwords()

            strength, color = evaluate_strength(self.passwords[0])
            self.strength_label.config(text=f"Strength: {strength}", fg=color)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_passwords(self):
        self.output.delete("1.0", tk.END)
        for i, p in enumerate(self.passwords, 1):
            if self.show_passwords:
                self.output.insert(tk.END, f"{i}: {p}\n")
            else:
                self.output.insert(tk.END, f"{i}: {'•'*len(p)}\n")

    def toggle_visibility(self):
        self.show_passwords = not self.show_passwords
        self.display_passwords()

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(self.passwords))
        messagebox.showinfo("Copied", "Copied!")


# ================= MAIN =================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    SplashScreen(root, 2000)

    def start():
        PasswordGeneratorGUI(root)

    root.after(2000, start)
    root.mainloop()
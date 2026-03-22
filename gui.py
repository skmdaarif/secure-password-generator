import os
import tkinter as tk
from tkinter import ttk, messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "app/assets/passwd-icon.png")

from password_generator.core import (
    build_password_specs,
    build_pool_config,
    generate_passwords,
    CharacterConfig,
    MAX_PASSWORD_COUNT,
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    MAX_TOTAL_CHARACTERS
)

# ===== COLORS =====
BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#22c55e"
TEXT = "#e2e8f0"
SUBTLE = "#94a3b8"
BUTTON = "#16a34a"

def safe_int(value):
    return int(value) if value.strip() != "" else 0

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


class PasswordGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure-Password-Generator")
        self.root.geometry("520x720")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(520, 720)

        self.passwords = []
        self.show_passwords = True

        try:
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        except:
            pass

        tk.Label(root, text="🔐 Secure-Password-Generator",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=15)

        # ===== SCROLLABLE MAIN AREA =====
        container = tk.Frame(root, bg=BG)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.scrollable_frame = tk.Frame(canvas, bg=BG)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        self.canvas_window = canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        def resize_canvas(event):
            canvas.itemconfig(self.canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_canvas)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas = canvas
        
        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down
        
        self.card = tk.Frame(self.scrollable_frame, bg=CARD)
        self.card.pack(padx=20, pady=2, fill="both", expand=True, anchor="n")

        # ===== COUNT =====
        self.make_row("Number of Passwords:", "count", "")
        self.count.insert(0, "5")
        self.count_error = tk.Label(self.card, text="", fg="red", bg=CARD)
        self.count_error.pack()

        # ===== LENGTH TYPE =====
        self.length_type = tk.StringVar(value="fixed")

        frame_type = tk.Frame(self.card, bg=CARD)
        frame_type.pack(pady=(5,2))

        tk.Radiobutton(frame_type, text="Fixed", variable=self.length_type,
                       value="fixed", command=self.toggle_length,
                       bg=CARD, fg=TEXT).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(frame_type, text="Range", variable=self.length_type,
                       value="range", command=self.toggle_length,
                       bg=CARD, fg=TEXT).pack(side=tk.LEFT, padx=10)

        self.length_container = tk.Frame(self.card, bg=CARD)
        self.length_container.pack(pady=(2,2))

        # FIXED
        self.frame_fixed = tk.Frame(self.length_container, bg=CARD)
        self.frame_fixed.pack(pady=0)
        self.make_row("Length:", "length", "", parent=self.frame_fixed)
        self.length.insert(0, "12")
        self.length_error = tk.Label(self.frame_fixed, text="", fg="red", bg=CARD)
        self.length_error.pack()

        # RANGE
        self.frame_range = tk.Frame(self.length_container, bg=CARD)

        tk.Label(self.frame_range, text="Minimum:", bg=CARD, fg=TEXT).pack(side=tk.LEFT)
        self.min_length = tk.Entry(self.frame_range, width=5, bg=BG, fg=TEXT)
        self.min_length.insert(0, "8")
        self.min_length.pack(side=tk.LEFT)

        tk.Label(self.frame_range, text="Maximum:", bg=CARD, fg=TEXT).pack(side=tk.LEFT)
        self.max_length = tk.Entry(self.frame_range, width=5, bg=BG, fg=TEXT)
        self.max_length.insert(0, "256")
        self.max_length.pack(side=tk.LEFT)

        self.range_error = tk.Label(self.card, text="", fg="red", bg=CARD)
        self.range_error.pack()

        self.total_error = tk.Label(self.card, text="", fg="red", bg=CARD)
        self.total_error.pack()

        # ===== MODE =====
        frame_mode = tk.Frame(self.card, bg=CARD)
        frame_mode.pack(pady=(2,5))

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

        self.upper_row, self.min_upper = self.make_small_input("Minimum Upper:", "0")
        self.upper_error = tk.Label(self.char_frame, text="", fg="red", bg=CARD)

        self.lower_row, self.min_lower = self.make_small_input("Minimum Lower:", "0")
        self.lower_error = tk.Label(self.char_frame, text="", fg="red", bg=CARD)

        self.numeric_row, self.min_numeric = self.make_small_input("Minimum Numeric:", "0")
        self.numeric_error = tk.Label(self.char_frame, text="", fg="red", bg=CARD)

        self.special_row, self.min_special = self.make_small_input("Minimum Special:", "0")
        self.special_error = tk.Label(self.char_frame, text="", fg="red", bg=CARD)

        # ===== BUTTON =====
        self.generate_button = tk.Button(
            self.card,
            text="Generate Password",
            command=self.generate,
            bg=BUTTON,
            fg="#0f172a",
            font=("Segoe UI", 10, "bold"),
            state="disabled"
        )
        self.generate_button.pack(pady=15)

        # ===== OUTPUT =====
        output_frame = tk.Frame(self.card, bg=CARD)
        output_frame.pack(padx=10, pady=10, fill="both")

        output_frame = tk.Frame(self.card, bg=CARD)
        output_frame.pack(padx=10, pady=10, fill="both")

        self.output = tk.Text(output_frame, height=6, bg=BG, fg=ACCENT)
        scrollbar = tk.Scrollbar(output_frame, command=self.output.yview)

        self.output.configure(yscrollcommand=scrollbar.set)

        self.output.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scroll = tk.Scrollbar(output_frame, command=self.output.yview)
        scroll.pack(side="right", fill="y")

        self.output.config(yscrollcommand=scroll.set)

        self.strength_label = tk.Label(self.card, text="Strength: -", bg=CARD, fg=SUBTLE)
        self.strength_label.pack()

        tk.Button(self.card, text="👁 Toggle Visibility",
                  command=self.toggle_visibility, bg="#334155").pack(pady=5)

        tk.Button(self.card, text="Copy",
                  command=self.copy, bg="#334155").pack(pady=5)

        # ===== BINDINGS =====
        for widget in [
            self.count, self.length, self.min_length, self.max_length,
            self.min_upper, self.min_lower, self.min_numeric, self.min_special
        ]:
            widget.bind("<KeyRelease>", lambda e: self.validate_inputs())

        self.validate_inputs()
    
    def _on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows / macOS
            self.canvas.yview_scroll(int(-1 * event.delta / 120), "units")

    # ===== HELPERS =====
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

    # ===== LOGIC =====
    def toggle_length(self):
        self.frame_fixed.pack_forget()
        self.frame_range.pack_forget()

        if self.length_type.get() == "fixed":
            self.frame_fixed.pack(pady=0)
        else:
            self.frame_range.pack()

        self.validate_inputs()

    def toggle_advanced(self):
        if self.advanced.get():
            self.advanced_container.pack(before=self.generate_button, pady=5)
            self.char_frame.pack()
            self.update_character_fields()
        else:
            self.advanced_container.pack_forget()
        self.validate_inputs()

    def update_character_fields(self, event=None):
        mode = self.mode.get()

        # clear everything
        for widget in self.char_frame.winfo_children():
            widget.pack_forget()

        # ALPHABETS
        if "a" in mode:
            self.upper_row.pack(pady=2)
            self.upper_error.pack()
            self.lower_row.pack(pady=2)
            self.lower_error.pack()

        # NUMERIC
        if "n" in mode:
            self.numeric_row.pack(pady=2)
            self.numeric_error.pack()

        # SPECIAL
        if "s" in mode:
            self.special_row.pack(pady=2)
            self.special_error.pack()

        # 🔥 IMPORTANT
        self.validate_inputs()

    # ===== VALIDATION =====
    def validate_inputs(self):
        errors = []

        self.count_error.config(text="")
        self.length_error.config(text="")
        self.range_error.config(text="")
        self.total_error.config(text="")

        # COUNT
        try:
            count = int(self.count.get())
            if count <= 0:
                self.count_error.config(text="Number of passwords must be greater than zero")
                errors.append(1)
            elif count > MAX_PASSWORD_COUNT:
                self.count_error.config(text=f"Cannot exceed {MAX_PASSWORD_COUNT}")
                errors.append(1)
        except:
            self.count_error.config(text="Invalid number")
            errors.append(1)

        # LENGTH
        try:
            if self.length_type.get() == "fixed":
                length = int(self.length.get())
                if length < MIN_PASSWORD_LENGTH:
                    self.length_error.config(text=f"Minimum length is {MIN_PASSWORD_LENGTH}")
                    errors.append(1)
                elif length > MAX_PASSWORD_LENGTH:
                    self.length_error.config(text=f"Maximum length is {MAX_PASSWORD_LENGTH}")
                    errors.append(1)
            else:
                min_l = int(self.min_length.get())
                max_l = int(self.max_length.get())

                if min_l < MIN_PASSWORD_LENGTH or max_l < MIN_PASSWORD_LENGTH:
                    self.range_error.config(text=f"Minimum length is {MIN_PASSWORD_LENGTH}")
                    errors.append(1)
                elif min_l > max_l:
                    self.range_error.config(text="Minimum cannot exceed maximum")
                    errors.append(1)
                elif max_l > MAX_PASSWORD_LENGTH:
                    self.range_error.config(text=f"Maximum length is {MAX_PASSWORD_LENGTH}")
                    errors.append(1)
        except:
            self.range_error.config(text="Invalid input")
            errors.append(1)

        # TOTAL LIMIT
        try:
            total = int(self.count.get()) * (
                int(self.length.get()) if self.length_type.get() == "fixed"
                else int(self.max_length.get())
            )
            if total > MAX_TOTAL_CHARACTERS:
                self.total_error.config(text=f"Total characters cannot exceed {MAX_TOTAL_CHARACTERS}")
                errors.append(1)
        except:
            pass

        # ===== ADVANCED VALIDATION =====
        if self.advanced.get():
            try:
                # get total length
                if self.length_type.get() == "fixed":
                    total_length = int(self.length.get())
                else:
                    total_length = int(self.max_length.get())

                mode = self.mode.get()

                upper = lower = numeric = special = 0

                if "a" in mode:
                    upper = int(self.min_upper.get() or 0)
                    lower = int(self.min_lower.get() or 0)

                if "n" in mode:
                    numeric = int(self.min_numeric.get() or 0)

                if "s" in mode:
                    special = int(self.min_special.get() or 0)

                remaining = total_length

                # reset advanced errors
                self.upper_error.config(text="")
                self.lower_error.config(text="")
                self.numeric_error.config(text="")
                self.special_error.config(text="")

                # ---- ALPHABETS ----
                if "a" in mode:
                    if upper > total_length:
                        self.upper_error.config(text="Should not exceed password length")
                        errors.append(1)
                    else:
                        remaining -= upper

                    if lower > remaining:
                        self.lower_error.config(text=f"Total required exceeds password length ({total_length})")
                        errors.append(1)
                    else:
                        remaining -= lower

                # ---- NUMERIC ----
                if "n" in mode:
                    if numeric > remaining:
                        self.numeric_error.config(text=f"Total required exceeds password length ({total_length})")
                        errors.append(1)
                    else:
                        remaining -= numeric

                # ---- SPECIAL ----
                if "s" in mode:
                    if special > remaining:
                        self.special_error.config(text=f"Total required exceeds password length ({total_length})")
                        errors.append(1)
                    else:
                        remaining -= special

            except:
                self.upper_error.config(text="Invalid input")
                self.lower_error.config(text="Invalid input")
                self.numeric_error.config(text="Invalid input")
                self.special_error.config(text="Invalid input")
                errors.append(1)

        self.generate_button.config(state="normal" if not errors else "disabled")

    # ===== CORE =====
    def generate(self):
        try:
            count = int(self.count.get())
            mode = self.mode.get()

            if self.length_type.get() == "fixed":
                specs = build_password_specs(count, fixed_length=int(self.length.get()), cli_mode=mode)
            else:
                specs = build_password_specs(count,
                                             min_length=int(self.min_length.get()),
                                             max_length=int(self.max_length.get()),
                                             cli_mode=mode)

            pool = build_pool_config(False)

            if self.advanced.get():
                configs = [
                    CharacterConfig(
                        upper=safe_int(self.min_upper.get()),
                        lower=safe_int(self.min_lower.get()),
                        numeric=safe_int(self.min_numeric.get()),
                        special=safe_int(self.min_special.get())
                    )
                    for _ in specs
                ]
            else:
                configs = [CharacterConfig() for _ in specs]

            self.passwords = generate_passwords(specs, configs, pool)
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
                self.output.insert(tk.END, f"{i}: {'•' * len(p)}\n")

    def toggle_visibility(self):
        if not self.passwords:
            return  # nothing to toggle

        self.show_passwords = not self.show_passwords
        self.display_passwords()

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(self.passwords))
        messagebox.showinfo("Copied", "Passwords copied successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    SplashScreen(root, 2000)

    root.after(2000, lambda: PasswordGeneratorGUI(root))
    root.mainloop()
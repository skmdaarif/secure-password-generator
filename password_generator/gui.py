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


# ================= SPLASH SCREEN =================
class SplashScreen:
    def __init__(self, root, duration=2000):
        self.root = root
        self.duration = duration

        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.configure(bg=BG)

        width = 400
        height = 250

        x = (self.splash.winfo_screenwidth() // 2) - (width // 2)
        y = (self.splash.winfo_screenheight() // 2) - (height // 2)

        self.splash.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(self.splash,
                 text="🔐 Secure-Password-Generator",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG,
                 fg=ACCENT).pack(pady=40)

        tk.Label(self.splash,
                 text="Launching secure generator...",
                 font=("Segoe UI", 10),
                 bg=BG,
                 fg=SUBTLE).pack(pady=10)

        try:
            img = tk.PhotoImage(file=icon_path)
            tk.Label(self.splash, image=img, bg=BG).pack()
            self.splash.image = img
        except:
            pass

        self.root.after(self.duration, self.close)

    def close(self):
        self.splash.destroy()
        self.root.deiconify()


# ================= MAIN GUI =================
class PasswordGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure-Password-Generator")
        self.root.geometry("520x600")
        self.root.configure(bg=BG)

        # ===== ICON =====
        try:
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        except:
            pass

        # ===== STYLE =====
        style = ttk.Style()
        style.theme_use("clam")

        # FIXED COMBOBOX VISIBILITY
        style.configure("TCombobox",
                        fieldbackground=BG,
                        background=BG,
                        foreground=TEXT)
        style.map("TCombobox",
                fieldbackground=[("readonly", BG)],
                foreground=[("readonly", TEXT)])

        # ===== HEADER =====
        header = tk.Frame(root, bg=BG)
        header.pack(pady=15)

        tk.Label(header,
                 text="🔐 Secure-Password-Generator",
                 font=("Segoe UI", 18, "bold"),
                 bg=BG,
                 fg=ACCENT).pack()

        tk.Label(header,
                 text="Generate strong, secure passwords instantly",
                 font=("Segoe UI", 10),
                 bg=BG,
                 fg=SUBTLE).pack()

        # ===== CARD =====
        self.card = tk.Frame(root, bg=CARD)
        self.card.pack(padx=20, pady=10, fill="both", expand=True)

        # ===== COUNT =====
        self.make_row("Number of Passwords:", "count", "1")

        # ===== LENGTH TYPE =====
        self.length_type = tk.StringVar(value="fixed")

        frame_type = tk.Frame(self.card, bg=CARD)
        frame_type.pack(pady=10)

        tk.Radiobutton(frame_type, text="Fixed",
                       variable=self.length_type,
                       value="fixed",
                       command=self.toggle_length,
                       bg=CARD, fg=TEXT, selectcolor=BG).pack(side=tk.LEFT, padx=10)

        tk.Radiobutton(frame_type, text="Range",
                       variable=self.length_type,
                       value="range",
                       command=self.toggle_length,
                       bg=CARD, fg=TEXT, selectcolor=BG).pack(side=tk.LEFT, padx=10)

        # ===== LENGTH CONTAINER (NEW) =====
        self.length_container = tk.Frame(self.card, bg=CARD)
        self.length_container.pack(pady=5)

        # ===== FIXED =====
        self.frame_fixed = tk.Frame(self.length_container, bg=CARD)
        self.frame_fixed.pack()
        self.make_row("Length:", "length", "12", parent=self.frame_fixed)

        # ===== RANGE =====
        self.frame_range = tk.Frame(self.length_container, bg=CARD)

        tk.Label(self.frame_range, text="Min:", bg=CARD, fg=TEXT).pack(side=tk.LEFT, padx=5)
        self.min_length = tk.Entry(self.frame_range, width=5, bg=BG, fg=TEXT, insertbackground=TEXT)
        self.min_length.insert(0, "8")
        self.min_length.pack(side=tk.LEFT)

        tk.Label(self.frame_range, text="Max:", bg=CARD, fg=TEXT).pack(side=tk.LEFT, padx=5)
        self.max_length = tk.Entry(self.frame_range, width=5, bg=BG, fg=TEXT, insertbackground=TEXT)
        self.max_length.insert(0, "20")
        self.max_length.pack(side=tk.LEFT)

        # ===== MODE =====
        frame_mode = tk.Frame(self.card, bg=CARD)
        frame_mode.pack(pady=10)

        tk.Label(frame_mode, text="Mode:", bg=CARD, fg=TEXT).pack(side=tk.LEFT)

        self.mode = ttk.Combobox(
                            frame_mode,
                            values=["a", "n", "s", "an", "as", "ns", "ans"],
                            state="readonly",
                            width=10,
                            foreground=TEXT)
        self.mode.current(6)
        self.mode.pack(side=tk.LEFT, padx=10)

        # ===== CHECKBOX =====
        self.exclude_ambiguous = tk.BooleanVar()

        tk.Checkbutton(self.card,
                       text="Exclude ambiguous characters",
                       variable=self.exclude_ambiguous,
                       bg=CARD,
                       fg=SUBTLE,
                       selectcolor=BG).pack(pady=5)

        # ===== GENERATE BUTTON (FIXED TEXT VISIBILITY) =====
        tk.Button(self.card,
                  text="Generate Password",
                  command=self.generate,
                  bg=BUTTON,
                  fg="#0f172a",
                  activeforeground="#0f172a",
                  activebackground="#15803d",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat",
                  padx=10,
                  pady=6).pack(pady=15)

        # ===== OUTPUT =====
        self.output = tk.Text(self.card,
                              height=6,
                              bg=BG,
                              fg=ACCENT,
                              insertbackground=TEXT,
                              relief="flat")
        self.output.pack(padx=10, pady=10, fill="both")

        # ===== COPY BUTTON (FIXED) =====
        tk.Button(self.card,
                  text="Copy",
                  command=self.copy,
                  bg="#334155",
                  fg="#0f172a",
                  activeforeground="#ffffff",
                  activebackground="#475569",
                  relief="flat").pack(pady=5)

        # ===== FOOTER =====
        tk.Label(root,
                 text="Built by Sheikh Md Aarif",
                 bg=BG,
                 fg=SUBTLE,
                 font=("Segoe UI", 8)).pack(pady=5)

    def make_row(self, label, attr, default, parent=None):
        parent = parent or self.card
        frame = tk.Frame(parent, bg=CARD)
        frame.pack(pady=5)

        tk.Label(frame, text=label, bg=CARD, fg=TEXT).pack(side=tk.LEFT)

        entry = tk.Entry(frame, bg=BG, fg=TEXT, insertbackground=TEXT)
        entry.insert(0, default)
        entry.pack(side=tk.LEFT, padx=10)

        setattr(self, attr, entry)

    def toggle_length(self):
        if self.length_type.get() == "fixed":
            self.frame_range.pack_forget()
            self.frame_fixed.pack()
        else:
            self.frame_fixed.pack_forget()
            self.frame_range.pack()

    def generate(self):
        try:
            count = int(self.count.get())
            mode = self.mode.get()

            if self.length_type.get() == "fixed":
                length = int(self.length.get())
                specs = build_password_specs(count, fixed_length=length, cli_mode=mode)
            else:
                min_len = int(self.min_length.get())
                max_len = int(self.max_length.get())

                if min_len > max_len:
                    raise ValueError("Min length > Max length")

                specs = build_password_specs(
                    count,
                    min_length=min_len,
                    max_length=max_len,
                    cli_mode=mode
                )

            pool = build_pool_config(self.exclude_ambiguous.get())
            configs = [CharacterConfig() for _ in specs]

            passwords = generate_passwords(specs, configs, pool)

            self.output.delete("1.0", tk.END)
            for i, p in enumerate(passwords, 1):
                self.output.insert(tk.END, f"{i}: {p}\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copy(self):
        text = self.output.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Copied to clipboard!")


# ================= MAIN =================
if __name__ == "__main__":
    root = tk.Tk()

    root.withdraw()

    SplashScreen(root, duration=2000)

    def start_app():
        PasswordGeneratorGUI(root)

    root.after(2000, start_app)

    root.mainloop()
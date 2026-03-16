# Secure Password Generator CLI

A small command-line tool written in Python for generating secure passwords.

It uses Python's `secrets` module to produce cryptographically secure randomness and allows users to customize password length, character types, and other password rules.

---

## Features

- Generates cryptographically secure passwords
- Customizable password length
- Optional minimum counts for different character types
- Interactive mode with prompts
- Non-interactive mode using command-line arguments
- Option to exclude ambiguous characters (`0`, `O`, `o`, `1`, `l`, `I`)
- Ability to generate multiple passwords at once

---

## Installation

Clone the repository:

```bash
git clone https://github.com/skmdaarif/secure-password-generator.git
cd secure-password-generator
```

No external dependencies are required. The program uses only Python’s standard library.

---

## Usage

### Interactive Mode

Run the program without arguments:

```bash
python password_generator.py
```

The program will guide you through password configuration using prompts.

---

### Non-Interactive Mode

You can generate passwords directly using command-line arguments.

Example:

```bash
python password_generator.py --count 3 --length 12 --mode ans --non-interactive
```

This generates **3 passwords**, each **12 characters long**, containing **alphabetic**, **numeric**, and **special characters**.

---

## Example Output

```
Secure Password Generator CLI
--------------------------------

Generated Passwords
-------------------
1: Q#9sK@d1Lp
2: T8!x$QmP4z
3: W@2mF#s7Zq
```

---

## Technologies Used

- Python
- argparse
- dataclasses
- secrets module

---

## License

This project is licensed under the MIT License.
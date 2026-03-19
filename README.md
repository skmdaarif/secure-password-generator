# Secure Password Generator CLI

A lightweight command-line tool for generating secure, customizable passwords.

Built using Python’s `secrets` module, this tool provides cryptographically secure randomness along with flexible configuration options for password length, character types, and constraints.

---

## Features

* Cryptographically secure password generation
* Configurable password length
* Support for minimum character constraints (uppercase, lowercase, numeric, special)
* Interactive mode with guided prompts
* Non-interactive mode using command-line arguments
* Option to exclude ambiguous characters (`0`, `O`, `o`, `1`, `l`, `I`)
* Generate multiple passwords in a single command

---

## Installation

Clone the repository and install locally:

```bash
git clone https://github.com/skmdaarif/secure-password-generator.git
cd secure-password-generator
pip install -e .
```

No external dependencies are required — uses only Python’s standard library.

---

## Usage

### CLI Command (Recommended)

Once installed, use:

```bash
spg
```

---

### Interactive Mode

Run without arguments:

```bash
spg
```

The program will guide you through password configuration step by step.

---

### Non-Interactive Mode

Generate passwords directly using arguments:

```bash
spg --count 3 --length 12 --mode ans --non-interactive
```

This generates **3 passwords**, each **12 characters long**, containing **alphabetic**, **numeric**, and **special characters**.

---

### Alternative (Without Installation)

You can also run the tool as a module:

```bash
python3 -m password_generator.cli
```

## GUI Version

Run the desktop app:

```bash
python3 gui.py
```

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

* Python
* argparse
* dataclasses
* secrets module

---

## License

This project is licensed under the MIT License.

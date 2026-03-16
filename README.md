# Secure Password Generator CLI

A small command-line tool written in Python for generating secure passwords.

It uses Python's `secrets` module to produce cryptographically secure randomness and allows users to customize password length, character types, and other basic rules.

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
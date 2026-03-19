"""
Secure Password Generator CLI

Features:
- Cryptographically secure password generation
- Configurable password policies
- Interactive and non-interactive modes
- CLI argument support

Author: Sheikh Md Aarif Al Zubair
"""

from __future__ import annotations

import argparse
import secrets
import string
from dataclasses import dataclass
from typing import Callable, TypeAlias, TypeVar

VALID_MODES = {"a", "n", "s", "an", "as", "ns", "ans"}
YES_NO_ERROR = "Please enter y or n."
MIN_PASSWORD_LENGTH = 5
AMBIGUOUS_CHARACTERS = set("0Oo1lI")
secure_random = secrets.SystemRandom()
T = TypeVar("T")


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the password generator."""

    parser = argparse.ArgumentParser(
        description=(
            "Secure Password Generator CLI\n\n"
            "Features:\n"
            "- Cryptographically secure password generation\n"
            "- Configurable password policies\n"
            "- Interactive and non-interactive modes\n"
            "- CLI argument support\n\n"
            "Author: Sheikh Md Aarif Al Zubair"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Number of passwords to generate",
    )

    parser.add_argument(
        "--length",
        type=int,
        default=None,
        help="Password length",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=sorted(VALID_MODES),
        default=None,
        help="Password mode",
    )

    parser.add_argument(
        "--exclude-ambiguous",
        action="store_true",
        help="Exclude ambiguous characters (0, O, o, 1, l, I)",
    )

    parser.add_argument(
        "--min-upper",
        type=int,
        default=None,
        help="Minimum uppercase alphabetic characters",
    )

    parser.add_argument(
        "--min-lower",
        type=int,
        default=None,
        help="Minimum lowercase alphabetic characters",
    )

    parser.add_argument(
        "--min-numeric",
        type=int,
        default=None,
        help="Minimum numeric characters",
    )

    parser.add_argument(
        "--min-special",
        type=int,
        default=None,
        help="Minimum special characters",
    )

    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run without interactive prompts; requires --count, --length, and --mode",
    )

    return parser


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    """Parse command-line arguments for the password generator."""

    parser = build_parser()
    return parser, parser.parse_args()


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    """Validate parsed command-line arguments."""

    if args.count is not None and args.count < 1:
        parser.error("--count must be greater than or equal to 1.")

    if args.length is not None and args.length < MIN_PASSWORD_LENGTH:
        parser.error(f"--length must be greater than or equal to {MIN_PASSWORD_LENGTH}.")

    minimum_fields = {
        "--min-upper": args.min_upper,
        "--min-lower": args.min_lower,
        "--min-numeric": args.min_numeric,
        "--min-special": args.min_special,
    }
    for name, value in minimum_fields.items():
        if value is not None and value < 0:
            parser.error(f"{name} must be greater than or equal to 0.")

    if args.non_interactive:
        missing = []

        if args.count is None:
            missing.append("--count")

        if args.length is None:
            has_range = (
                hasattr(args, "min_length") and hasattr(args, "max_length")
                and args.min_length is not None and args.max_length is not None
            )
            if not has_range:
                missing.append("--length")

        if args.mode is None:
            missing.append("--mode")

        if missing:
            parser.error("--non-interactive requires " + ", ".join(missing) + ".")


@dataclass(frozen=True)
class FixedLengthConfig:
    """A fixed password length configuration.

    Attributes:
        length: The exact length every password should use.
    """

    length: int


@dataclass(frozen=True)
class RangeLengthConfig:
    """A ranged password length configuration.

    Attributes:
        minimum: The inclusive lower bound for password length.
        maximum: The inclusive upper bound for password length.
    """

    minimum: int
    maximum: int


LengthConfig: TypeAlias = FixedLengthConfig | RangeLengthConfig


@dataclass(frozen=True)
class CharacterConfig:
    """Minimum counts required for each character category.

    Attributes:
        upper: Minimum uppercase alphabetic characters.
        lower: Minimum lowercase alphabetic characters.
        numeric: Minimum numeric characters.
        special: Minimum special characters.
    """

    upper: int = 0
    lower: int = 0
    numeric: int = 0
    special: int = 0

    def total(self) -> int:
        """Return the sum of all minimum required characters."""

        return self.upper + self.lower + self.numeric + self.special

    def for_mode(self, mode: str) -> CharacterConfig:
        """Return a mode-compatible character config.

        Args:
            mode: Password mode such as ``a``, ``an``, or ``ans``.

        Returns:
            A new config with values zeroed for categories not present in ``mode``.
        """

        return CharacterConfig(
            upper=self.upper if "a" in mode else 0,
            lower=self.lower if "a" in mode else 0,
            numeric=self.numeric if "n" in mode else 0,
            special=self.special if "s" in mode else 0,
        )


@dataclass(frozen=True)
class PasswordSpec:
    """Configuration for generating one password.

    Attributes:
        length: Final password length.
        mode: Password mode controlling allowed character categories.
    """

    length: int
    mode: str


@dataclass(frozen=True)
class PoolConfig:
    """Character pools used for password generation.

    Attributes:
        uppercase: Available uppercase alphabetic characters.
        lowercase: Available lowercase alphabetic characters.
        numeric: Available numeric characters.
        special: Available special characters.
    """

    uppercase: str
    lowercase: str
    numeric: str
    special: str

    def for_mode(self, mode: str) -> str:
        """Build the combined pool for the requested mode.

        Args:
            mode: Password mode such as ``a``, ``an``, or ``ans``.

        Returns:
            A string containing all characters allowed by the mode.
        """

        pools = []
        if "a" in mode:
            pools.extend([self.uppercase, self.lowercase])
        if "n" in mode:
            pools.append(self.numeric)
        if "s" in mode:
            pools.append(self.special)
        return "".join(pools)


def prompt_user(prompt: str, add_newline: bool = True) -> str:
    """Prompt the user and optionally print a trailing blank line.

    Args:
        prompt: Text shown to the user.
        add_newline: Whether to print a blank line after input is received.

    Returns:
        The stripped user input.
    """

    value = input(prompt).strip()
    if add_newline:
        print()
    return value


def ask_yes_no(prompt: str) -> bool:
    """Ask a yes/no question until a valid answer is received.

    Args:
        prompt: The yes/no prompt text.

    Returns:
        ``True`` for ``y`` and ``False`` for ``n``.
    """

    while True:
        choice = prompt_user(prompt).lower()
        if choice == "y":
            return True
        if choice == "n":
            return False
        print(YES_NO_ERROR)


def get_positive_number(prompt: str, minimum: int = 1, compact: bool = False) -> int:
    """Read an integer greater than or equal to a minimum value.

    Args:
        prompt: Prompt shown to the user.
        minimum: Minimum accepted value.
        compact: Whether to suppress the extra blank line after input.

    Returns:
        A validated integer.
    """

    while True:
        raw_value = prompt_user(prompt, add_newline=not compact)
        if not raw_value.isdigit():
            print("Please enter a valid positive number.")
            continue

        value = int(raw_value)
        if value < minimum:
            print(f"Please enter a number greater than or equal to {minimum}.")
            continue

        return value


def get_password_count(cli_count: int | None = None) -> int:
    """Ask how many passwords to generate.

    Args:
        cli_count: Optional password count provided on the command line.

    Returns:
        The number of passwords requested by the user.
    """

    if cli_count is not None:
        return cli_count

    return get_positive_number("Enter number of passwords to generate: ")


def collect_shared_or_individual(
    password_count: int,
    shared_prompt: str,
    item_heading: str,
    getter: Callable[[], T],
) -> list[T]:
    """Collect one shared value or one value per password."""

    if password_count == 1:
        return [getter()]

    if ask_yes_no(shared_prompt):
        shared_value = getter()
        return [shared_value for _ in range(password_count)]

    values = []
    for index in range(1, password_count + 1):
        print(f"\nPassword {index} {item_heading}")
        values.append(getter())
    return values


def should_exclude_ambiguous_characters() -> bool:
    """Ask whether ambiguous characters should be excluded.

    Returns:
        ``True`` if ambiguous characters should be removed from pools.
    """

    return ask_yes_no("Exclude ambiguous characters (0, O, o, 1, l, I)? (y/n): ")


def build_pool_config(exclude_ambiguous: bool) -> PoolConfig:
    """Create the character pools used for generation.

    Args:
        exclude_ambiguous: Whether ambiguous characters should be removed.

    Returns:
        A ``PoolConfig`` instance with the active character pools.
    """

    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    numeric = string.digits
    special = string.punctuation

    if exclude_ambiguous:
        uppercase = "".join(char for char in uppercase if char not in AMBIGUOUS_CHARACTERS)
        lowercase = "".join(char for char in lowercase if char not in AMBIGUOUS_CHARACTERS)
        numeric = "".join(char for char in numeric if char not in AMBIGUOUS_CHARACTERS)

    return PoolConfig(
        uppercase=uppercase,
        lowercase=lowercase,
        numeric=numeric,
        special=special,
    )


def get_length_mode() -> str:
    """Ask whether password lengths are fixed or ranged.

    Returns:
        ``f`` for fixed length or ``r`` for range length.
    """

    while True:
        choice = prompt_user("Should passwords have fixed length or range length? (f/r): ").lower()
        if choice in {"f", "r"}:
            return choice
        print("Please enter f or r.")


def get_fixed_length_config() -> FixedLengthConfig:
    """Read a fixed password length configuration.

    Returns:
        A ``FixedLengthConfig`` instance.
    """

    length = get_positive_number(
        "Enter fixed password length: ", minimum=MIN_PASSWORD_LENGTH
    )
    return FixedLengthConfig(length=length)


def get_range_length_config() -> RangeLengthConfig:
    """Read a ranged password length configuration.

    Returns:
        A ``RangeLengthConfig`` instance.
    """

    while True:
        minimum = get_positive_number(
            "Enter minimum password length: ", minimum=MIN_PASSWORD_LENGTH
        )
        maximum = get_positive_number(
            "Enter maximum password length: ", minimum=MIN_PASSWORD_LENGTH
        )

        if maximum < minimum + 1:
            print("Maximum length must be at least minimum length + 1.")
            continue

        return RangeLengthConfig(minimum=minimum, maximum=maximum)


def get_length_config(length_mode: str) -> LengthConfig:
    """Read the selected length configuration.

    Args:
        length_mode: ``f`` for fixed length or ``r`` for range length.

    Returns:
        A concrete ``LengthConfig`` instance.
    """

    if length_mode == "f":
        return get_fixed_length_config()
    return get_range_length_config()


def resolve_length(length_config: LengthConfig) -> int:
    """Resolve a final password length from a length configuration.

    Args:
        length_config: Fixed or ranged length configuration.

    Returns:
        The final password length.
    """

    if isinstance(length_config, FixedLengthConfig):
        return length_config.length

    span = length_config.maximum - length_config.minimum + 1
    return length_config.minimum + secrets.randbelow(span)


def collect_password_lengths(
    password_count: int, fixed_length: int | None = None
) -> list[int]:
    """Collect final lengths for each password.

    Args:
        password_count: Number of passwords to generate.
        fixed_length: Optional fixed password length from the command line.

    Returns:
        A list of resolved lengths, one per password.
    """

    if fixed_length is not None:
        return [fixed_length for _ in range(password_count)]

    if password_count == 1:
        return [resolve_length(get_length_config(get_length_mode()))]

    same_length_config = ask_yes_no(
        "Should all passwords use the same length config? (y/n): "
    )

    if same_length_config:
        length_mode = get_length_mode()
        length_config = get_length_config(length_mode)
        if isinstance(length_config, FixedLengthConfig):
            shared_length = resolve_length(length_config)
            return [shared_length for _ in range(password_count)]

        same_length = ask_yes_no("Should all passwords have the same length? (y/n): ")
        if same_length:
            shared_length = resolve_length(length_config)
            return [shared_length for _ in range(password_count)]
        return [resolve_length(length_config) for _ in range(password_count)]

    length_mode = get_length_mode()
    if length_mode == "r":
        length_config = get_length_config(length_mode)
        return [resolve_length(length_config) for _ in range(password_count)]

    lengths = []
    for index in range(1, password_count + 1):
        print(f"\nPassword {index} length")
        lengths.append(resolve_length(get_fixed_length_config()))
    return lengths


def get_mode() -> str:
    """Ask for a password mode.

    Returns:
        A validated mode string.
    """

    prompt = "Choose password mode (a, n, s, an, as, ns, ans): "
    while True:
        mode = prompt_user(prompt).lower()
        if mode in VALID_MODES:
            return mode
        print("Invalid mode. Use one of: a, n, s, an, as, ns, ans.")


def collect_password_modes(password_count: int, cli_mode: str | None = None) -> list[str]:
    """Collect modes for each password.

    Args:
        password_count: Number of passwords to generate.
        cli_mode: Optional shared password mode from the command line.

    Returns:
        A list of modes, one per password.
    """

    if cli_mode is not None:
        return [cli_mode for _ in range(password_count)]

    return collect_shared_or_individual(
        password_count,
        "Should all passwords use the same mode? (y/n): ",
        "mode",
        get_mode,
    )

def get_character_config(length: int, mode: str) -> CharacterConfig:
    """Collect minimum character requirements for one password.

    Args:
        length: The password length.
        mode: The password mode.

    Returns:
        A validated ``CharacterConfig`` instance.
    """

    while True:
        print("Set minimum character counts for this password.")

        upper = lower = numeric = special = 0
        if "a" in mode:
            upper = get_positive_number(
                "Enter minimum number of uppercase alphabetic characters: ",
                minimum=0,
                compact=True,
            )
            lower = get_positive_number(
                "Enter minimum number of lowercase alphabetic characters: ",
                minimum=0,
                compact=True,
            )
        if "n" in mode:
            numeric = get_positive_number(
                "Enter minimum number of numeric characters: ",
                minimum=0,
                compact=True,
            )
        if "s" in mode:
            special = get_positive_number(
                "Enter minimum number of special characters: ",
                minimum=0,
                compact=True,
            )

        config = CharacterConfig(
            upper=upper,
            lower=lower,
            numeric=numeric,
            special=special,
        )
        if config.total() <= length:
            return config

        print("Total minimum character counts cannot be greater than password length.")


def build_character_config_for_mode(
    mode: str,
    upper: int = 0,
    lower: int = 0,
    numeric: int = 0,
    special: int = 0,
) -> CharacterConfig:
    """Build a character config compatible with a password mode."""

    return CharacterConfig(
        upper=upper if "a" in mode else 0,
        lower=lower if "a" in mode else 0,
        numeric=numeric if "n" in mode else 0,
        special=special if "s" in mode else 0,
    )


def build_cli_character_config(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
    password_spec: PasswordSpec,
) -> CharacterConfig:
    """Build character config from CLI arguments."""

    requested = CharacterConfig(
        upper=args.min_upper or 0,
        lower=args.min_lower or 0,
        numeric=args.min_numeric or 0,
        special=args.min_special or 0,
    )
    mode_specific_config = build_character_config_for_mode(
        password_spec.mode,
        upper=requested.upper,
        lower=requested.lower,
        numeric=requested.numeric,
        special=requested.special,
    )

    incompatible_fields = []
    if requested.upper and "a" not in password_spec.mode:
        incompatible_fields.append("--min-upper")
    if requested.lower and "a" not in password_spec.mode:
        incompatible_fields.append("--min-lower")
    if requested.numeric and "n" not in password_spec.mode:
        incompatible_fields.append("--min-numeric")
    if requested.special and "s" not in password_spec.mode:
        incompatible_fields.append("--min-special")
    if incompatible_fields:
        parser.error(
            f"{', '.join(incompatible_fields)} cannot be used with mode {password_spec.mode!r}."
        )

    if mode_specific_config.total() > password_spec.length:
        parser.error(
            "Minimum character requirements cannot be greater than password length."
        )

    return mode_specific_config


def adapt_shared_character_config(
    shared_config: CharacterConfig, password_spec: PasswordSpec
) -> CharacterConfig | None:
    """Adapt shared character requirements to a specific password mode.

    Args:
        shared_config: Shared minimum character requirements.
        password_spec: Password spec to adapt the config for.

    Returns:
        A compatible ``CharacterConfig`` or ``None`` if the config cannot fit.
    """

    mode_specific_config = shared_config.for_mode(password_spec.mode)
    if mode_specific_config.total() > password_spec.length:
        return None
    return mode_specific_config


def build_character_pool(mode: str, pool_config: PoolConfig) -> str:
    """Build the combined character pool for a mode.

    Args:
        mode: Password mode.
        pool_config: Active character pools.

    Returns:
        A string containing all allowed characters for the mode.
    """

    return pool_config.for_mode(mode)


def generate_password(
    password_spec: PasswordSpec,
    character_config: CharacterConfig,
    pool_config: PoolConfig,
) -> str:
    """Generate one password from the supplied settings.

    Args:
        password_spec: Final password length and mode.
        character_config: Minimum character requirements.
        pool_config: Active character pools.

    Returns:
        A generated password.
    """

    characters: list[str] = []

    if "a" in password_spec.mode:
        characters.extend(
            secrets.choice(pool_config.uppercase) for _ in range(character_config.upper)
        )
        characters.extend(
            secrets.choice(pool_config.lowercase) for _ in range(character_config.lower)
        )
    if "n" in password_spec.mode:
        characters.extend(
            secrets.choice(pool_config.numeric) for _ in range(character_config.numeric)
        )
    if "s" in password_spec.mode:
        characters.extend(
            secrets.choice(pool_config.special) for _ in range(character_config.special)
        )

    remaining_length = password_spec.length - len(characters)
    combined_pool = build_character_pool(password_spec.mode, pool_config)
    characters.extend(secrets.choice(combined_pool) for _ in range(remaining_length))

    secure_random.shuffle(characters)
    return "".join(characters)


def collect_character_configs(
    password_specs: list[PasswordSpec],
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
) -> list[CharacterConfig] | None:
    """Collect character configuration for each password spec.

    Args:
        password_specs: Password specifications to configure.
        args: Parsed command-line arguments.

    Returns:
        A list of character configs matching ``password_specs``, or ``None``
        when shared config requirements cannot fit all specs.
    """

    if args.non_interactive:
        return [build_cli_character_config(parser, args, spec) for spec in password_specs]

    if not ask_yes_no("Do you want character config? (y/n): "):
        return [CharacterConfig() for _ in password_specs]

    if len(password_specs) == 1:
        spec = password_specs[0]
        return [get_character_config(spec.length, spec.mode)]

    if ask_yes_no("Should all passwords use the same character config? (y/n): "):
        shared_config = get_character_config(password_specs[0].length, password_specs[0].mode)
        character_configs = []
        for spec in password_specs:
            config = adapt_shared_character_config(shared_config, spec)
            if config is None:
                print("Shared character config does not fit every password length and mode.")
                return None
            character_configs.append(config)
        return character_configs

    character_configs = []
    for index, spec in enumerate(password_specs, start=1):
        print(f"\nCharacter config for password {index}")
        character_configs.append(get_character_config(spec.length, spec.mode))
    return character_configs


def generate_passwords(
    password_specs: list[PasswordSpec],
    character_configs: list[CharacterConfig],
    pool_config: PoolConfig,
) -> list[str]:
    """Generate passwords from reusable configuration objects.

    Args:
        password_specs: Final password specifications.
        character_configs: Character requirements matching the specs.
        pool_config: Active character pools.

    Returns:
        A list of generated passwords.
    """

    return [
        generate_password(password_spec, character_config, pool_config)
        for password_spec, character_config in zip(password_specs, character_configs)
    ]

def build_password_specs(
    password_count: int,
    fixed_length: int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    cli_mode: str | None = None,
) -> list[PasswordSpec]:
    """Build the final password specifications.

    Supports:
    - CLI (interactive + non-interactive)
    - GUI fixed
    - GUI range (secure)
    """

    # ✅ GUI RANGE
    if min_length is not None and max_length is not None:
        span = max_length - min_length + 1
        lengths = [
            min_length + secrets.randbelow(span)
            for _ in range(password_count)
        ]

    # ✅ GUI FIXED (important: skip CLI prompts)
    elif fixed_length is not None and cli_mode is not None:
        # this condition = GUI or non-interactive CLI
        lengths = [fixed_length for _ in range(password_count)]

    # ✅ CLI (interactive or mixed)
    else:
        lengths = collect_password_lengths(
            password_count,
            fixed_length=fixed_length
        )

    modes = collect_password_modes(password_count, cli_mode=cli_mode)

    return [
        PasswordSpec(length=length, mode=mode)
        for length, mode in zip(lengths, modes)
    ]

def run_cli() -> None:
    """Run the interactive CLI application."""

    parser, args = parse_args()
    validate_args(parser, args)
    print("Secure Password Generator CLI")
    print("--------------------------------")
    password_count = get_password_count(args.count)
    exclude_ambiguous = (
        args.exclude_ambiguous
        if args.non_interactive
        else should_exclude_ambiguous_characters()
    )
    pool_config = build_pool_config(exclude_ambiguous)
    password_specs = build_password_specs(
        password_count,
        fixed_length=args.length,
        cli_mode=args.mode,
    )
    character_configs = collect_character_configs(password_specs, args, parser)

    if character_configs is None:
        return

    passwords = generate_passwords(password_specs, character_configs, pool_config)
    print("\nGenerated Passwords")
    print("-------------------")
    for index, password in enumerate(passwords, start=1):
        print(f"{index}: {password}")

__all__ = [
    "RULES_DIR",
    "DISABLE_KEYS",
    "LINTER_REGEX",
    "load_settings",
    "SETTINGS",
    "encode",
    "decode",
    "wrap",
    "lint",
    "fix"
]

from pathlib import Path
import json
import subprocess
import sys
import re
import base64

RULES_DIR = Path(__file__).parent / "rules"
DISABLE_KEYS = {
    'flake8': '--ignore',
    'ruff': '--ignore',
    'pylint': '--disable'
}
LINTER_REGEX = {
    'flake8': r"^stdin:(\d+):(\d+):\s+([A-Z]\d{3})\s+(.*)$",
    'ruff': r"^\S+:(\d+):(\d+):\s+([A-Z]+\d+)\s+(.+)$",
    'pylint': r"^\S+:(\d+):(\d+):\s+([A-Z]\d+)\s+(.+)$"
}


def load_settings(linter: str) -> dict:
    """Load linter settings from the corresponding JSON file."""
    with open(RULES_DIR / f"{linter.lower()}.json", 'r') as f:
        return json.load(f)


SETTINGS = {
    'flake8': load_settings('flake8'),
    'ruff': load_settings('ruff'),
    'pylint': load_settings('pylint')
}


def encode(disabled: list, linter: str = 'flake8') -> str:
    disabled = set(disabled)
    settings = SETTINGS[linter]

    binary = ''.join(
        '1' if code in disabled else '0' for code in settings)  # O(n)
    encoded = base64.urlsafe_b64encode(
        int(binary, 2).to_bytes((len(binary) + 7) // 8, 'big')).decode()

    return {'link': encoded.strip('=')}


def decode(code: str, linter: str = 'flake8') -> dict:
    settings = SETTINGS[linter]

    if code == "":
        return settings

    total_errors = len(settings)
    decoded_bytes = base64.urlsafe_b64decode(code + '==='[:len(code) % 4])
    n = int.from_bytes(decoded_bytes, 'big')
    binary = bin(n)[2:].zfill(total_errors)

    for index, rule in enumerate(settings):
        settings[rule]['value'] = binary[index] == '0'

    return settings


def wrap(output: str, linter: str = 'flake8') -> dict[str]:
    pattern = re.compile(LINTER_REGEX[linter.lower()], re.MULTILINE)
    return {'errors': [match.groups() for match in pattern.finditer(output)]}


def lint(code: str, disable: list = None, linter: str = 'flake8') -> dict[str]:
    linter = linter.lower()
    command = [sys.executable, "-m", linter]

    if linter == "ruff":
        command.append("check")

    command.append("-")

    if disable:
        command.append(DISABLE_KEYS[linter] + '=' + ','.join(disable))

    process = subprocess.Popen(command,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

    output = process.communicate(code.encode())[0].decode()
    return wrap(output, linter)


def fix(code: str) -> dict[str, str]:
    process = subprocess.Popen(["autopep8",
                                "--aggressive",
                                "--aggressive",
                                "-"],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)
    output = process.communicate(code.encode())[0].decode()

    return {"code": output}

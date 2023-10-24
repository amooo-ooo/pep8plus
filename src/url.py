from pathlib import Path
import json
RULES_DIR = Path(Path(__file__).parent, "rules")

def encode(disabled: list, chars: str, linter: str = 'flake8') -> str:
    linter = linter.lower()

    # set settings based on linter
    with open(Path(RULES_DIR, linter+'.json'), 'r') as f:
        settings = json.loads(f.read())

    binary = ''
    for category in settings:
        for code in settings[category]:
             binary += str(int(code in disabled))
             if code in disabled:
                 print(code)
    n = int(binary, 2)
        
    e = len(chars)

    if n <= e: return chars[n]
    digits = []
    while n:
        n, remainder = divmod(n, e)
        digits.append(chars[remainder])

    return ''.join(digits[::-1])


def decode(code: str, chars: str, linter: str) -> dict:
    linter = linter.lower()

    # set settings based on linter
    with open(Path(RULES_DIR, linter+'.json'), 'r') as f:
        settings = json.loads(f.read())

    if code == 'all':
        return settings
    
    total_errors = len(settings.values())

    n = 0
    for char in code:
        n = n * len(chars) + chars.index(char)

    n = str(bin(n)[2:])
    n = '0'*(total_errors-len(n)+1) + n

    index = 0
    for category in settings:
        print(len(settings[category]))
        for code in settings[category]:
            settings[category][code]['value'] = not bool(int(n[index-1]))
            index += 1

    return settings

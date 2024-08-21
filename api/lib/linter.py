from pathlib import Path
import subprocess
import uuid
import os

TEMP_PATH = Path(Path(__file__).parent, "temp")
IS_WINDOWS = os.name == 'nt'

def wrap(output: str, linter: str = 'flake8') -> dict[str]:
    output = output.splitlines()
    linter = linter.lower()

    if linter == 'pylint':
        # Filter and convert to format
        errors = tuple(output[1:-4])
        info = {'errors': [i.replace(': ', ':').split(':')[1:]
                           for i in errors]}
        return info

    if linter == 'flake8' or linter == 'ruff':
        if linter == 'ruff': output = output[:-1]
        index = 1 if linter == 'ruff' else 2        
        info = [i.replace(':', ' ').split()[index:] for i in output]
        info = [i[:3] + [' '.join(i[3:])] for i in info]

        return {'errors': info}


def lint(code: str, disable: list = None, linter: str = 'flake8') -> dict[str]:
    linter = linter.lower()
    tempfile = Path(TEMP_PATH, str(uuid.uuid4()) + ".py")
    os.makedirs(os.path.dirname(tempfile), exist_ok=True)
    with open(tempfile, 'w') as f:
        f.write(code)

    disable_key = {'flake8': '--ignore',
                   'ruff': '--ignore',
                   'pylint': '--disable'}

    command = ["py", "-m", linter]
    if linter == "ruff":
        command.append("check")
    command.append(str(tempfile))

    if disable:
        command.append(disable_key[linter] + '=' + ','.join(disable))

    result = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output = wrap(result.stdout.decode('utf-8'), linter)
    os.remove(tempfile)

    return output

def fix(code: str) -> dict[str]:
    tempfile = Path(TEMP_PATH, str(uuid.uuid4()) + ".py")
    os.makedirs(os.path.dirname(tempfile), exist_ok=True)
    with open(tempfile, 'w') as f:
        f.write(code)

    fixed = subprocess.run(f"autopep8 --aggressive --aggressive {tempfile}", 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE).stdout.decode('utf-8')
    os.remove(tempfile)

    return { "code": fixed }

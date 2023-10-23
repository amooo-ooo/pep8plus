import subprocess
import tempfile
import os
import time

def wrap(output: str, linter: str = 'flake8'):
    output = output.splitlines()
    linter = linter.lower()

    if linter == 'pylint':
        # Filter and convert to format
        errors = tuple(output[1:-4])
        info = {'errors': [i.replace(': ',':').split(':')[2:] for i in errors],
                'rating': output[-2].split()[6]}
    
        return info

    if linter == 'flake8' or linter == 'ruff':
        if linter == 'ruff':
            output = output[:-2]
        info = [i.replace(':', ' ').split()[2:] for i in output]
        info = [i[:3] + [' '.join(i[3:])] for i in info]

        return {'errors':info}

def lint(code:str, disable: list = None, linter: str = 'flake8') -> dict:
    linter = linter.lower()
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(code)
        temp_filename = temp.name
    
    disable_key = {'flake8':'--ignore',
                   'ruff':'--ignore',
                   'pylint':'--disable'}

    command = [linter, temp_filename]

    if disable:
        command.append(disable_key[linter] + '=' + ','.join(disable))   
    
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = wrap(result.stdout.decode('utf-8'), linter)
    os.remove(temp_filename)

    return output
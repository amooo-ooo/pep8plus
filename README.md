<p align="center">
    <img src="https://raw.githubusercontent.com/amooo-ooo/pep8plus/main/example.png" alt="pep8plus logo" width="630">
</p>
<h2 align="center">pep8plus</h2>

<p align="center">
  Online Python syntax checker for educational institutions.
</p>

# pep8plus

pep8plus is an open-source online tool built for educational institutions to help students enforce and maintain Python programming standards. Powered by Ruff, Flake8 and Pylint, pep8plus is built on the principle of customisability, ease of use and user experience. 

> **Warning**
> This project is still in its early stages. Hence, bugs and ironically, questionable programming practices may be present.


## Features

Here are a few major features of pep8plus: 

- Customisation:
pep8plus offers three different popular linters: Ruff, Pylint and Flake8. With over 1000 built-in convention guides and rules combined, all convention settings are able to be easily activated and deactivated to share with students.
- Shareability:
Easily share customised convention settings with students by generating a custom link.
- Open-source:
pep8plus gives the opportunity for institutions to host the project and implement their own conventions and plugins.
- Customised Themes:
pep8plus by default supports dark mode and light mode however it's dynamic programming allows locally hosted checkers to easily implement their own themes.

and more!

# Categories
Convention rules are given tags which are colour-coded based on their severity.

| Colour        | Severity          | Description                                                               | 
| ------------- | ----------------- | ------------------------------------------------------------------------- |
| `red`         | `error`           | There is an error or some sort of issue with the code.                    |
| `light red`   | `syntax-error`    | Convention error is found within the code.                                |
| `yellow`      | `severe-warning`  | High priority warning with code's syntax.                                 |
| `orange`      | `warning`         | Warning with code's syntax                                                |
| `purple`      | `complex`         | Complex convention issues. (For more experienced developers)              |
| `dark purple` | `super-complex`   | More complex convention issues. (For more experienced developers)         |
| `cyan`        | `neutral`         | Neutral convention issues with syntax.                                    |

# Quick Start
```shell
git clone https://github.com/amooo-ooo/pep8plus
```

## Setup
Setup dependencies by running the following on the terminal: 
```shell
pip install -r requirements.txt
cd client
npm install
```

## Hosting
Simply run `python server.py` to host the project:
```shell
python server.py
```

## Support
pep8plus was created as a school project with the aspiration of helping other young Pythonistas enforce and learn python coding practices. The purpose of this project is to provide educators with a transparent, customisable and easy solution to helping their students enforce Python conventions. 

## Contact
You can contact me at [amor.budiyanto@gmail.com](mailto:amor.budiyanto@gmail.com).

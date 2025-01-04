"""
Print results of pyflakes {file} to stdout.
Only .py files are checked. See "exclude" for directories and files.
"""

import subprocess

from os import walk
from os.path import dirname, join, realpath
from sys import path
project_home = dirname(dirname(realpath(__file__)))
if project_home not in path:
    path.insert(0, project_home)


def main():

    file_list = []
    exclude = set(["venv", "icons", "logo"])
    for root, dirs, files in walk(project_home):
        dirs[:] = [d for d in dirs if d not in exclude]
        for file in files:
            if file.endswith(".py"):
                file_list.append(join(root, file))

    exclude = [
        join(project_home, f) for f in [
            "main.py",
            join("gresource", "load_widgets.py"),
            # join("gresource", "compile_register.py"),
            join("_distribution", "main.py"),
        ]
    ]

    check_result = ""
    for file in file_list:
        if file not in exclude:
            try:
                process = subprocess.run(
                    ["pyflakes", file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                    text=True,  # Decode output to string
                    check=True  # Raise an exception on non-zero exit code
                )
                result = process.stdout
            except subprocess.CalledProcessError as e:
                result = e.stdout  # Capture the output even in case of error
            if len(result) > 0:
                check_result += result + "\n"

    if len(check_result) > 0:
        print(check_result.strip("\n"))
    else:
        print("All good")


if __name__ == "__main__":
    main()

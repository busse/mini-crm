"""Check that the Python version meets the minimum requirement."""
import sys

MIN_VERSION = (3, 10)


def main():
    current = sys.version_info
    if current < MIN_VERSION:
        print(
            "ERROR: Python %d.%d+ is required, but you have %d.%d.%d"
            % (MIN_VERSION[0], MIN_VERSION[1], current.major, current.minor, current.micro)
        )
        print()
        print("To install a newer Python:")
        print("  macOS (Homebrew): brew install python@3.12")
        print("  Ubuntu / Debian:  sudo apt install python3.12 python3.12-venv")
        print("  pyenv:            pyenv install 3.12 && pyenv local 3.12")
        print("  Windows:          https://www.python.org/downloads/")
        sys.exit(1)
    else:
        print(
            "Python %d.%d.%d -- OK"
            % (current.major, current.minor, current.micro)
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
    if len(sys.argv) == 2 and sys.argv[1] == "runserver":
        sys.argv.append("127.0.0.1:8001")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django is not installed. Install the project dependencies first."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
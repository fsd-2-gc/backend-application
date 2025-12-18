#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# If you want tests to default to test settings when you run "python manage.py test"
# you can set it here when "test" is in argv.
if "test" in sys.argv:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.test_settings")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

# Stub boto3 (and any other optional deps) before Django imports URLConf/views.
if "test" in sys.argv:
    import app.test_bootstrap  # noqa: F401


def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

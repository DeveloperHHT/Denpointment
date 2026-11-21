"""Starts Denpointment.

    python main.py                 uses MySQL (see the DENPOINTMENT_DB_* variables in the README)
    python main.py --demo          uses a throw-away SQLite file with sample data, no MySQL needed
"""
from __future__ import annotations

import argparse
import os
from dataclasses import replace

from Backend.app import create_app
from Backend.config import Settings


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Denpointment, a dentist appointment system.")
    parser.add_argument("--demo", action="store_true", help="run on a SQLite demo database with sample data")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true", help="reload on code changes (development only)")
    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    settings = Settings.from_environment()
    if arguments.demo:
        from Scripts.seed_demo import prepare_demo_database

        settings = replace(settings, backend="sqlite")
        prepare_demo_database(settings)
    application = create_app(settings)
    # The reloader starts the program twice; only the first one should print the banner.
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        print(f"Denpointment {application.config['VERSION']} on http://{arguments.host}:{arguments.port}")
    application.run(host=arguments.host, port=arguments.port, debug=arguments.debug)


if __name__ == "__main__":
    main()

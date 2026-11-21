"""Blueprints: they turn requests into service calls and service results into pages."""
from flask import Flask


def register_blueprints(app: Flask) -> None:
    from . import account, auth, dentist, patient

    for module in (auth, account, patient, dentist):
        app.register_blueprint(module.bp)

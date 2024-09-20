"""Configration for application."""

import logging
import os

import dynaconf

_log = logging.getLogger(__name__)

ENV = os.getenv("ENV", "dev")

# load in config with dynaconf from ./config directory based on the environment
CONFIG = dynaconf.Dynaconf(
    settings_files=["./config/default.yaml", f"./config/{ENV.lower()}.yaml"],
)

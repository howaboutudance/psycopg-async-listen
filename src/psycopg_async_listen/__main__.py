"""Main execution entrypoint for application."""

import argparse
import asyncio
import logging

import psycopg

from psycopg_async_listen.execute import listen_for_notifications
from psycopg_async_listen.config import CONFIG

_log = logging.getLogger(__name__)


def execute():
    """Execute the application."""
    parser = argparse.ArgumentParser(description="Listen for notifications on a channel.")
    parser.add_argument("channel", help="The channel to listen for notifications on.")
    args = parser.parse_args()

    try:
        asyncio.run(listen_for_notifications(args.channel, asyncio.Queue()))
    except KeyboardInterrupt:
        _log.debug("Exiting application")
    except psycopg.OpertionalError as e:
        _log.error("An error occurred: %s, disconnecting", e)


if __name__ == "__main__":
    logging.basicConfig(level=CONFIG.log_level.upper())
    execute()

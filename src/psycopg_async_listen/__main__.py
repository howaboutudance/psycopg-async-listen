"""Main execution entrypoint for application."""

import argparse
import asyncio
import logging

from psycopg_async_listen.execute import listen_for_notifications
from psycopg_async_listen.config import CONFIG

_log = logging.getLogger(__name__)


def execute():
    """Execute the application."""
    parser = argparse.ArgumentParser(description="Listen for notifications on a channel.")
    parser.add_argument("channel", help="The channel to listen for notifications on.")
    args = parser.parse_args()

    asyncio.run(listen_for_notifications(args.channel, asyncio.Queue()))


if __name__ == "__main__":
    logging.basicConfig(level=CONFIG.log_level.upper())
    execute()

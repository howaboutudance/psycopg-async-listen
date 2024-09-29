"""Send a notification continuously until keyboard interrupt."""
import asyncio
import logging

from psycopg_async_listen.util import help_send_notifcations_continuously

_log = logging.getLogger(__name__)

def execute():
    """Execute the application."""
    asyncio.run(help_send_notifcations_continuously())

if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    execute()
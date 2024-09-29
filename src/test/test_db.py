"Test for conecting to the database"

import pytest

from psycopg_async_listen.db import get_cursor


# write a integration test to connect to the database
@pytest.mark.integration
@pytest.mark.asyncio
async def test_intg_cursor():
    async with get_cursor() as cursor:
        await cursor.execute("SELECT 1;")
        result = await cursor.fetchone()
        assert result == (1,)

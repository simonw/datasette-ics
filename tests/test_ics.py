import datasette
from datasette.app import Datasette
import urllib.parse
import pytest
import httpx


@pytest.mark.asyncio
async def test_incorrect_sql_returns_400():
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.ics?sql=select+sqlite_version()"
        )
    assert 400 == response.status_code
    assert b"SQL query must return columns" in response.content


@pytest.mark.asyncio
async def test_ics_for_valid_query():
    sql = """
    select
        'hello' as event_name,
        '2019-10-23T21:32:12' as event_dtstart,
        'item_1' as event_uid
    union select
        'another event' as event_name,
        '2019-09-24T21:32:12' as event_dtstart,
        'item_2' as event_uid
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.ics?" + urllib.parse.urlencode({"sql": sql})
        )
    assert 200 == response.status_code
    assert "text/calendar; charset=utf-8" == response.headers["content-type"]
    actual = response.content.decode("utf-8").strip()
    assert (
        "BEGIN:VCALENDAR\r\nBEGIN:VEVENT\r\nDTSTART:20191023T213212Z\r\nSUMMARY:hello\r\nUID:item_1\r\nEND:VEVENT\r\nBEGIN:VEVENT\r\nDTSTART:20190924T213212Z\r\nSUMMARY:another event\r\nUID:item_2\r\nEND:VEVENT\r\nPRODID:-//Datasette 0.37//datasette-ics//EN\r\nVERSION:2.0\r\nEND:VCALENDAR"
        == actual
    )

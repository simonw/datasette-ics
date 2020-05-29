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
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Datasette {}//datasette-ics//EN\r\n".format(
            datasette.version.__version__
        )
        + "BEGIN:VEVENT\r\n"
        "DTSTART:20191023T213212Z\r\n"
        "SUMMARY:hello\r\n"
        "UID:item_1\r\n"
        "END:VEVENT\r\n"
        "BEGIN:VEVENT\r\n"
        "DTSTART:20190924T213212Z\r\n"
        "SUMMARY:another event\r\n"
        "UID:item_2\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR" == actual
    )


@pytest.mark.asyncio
async def test_ics_with_timezone():
    sql = """
    select
        'hello' as event_name,
        '2019-10-23T21:32:12' as event_dtstart,
        'item_1' as event_uid,
        'America/Chicago' as event_tzid
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:.ics?"
            + urllib.parse.urlencode({"sql": sql, "_ics_title": "My calendar",})
        )
    assert 200 == response.status_code
    assert "text/calendar; charset=utf-8" == response.headers["content-type"]
    actual = response.content.decode("utf-8").strip()
    assert (
        "BEGIN:VCALENDAR\r\n"
        "X-WR-CALNAME:My calendar\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Datasette {}//datasette-ics//EN\r\n".format(
            datasette.version.__version__
        )
        + "BEGIN:VEVENT\r\n"
        "DTSTART;TZID=America/Chicago:20191023T213212\r\n"
        "SUMMARY:hello\r\n"
        "UID:item_1\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR" == actual
    )


@pytest.mark.asyncio
async def test_ics_link_only_shown_for_correct_queries():
    sql = """
    select
        'hello' as event_name,
        '2019-10-23T21:32:12' as event_dtstart,
        'item_1' as event_uid,
        'America/Chicago' as event_tzid
    """
    app = Datasette([], immutables=[], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:?" + urllib.parse.urlencode({"sql": sql})
        )
    assert 200 == response.status_code
    assert "text/html; charset=utf-8" == response.headers["content-type"]
    assert b'<a href="/:memory:.ics' in response.content
    # But with a different query that link is not shown:
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get(
            "http://localhost/:memory:?"
            + urllib.parse.urlencode({"sql": "select sqlite_version()"})
        )
    assert b'<a href="/:memory:.json' in response.content
    assert b'<a href="/:memory:.ics' not in response.content


@pytest.mark.asyncio
async def test_ics_from_titled_canned_query():
    sql = """
    select
        'hello' as event_name,
        '2019-10-23T21:32:12' as event_dtstart,
        'item_1' as event_uid,
        'America/Chicago' as event_tzid
    """
    app = Datasette(
        [],
        immutables=[],
        memory=True,
        metadata={
            "databases": {
                ":memory:": {
                    "queries": {"calendar": {"sql": sql, "title": "My calendar"}}
                }
            }
        },
    ).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/:memory:/calendar.ics")
    assert 200 == response.status_code
    assert "text/calendar; charset=utf-8" == response.headers["content-type"]
    actual = response.content.decode("utf-8").strip()
    assert (
        "BEGIN:VCALENDAR\r\n"
        "X-WR-CALNAME:My calendar\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Datasette {}//datasette-ics//EN\r\n".format(
            datasette.version.__version__
        )
        + "BEGIN:VEVENT\r\n"
        "DTSTART;TZID=America/Chicago:20191023T213212\r\n"
        "SUMMARY:hello\r\n"
        "UID:item_1\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR" == actual
    )

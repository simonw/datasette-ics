import datasette
from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
async def test_incorrect_sql_returns_400():
    ds = Datasette([], immutables=[], memory=True)
    response = await ds.client.get("/_memory.ics?sql=select+sqlite_version()")
    assert response.status_code == 400
    assert "SQL query must return columns" in response.text


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
    ds = Datasette([], immutables=[], memory=True)
    response = await ds.client.get("_memory.ics", params={"sql": sql})
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
    ds = Datasette(memory=True)
    response = await ds.client.get(
        "/_memory.ics?",
        params={
            "sql": sql,
            "_ics_title": "My calendar",
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    actual = response.text.strip()
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
    ds = Datasette(memory=True)
    response = await ds.client.get("/_memory", params={"sql": sql})
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert '<a href="/_memory.ics' in response.text
    # But with a different query that link is not shown:
    response2 = await ds.client.get(
        "/_memory", params={"sql": "select sqlite_version()"}
    )
    assert '<a href="/_memory.json' in response2.text
    assert '<a href="/_memory.ics' not in response2.text


@pytest.mark.asyncio
async def test_ics_from_titled_canned_query():
    sql = """
    select
        'hello' as event_name,
        '2019-10-23T21:32:12' as event_dtstart,
        'item_1' as event_uid,
        'America/Chicago' as event_tzid
    """
    ds = Datasette(
        memory=True,
        metadata={
            "databases": {
                "_memory": {
                    "queries": {"calendar": {"sql": sql, "title": "My calendar"}}
                }
            }
        },
    )
    response = await ds.client.get("/_memory/calendar.ics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/calendar; charset=utf-8"
    actual = response.text.strip()
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

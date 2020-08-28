from datasette import hookimpl, __version__
from datasette.utils.asgi import Response
from ics import Calendar, parse
from .utils import EventWithTimezone


REQUIRED_COLUMNS = {"event_name", "event_dtstart"}


@hookimpl
def register_output_renderer():
    return {"extension": "ics", "render": render_ics, "can_render": can_render_ics}


def render_ics(
    datasette, request, database, table, rows, columns, sql, query_name, data
):
    from datasette.views.base import DatasetteError

    if not REQUIRED_COLUMNS.issubset(columns):
        raise DatasetteError(
            "SQL query must return columns {}".format(", ".join(REQUIRED_COLUMNS)),
            status=400,
        )
    c = Calendar(creator="-//Datasette {}//datasette-ics//EN".format(__version__))
    title = request.args.get("_ics_title") or ""
    if table and not title:
        title = table
    if data.get("human_description_en"):
        title += ": " + data["human_description_en"]

    # If this is a canned query the configured title for that over-rides all others
    if query_name:
        try:
            title = datasette.metadata(database=database)["queries"][query_name][
                "title"
            ]
        except (KeyError, TypeError):
            pass

    if title:
        c.extra.append(parse.ContentLine(name="X-WR-CALNAME", params={}, value=title))

    for row in reversed(rows):
        e = EventWithTimezone()
        e.name = row["event_name"]
        e.begin = row["event_dtstart"]
        if "event_dtend" in columns:
            e.end = row["event_dtend"]
        elif "event_duration" in columns:
            e.duration = row["event_duration"]
        if "event_description" in columns:
            e.description = row["event_description"]
        if "event_uid" in columns:
            # TODO: Must be globally unique - include the
            # current URL to help achieve this
            e.uid = str(row["event_uid"])
        if "event_tzid" in columns:
            e.timezone = row["event_tzid"]
        c.events.add(e)

    content_type = "text/calendar; charset=utf-8"
    if request.args.get("_plain"):
        content_type = "text/plain; charset=utf-8"

    return Response(str(c), content_type=content_type, status=200)


def can_render_ics(columns):
    return REQUIRED_COLUMNS.issubset(columns)

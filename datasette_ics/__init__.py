from datasette import hookimpl, __version__
from ics import Calendar, Event


REQUIRED_COLUMNS = {"event_name", "event_dtstart"}


@hookimpl
def register_output_renderer():
    return {"extension": "ics", "callback": render_ics}


def render_ics(args, data, view_name):
    from datasette.views.base import DatasetteError

    columns = set(data["columns"])
    if not REQUIRED_COLUMNS.issubset(columns):
        raise DatasetteError(
            "SQL query must return columns {}".format(", ".join(REQUIRED_COLUMNS)),
            status=400,
        )
    c = Calendar(creator="-//Datasette {}//datasette-ics//EN".format(__version__))
    sql = data["query"]["sql"]
    title = title = args.get("_ics_title", sql)
    if data.get("table"):
        title += "/" + data["table"]
    if data.get("human_description_en"):
        title += ": " + data["human_description_en"]

    for row in reversed(data["rows"]):
        e = Event()
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
        c.events.add(e)

    content_type = "text/calendar; charset=utf-8"
    if args.get("_plain"):
        content_type = "text/plain; charset=utf-8"

    return {
        "body": str(c),
        "content_type": content_type,
        "status_code": 200,
    }

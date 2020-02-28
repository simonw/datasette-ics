from ics.grammar.parse import ContentLine
from ics.parsers.event_parser import EventParser
from ics.serializers.event_serializer import EventSerializer
from ics.event import Event
import arrow


class EventWithTimezoneSerializer(EventSerializer):
    def serialize_start(event, container):
        if event.begin and not event.all_day:
            value = arrow.get(event.begin).format("YYYYMMDDTHHmmss")
            if event.timezone is None:
                value += "Z"
            container.append(
                ContentLine("DTSTART", value=value, params=event.timezone_params(),)
            )

    def serialize_end(event, container):
        if event.begin and event._end_time and not event.all_day:
            value = arrow.get(event.end).format("YYYYMMDDTHHmmss")
            if event.timezone is None:
                value += "Z"

            container.append(
                ContentLine("DTEND", value=value, params=event.timezone_params(),)
            )


class EventWithTimezone(Event):
    timezone = None

    class Meta:
        name = "VEVENT"
        parser = EventParser
        serializer = EventWithTimezoneSerializer

    def timezone_params(self):
        if getattr(self, "timezone", None):
            return {"TZID": [self.timezone]}
        return {}

# datasette-ics

[![PyPI](https://img.shields.io/pypi/v/datasette-ics.svg)](https://pypi.org/project/datasette-ics/)
[![Changelog](https://img.shields.io/github/v/release/simonw/datasette-ics?include_prereleases&label=changelog)](https://github.com/simonw/datasette-ics/releases)
[![CircleCI](https://circleci.com/gh/simonw/datasette-ics.svg?style=svg)](https://circleci.com/gh/simonw/datasette-ics)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/datasette-ics/blob/main/LICENSE)

Datasette plugin that adds support for generating [iCalendar .ics files](https://tools.ietf.org/html/rfc5545) with the results of a SQL query.

## Installation

Install this plugin in the same environment as Datasette to enable the `.ics` output extension.

    $ pip install datasette-ics

## Usage

To create an iCalendar file you need to define a custom SQL query that returns a required set of columns:

* `event_name` - the short name for the event
* `event_dtstart` - when the event starts

The following columns are optional:

* `event_dtend` - when the event ends
* `event_duration` - the duration of the event (use instead of `dtend`)
* `event_description` - a longer description of the event
* `event_uid` - a globally unique identifier for this event
* `event_tzid` - the timezone for the event, e.g. `America/Chicago`

A query that returns these columns can then be returned as an ics feed by adding the `.ics` extension.

## Using a canned query

Datasette's [canned query mechanism](https://datasette.readthedocs.io/en/stable/sql_queries.html#canned-queries) can be used to configure calendars. If a canned query definition has a `title` that will be used as the title of the calendar.

Here's an example, defined using a `metadata.yaml` file:

```yaml
databases:
  mydatabase:
    queries:
      calendar:
        title: My Calendar
        sql: |-
          select
            title as event_name,
            start as event_dtstart,
            description as event_description
          from
            events
          order by
            start
          limit
            100
```
This will result in a calendar feed at `http://localhost:8001/mydatabase/calendar.ics`

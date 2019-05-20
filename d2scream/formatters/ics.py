from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List

ISO = "%Y%m%dT%H%M%S"
class Calendar():
    def __init__(self, events = None):
        self.events = []
        if events:
            self.events.extend(events)

    def dump(self):
        lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//Minervaclient//NONSGML minervaclient.npaun.ca//EN"
                ]
        for event in self.events:
            lines.extend(event.dump())

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines) + "\r\n"

class RRule(object):
    pass

class Status(Enum):
    TENTATIVE = "TENTATIVE"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


@dataclass
class Event():
    """
    There are many more vCalendar properties which are not supported,
    if you need to add one, take a look at:
    https://tools.ietf.org/html/rfc5545#section-3.6.1
    and
    https://tools.ietf.org/html/rfc5545#section-8.3.2
    """

    """
    A globally-unique identifier for this calendar event. It has to be selected
    so that if, for example, an exam time is updated, the UID will remain the same.
    """
    uid:str

    """
    The date of modification of this event. MUST be in UTC.
    """
    dtstamp:datetime = field(default_factory=datetime.utcnow)


    """
    Date at which this event starts. Can be in local time.
    """
    dtstart:datetime = None


    """
    Long description of the event. Line breaks can be used if escaped as \n 
    (we will take care of this for you.)
    """
    description:str = None

    """
    Geographical coordinates (lat/long of the event).
    We will not use this for now, but it may be useful if the calendar gets confused by location?
    """
    geo = None

    """
    Location of the event, as free-form text
    """
    location:str = None

    """
    Name and email address of the person that organized the event.
    Currently ignored
    """
    organizer:str = None

    """
    Priority of the event, an integer between 0 and 9.
    0 = not set, 1 = most urgent, 9 = least urgent
    """
    priority:int = None

    """
    Status of the event. Tentative, Confirmed or Cancelled.
    May be useful for tentative exam schedules?
    """
    status:Status = None

    """
    The title of the event. Stick to one line.
    """
    summary:str = None

    """
    You can provide a link to more information about the event.
    """
    url:str = None

    """
    Recurrence rule. There are many choices for how to specify this.
    """
    rrule:RRule = None

    """
    Date at which the event ends (on a particular occurence of it).
    This priority will take precedence over duration if you specify both.
    """
    dtend:datetime = None

    """
    Duration of the event, in ISO 8601 notation.
    Currently ignored.
    """
    duration = None

    """
    A list of categories for the event.
    Your calendar program probably just ignores it.
    """
    categories:List[str] = field(default_factory=list)

    """
    Dates that should be excluded from the recurrence rule.
    """
    exdate:List[datetime] = field(default_factory=list)

    """
    A list of resources required for the event.
    Your calendar program probably just ignores it.
    """
    resources:List[str] = field(default_factory=list)

    """
    Dates which should be exceptionally included in the recurrence rule.
    """
    rdate:List[datetime] = field(default_factory=list)

    """
    Calendar domain (our custom field used to scope UIDs)
    """
    calendar_domain:str = "minervaclient.npaun.ca"

    """
    Calendar timezone (used to scope dates)
    """
    calendar_tz:str = "America/Montreal"


   
    def dump(self):
        data = self.__dict__
        # Exclude all null fields
        data = {k:v for k,v in data.items() if v}

        vevent = {}

        STANDARD_FIELDS = {'url', 'summary', 'priority', 'location','organizer','status','rrule'}
        for field in STANDARD_FIELDS:
            if field in data:
                vevent[field] = str(data[field])

        DATE_FIELDS = {'dtstart','dtend', 'exdate','rdate'}
        for field in DATE_FIELDS:
            if field in data:
                vevent[field] = _dump_date(self.calendar_tz,data[field])

        LIST_FIELDS = {'categories','resources'}
        for field in LIST_FIELDS:
            if field in data:
                vevent[field] = ",".join(data[field])


        vevent['uid'] = self.uid + '@' + self.calendar_domain
        vevent['dtstamp'] = self.dtstamp.strftime(ISO) + 'Z'
        if 'description' in data:
            vevent['description'] = _escape_description(self.description)


        lines = ["BEGIN:VEVENT"]
        lines.extend("%s%s" % (k.upper(), _columnize(v)) for k,v in vevent.items())
        lines.append("END:VEVENT")

        return lines
        # Now for the custom fields


class Weekday(Enum):
    MO = "MO"
    TU = "TU"
    WE = "WE"
    TH = "TH"
    FR = "FR"
    SA = "SA"
    SU = "SU"


@dataclass
class Weekly(RRule):
   """
   How often should this event repeat?
   """
   freq:str = "WEEKLY"

   """
   When is the last date that the event should repeat?
   """
   until:datetime = None

   """
   Which days of the week does the event repeat on?
   Use the weekday enum.
   """
   byday:List[Weekday] = field(default_factory=[])

   def __str__(self):
       return "FREQ=%s;UNTIL=%s;BYDAY=%s" % (self.freq, self.until, ",".join(self.byday))


def _dump_date(calendar_tz,dates):
    if not hasattr(dates,'__iter__'):
        dates = [dates]

    date_spec = ",".join(date.strftime(ISO) for date in dates)
    return ";TZID=%s:%s" % (calendar_tz,date_spec)


def _escape_description(desc):
    return desc.replace('\n','\\n')

def _columnize(val):
    if val.startswith(';'):
        return val # Raw
    else:
        return ':' + val


"""
  html-calendar
  =============

  A simple HTML calendar generator with callbacks for adding links to date
  and formating classes
"""

__version__ = "0.0.24"

import calendar
import locale as lc
from html import escape


WEEKDAYS0 = [""] * 7
WEEKDAYS1 = [""] * 7


def nolist(date):
    return []


def nostr(date):
    return ""


def noattrs(date):
    return {}


def update_weekdays():
    global WEEKDAYS0, WEEKDAYS1
    WEEKDAYS0 = list(calendar.day_abbr)
    WEEKDAYS1 = [WEEKDAYS0[6]] + list(WEEKDAYS0[0:6])


EMPTY_ROW = "<tr>" + 7 * "<td>&nbsp;</td>" + "</tr>"


def htmlday(date, classes, links, attrs, safe):
    result = []
    ls = links(date)
    atdict = attrs(date)
    cs = classes(date)
    if cs:
        if safe:
            atdict['class'] = " ".join([c for c in cs])
        else:
            atdict['class'] = " ".join([escape(c) for c in cs])

    if atdict:
        if safe:
            ats = " ".join([f'{k}="{v}"' for k, v in atdict.items()])
        else:
            ats = [f'{escape(k)}="{escape(v)}"' for k, v in atdict.items()]
            ats = " ".join(ats)
        result.append(f"<td {ats}>")
    else:
        result.append("<td>")
    if ls:
        if safe:
            result.append(f'<a href="{ls}">')
        else:
            result.append(f'<a href="{escape(ls)}">')

    result.append(escape(str(date.day)))
    if ls:
        result.append("</a>")
    result.append("</td>")
    return "".join(result)


def html_week_days(caltype):
    result = ["<tr>"]
    wds = WEEKDAYS1 if caltype else WEEKDAYS0
    for wd in wds:
        result.append(f"<th>{escape(wd)}</th>")
    result.append("</tr>\n")
    return "".join(result)


def htmlmonth(month, year, classes=nolist, links=nostr, attrs=noattrs,
              th_classes=[], table_classes=[], caltype=0, header="h3",
              locale=None, safe=False):
    result = []
    week_count = 0
    header = escape(header)
    month_name = escape(calendar.month_name[month])
    result.append(f"<{header}>{month_name}</{header}>")
    if table_classes:
        cls = ' '.join([escape(c) for c in table_classes])
        result.append(f'<table class="{cls}">')
    else:
        result.append("<table>")
    result.append(html_week_days(caltype))
    cal = calendar.Calendar(caltype)
    for date in cal.itermonthdates(year, month):
        if date.weekday() == 0:
            week_count += 1
            result.append("<tr>\n")
        if date.month != month:
            result.append("<td></td>")
        else:
            result.append(htmlday(date, classes, links, attrs, safe))
        if date.weekday() == 6:
            result.append("</tr>\n")
    if week_count == 5:
        result.append(EMPTY_ROW)
    result.append("</table>\n\n")
    return "".join([str(x) for x in result])


def backwards_iterator(starting, months):
    month = starting.month
    year = starting.year
    yield (starting.month, starting.year)
    for i in range(0, months):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        yield (month, year)


def forward_iterator(starting, months):
    month = starting.month
    year = starting.year
    yield (starting.month, starting.year)
    for i in range(0, months):
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        yield (month, year)


def htmlcalendar(starting_date,
                 months=3,
                 classes=nolist,
                 links=nostr,
                 attrs=noattrs,
                 th_classes=[],
                 table_classes=[],
                 caltype=0,
                 backwards=True,
                 header="h3",
                 locale=None,
                 safe=False,
                 ):

    """
    Main function that takes a starting date and returns a list of
    tables containing months calendars in tables.

    All tables generated have 6 rows, even the last one is empty.

    Parameters
    ----------

    starting_date: datetime.date
        Any date object of the month we want to start generating from.
    months: int
        The number of months we want to generate
    classes: function
        A function that takes a datetime.date as parameter and returns
        a list of strings that will be put as classes of the table cell
    links: function
        A function that takes a datetime.date as parameter and returns
        a fully qualified URL that will be linked to the date number. If
        the function returns none there is no link generated.
    attrs:
        A dict of attributes to be inserted in the <td> tags.
    th_classes: list
        A list of classes to be put in each one of the weekdays labels.
    table_classes: list
        A list of classes to be put in the main table object.
    caltype: int
        If you want weeks starting on sunday 1 else 0
    backwards: bool
        If you want to generate the calendars to the past True else False
    header: string
        Set the html header level for the calendar month name
    locale: string
        Set the locale name used for naming month and week days names
    safe: bool
        If false escapes all variables that go into the templates
    """

    iterator = backwards_iterator if backwards else forward_iterator

    if locale is not None:
        lc.setlocale(lc.LC_ALL, locale)
        update_weekdays()

    result = []
    for month, year in iterator(starting_date, months - 1):
        result.append(htmlmonth(month,
                                year,
                                classes=classes,
                                links=links,
                                attrs=attrs,
                                th_classes=th_classes,
                                table_classes=table_classes,
                                caltype=caltype,
                                header=header,
                                locale=locale,
                                safe=safe))
    return reversed(result) if backwards else result

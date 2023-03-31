"""
  html-calendar
  =============

  A simple HTML calendar generator with callbacks for adding links to date
  and formating classes
"""

__version__ = "0.0.8"

import calendar


def nolist(date):
    return []


def nostr(date):
    return ""


def no_month_factory(no_month_class):
    def no_month(date):
        return [no_month_class]
    return no_month


WEEKDAYS0 = list(calendar.day_abbr)
WEEKDAYS1 = [WEEKDAYS0[6]] + list(WEEKDAYS0[0:6])
EMPTY_ROW = "<tr>" + 7 * "<td>&nbsp;</td>" + "</tr>"


def htmlday(date, classes, links):
    result = []
    cs = classes(date)
    ls = links(date)
    if cs:
        result.append(f'<td class="{" ".join(cs)}">')
    else:
        result.append("<td>")
    if ls:
        result.append(f'<a href="{ls}">')
    result.append(str(date.day))
    if ls:
        result.append("</a>")
    result.append("</td>")
    return "".join(result)


def html_week_days(caltype):
    result = ["<tr>"]
    wds = WEEKDAYS1 if caltype else WEEKDAYS0
    for wd in wds:
        result.append(f"<th>{wd}</th>")
    result.append("</tr>\n")
    return "".join(result)


def htmlmonth(month, year, classes=nolist, links=nostr, nomonth=nolist,
              th_classes=[], table_classes=[], caltype=0):
    result = []
    week_count = 0
    result.append(f"<h2>{calendar.month_name[month]}</h2>")
    if table_classes:
        cls = ' '.join(table_classes)
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
            result.append(htmlday(date, nomonth, nostr))
        else:
            result.append(htmlday(date, classes, links))
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
                 no_month_class='nomonth',
                 th_classes=[],
                 table_classes=[],
                 caltype=0,
                 backwards=True):
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
    no_month_class: string
        The name of a css class to be put in the cells of the table that
        don't belongo to the month in course.
    th_classes: list
        A list of classes to be put in each one of the weekdays labels.
    table_classes: list
        A list of classes to be put in the main table object.
    caltype: int
        If you want weeks starting on sunday 1 else 0
    backwards: bool
        If you want to generate the calendars to the past True else False
    """

    nomonth = no_month_factory(no_month_class)

    iterator = backwards_iterator if backwards else forward_iterator

    result = []
    for month, year in iterator(starting_date, months - 1):
        result.append(htmlmonth(month, year, classes, links, nomonth,
                      th_classes, table_classes, caltype))
    return reversed(result)

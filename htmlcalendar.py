#
# Objetive: Draw a calendar in html with links with months tables separated in
# divs so they can be thrown in a flexbox.
#

import calendar

nolist = lambda x:[]
nostr = lambda x:""

def htmlday(date, classes, links):
    result = []
    cs = classes(date)
    l = links(date)
    result.append("<td>")
    if cs:
        result.append(f'<span class="{" ".join(cs)}">')
    if l:
        result.append(f'<a href="{l}">')
    result.append(str(date.day))
    if l:
        result.append("</a>")
    if cs:
        result.append("</span>")
    result.append("</td>")
    return "".join(result)

def htmlmonth(month, year, classes, links, nomonth):
    result = ["<table>"]
    cal = calendar.Calendar()
    for date in cal.itermonthdates(year, month):
        if date.weekday() == 0:
            result.append("<tr>\n")
        if date.month != month:
            result.append(htmlday(date, nomonth, nostr))
        else:
            result.append(htmlday(date, classes, links))
        if date.weekday() == 6:
            result.append("</tr>\n")
    result.append("</table>\n\n")
    return "".join([str(x) for x in result])

def get_months(starting, months):
    month = starting.month
    year = starting.year 
    result = [(starting.month, starting.year)]
    for i in range(0, months):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -=1
        result.append((month, year))
    return result

def htmlcalendar(starting, months=3, classes=nolist, links=nostr, no_month_class='nomonth'):
    result = []
    nomonth = lambda x: [no_month_class]
    for month, year in get_months(starting, months):
        result.append(htmlmonth(month, year, classes, links, nomonth))
    return "\n".join([str(x) for x in reversed(result)])


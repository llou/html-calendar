#
#  html-calendar  
#  =============
#
#  A simple HTML calendar generator with callbacks for adding links to dates and
#  formating classes. 
#
# (c) 2023 Jorge Monforte Gonzalez
#

import calendar

nolist = lambda x:[]
nostr = lambda x:""

WEEKDAYS0 = ("mo", "tu", "we", "th", "fr", "sa", "su")
WEEKDAYS1 = ("su", "mo", "tu", "we", "th", "fr", "sa")
EMPTY_ROW = "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>"

def htmlday(date, classes, links):
    result = []
    cs = classes(date)
    l = links(date)
    if cs:
        result.append(f'<td class="{" ".join(cs)}">')
    else:
        result.append("<td>")
    if l:
        result.append(f'<a href="{l}">')
    result.append(str(date.day))
    if l:
        result.append("</a>")
    if cs:
        result.append("</span>")
    result.append("</td>")
    return "".join(result)

def html_week_days(caltype):
    result = ["<tr>"]
    wds = WEEKDAYS1 if caltype else WEEKDAYS0
    for wd in wds:
        result.append(f"<th>{wd}</th>")
    result.append("</tr>\n")
    return "".join(result)

def htmlmonth(month, year, classes, links, nomonth, th_classes, table_classes, 
        caltype):
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

def htmlcalendar(starting, months=3, classes=nolist, links=nostr, 
        no_month_class='nomonth', th_classes=[], table_classes=[],
        caltype=0):
    result = []
    nomonth = lambda x: [no_month_class]
    for month, year in get_months(starting, months):
        result.append(htmlmonth(month, year, classes, links, nomonth, 
            th_classes, table_classes, caltype))
    return [str(x) for x in reversed(result[0:months])]


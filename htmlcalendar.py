#
# Objetive: Draw a calendar in html with links with months tables separated in
# divs so they can be thrown in a flexbox.
#

import calendar

class HTMLDay:
    def __init__(self, date, classes, link):
        self.date = date
        self.classes = classes
        self.link = link

    def __str__(self):
        result = []
        result.append("<td>")
        if self.classes:
            result.append(f'<span class="{" ".join(self.classes)}">')
        if self.link:
            result.append(f'<a href="{self.link}">')
        result.append(self.date.day)
        if self.link:
            result.append("</a>")
        if self.classes:
            result.append("</span>")
        result.append("</td>")
        return "".join(result)


class HTMLMonth:

    not_in_month_classes = ["notinmonth"]

    def __init__(self, month, year, classes, links):
        self.month = month
        self.year = year
        self.classes = classes
        self.links = links

    def __str__(self):
        result = ["<table>"]
        for date in calendar.itermonthdates(self.year, self.month):
            if date.weekday == 0:
                result.append("<tr>")
            if date.month != self.month:
                result.append(HTMLDay(date, self.not_in_month_classes, ""))
            else:
                retusl.append(HTMLDay(date, classes(date), links(date)))
            if date.weekday == 6:
                result.append("</tr>\n")
        result.append("</table>")
        return "".join([str(x) for x in result])


class HTMLCalendar:

    @staticmethod
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

    def __init__(self, starting, classes, links, months=3):
        self.classes = class_callback
        self.links = link_callback
        self.months = self.get_months(starting, months)

    def __str__(self):
        result = []
        for month, year in self.months:
            result.append(HTMLMonth(month, year, self.classes, self.links))
        return "\n".join([str(x) for x in reversed(result)])

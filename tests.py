import importlib
import random
from datetime import date
import calendar
import unittest
from html.parser import HTMLParser
from htmlcalendar import (htmlcalendar, htmlday, htmlmonth, get_months, nolist,
        nostr, WEEKDAYS0, WEEKDAYS1)

VALID_HTML_TAGS = ["table", "th", "tr", "td", "a", "span", "h1", "h2"]

class CalParser(HTMLParser):
    def __init__(self):
        self.result = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        self.result.append(["starttag", tag, attrs])

    def handle_endtag(self, tag):
        self.result.append(["endtag", tag])

    def handle_data(self, data):
        self.result.append(["data", data])


class HTMLSError(Exception):
    pass


def html_sanity_checker(html_text):
    parser = CalParser()
    parser.feed(html_text)
    tags = {}
    for item in parser.result:
        if item[0] == "starttag":
            if not item[1] in VALID_HTML_TAGS:
                raise HTMLSError(f"Invalid tag '{item[1]}'")
            if item[1] in tags:
                tags[item[1]] += 1
            else:
                tags[item[1]] = 1
        if item[0] == "endtag":
            if item[1] in tags:
                tags[item[1]] -= 1
            else:
                raise HTMLSError(f"Invalid end tag {item[1]}")
    for tag, count in tags.items():
        if count != 0:
            raise HTMLSError(f"Tag {tag} counts {count}")


class SanityCheckerTestCase(unittest.TestCase):
    def assertSanityError(self, html):
        self.assertRaises(HTMLSError, html_sanity_checker, html)

    def test(self):
        self.assertSanityError('<a href="link">text')
        self.assertSanityError('<dog href="link">text</dog>')
        self.assertSanityError('<table><tr><th>a</th><th>b<th></tr><td>1</td><td>2</td></tr></table>')

        
class DayTestCase(unittest.TestCase):
    day = date(2023, 5, 8)
    parser_class = CalParser
    url = "https://nowhere"

    def setUp(self):
        self.parser = self.parser_class()

    def assertClassesInTag(self, attrs, classes):
        attrs = dict(attrs)
        self.assertIn("class", attrs)
        attr_classes = attrs["class"].split(" ")
        for cls in classes:
            self.assertIn(cls, attr_classes)

    def assertLinksTo(self, attrs, url):
        attrs = dict(attrs)
        self.assertIn("href", attrs)
        self.assertEqual(attrs["href"], url)

    def parse_day(self, date, class_callback, link_callback):
        html_day = htmlday(self.day, class_callback, link_callback)
        self.parser.feed(html_day)
        return self.parser.result

    def test_empty_day(self):
        feed = self.parse_day(self.day, nolist, nostr)
        item = feed[0]
        self.assertEqual(item[0], "starttag")
        self.assertEqual(item[1], "td")
        self.assertFalse(item[2])
        item = feed[1]
        self.assertEqual(item[0], "data")
        self.assertEqual(item[1], str(self.day.day))
        item = feed[2]
        self.assertEqual(item[0], "endtag")
        self.assertEqual(item[1], "td")

    def test_class(self):
        callback = lambda x: ["classy", "beautiful"]
        feed = self.parse_day(self.day, callback, nostr)
        item = feed[0]
        self.assertEqual(item[0], "starttag")
        self.assertEqual(item[1], "td")
        self.assertClassesInTag(item[2], ["classy", "beautiful"])
        classes = item[2]
        item = feed[1]
        self.assertEqual(item[0], "data")
        self.assertEqual(item[1], str(self.day.day))
        item = feed[2]
        self.assertEqual(item[0], "endtag")
        self.assertEqual(item[1], "td")

    def test_link_day(self):
        callback = lambda x: self.url 
        feed = self.parse_day(self.day, nolist, callback)
        item = feed[0]
        self.assertEqual(item[0], "starttag")
        self.assertEqual(item[1], "td")
        item = feed[1]
        self.assertEqual(item[0], "starttag")
        self.assertEqual(item[1], "a")
        self.assertLinksTo(item[2], self.url)
        item = feed[2]
        self.assertEqual(item[0], "data")
        self.assertEqual(item[1], str(self.day.day))
        item = feed[3]
        self.assertEqual(item[0], "endtag")
        self.assertEqual(item[1], "a")
        item = feed[4]
        self.assertEqual(item[0], "endtag")
        self.assertEqual(item[1], "td")


class MonthTestCase(unittest.TestCase):
    year = 2012
    month = 5
    no_month_classes = ["nomonth"]
    th_classes = ["header"]
    table_classes = ["table"]
    caltype = 0
    parser_class = CalParser


    def classFunction(self, date):
        return []

    def linkFunction(self, date):
        return ""

    def setUp(self):
        self.calendar = calendar.Calendar(self.caltype)
        self.date_iterator = self.calendar.itermonthdates(self.year, self.month)
        self.html = htmlmonth(self.month, self.year, 
            classes=self.classFunction,
            links=self.linkFunction,
            th_classes=self.th_classes,
            table_classes=self.table_classes,
            caltype=self.caltype)
        self.parser = self.parser_class()
        self.parser.feed(self.html)
        self.data = self.parser.result

    def header_iterator(self):
        header = False
        attrs = {}
        th = False
        for item in self.data:
            if item[0] == "endtag" and item[1] == "tr":
                break
            if item[0] == "startag" and item[1] == "th":
                th = True
                attrs = item[2]
            if item[0] == "data" and th:
                yield item[1], attrs
            if item[0] == "endtag" and item[1] == "th":
                th = False
                attrs = {}

    def table_iterator(self):
        header = True
        attrs = {}
        href = ""
        td = False
        for item in self.data:
            if item[0] == "endtag" and item[1] == "tr":
                header == False
            if header:
                continue
            if item[0] == "startag" and item[1] == "td":
                td = True
                attrs = item[2]
            if item[0] == "startag" and item[1] == "a" and "href" in item[2]:
                href = item[2]["href"]
            if item[0] == "data" and td:
                yield item[1], attrs, href
            if item[0] == "endtag" and item[1] == "a":
                href = ""
            if item[0] == "endtag" and item[1] == "tr":
                td = False
                attrs = {}

    def iter_month_days(self):
        in_month = False
        for x in self.table_iterator():
            if x[0] == '1':
                in_month = not in_month
            if in_month:
                yield x

    def iter_no_month_days(self):
        in_month = False
        for x in self.table_iterator():
            if x[0] == '1':
                in_month = not in_month
            if not in_month:
                yield x

    @staticmethod
    def day_to_date(day):
        return date(self.year, self.month, day)

    def assertClasses(self, attrs, classes):
        self.assertTrue('class' in attrs)
        attrs_classes = set(attrs['class'].split(" "))
        self.assertEqual(attrs_classes, set(classes))

    def test_sanity(self):
        html_sanity_checker(self.html)

    def test_table(self):
        # TODO Check table classes
        pass

    def test_header(self):
        names = [ x[0] for x in self.header_iterator() ]
        week_days = WEEKDAYS0 if self.caltype == 0 else WEEKDAYS1
        for name1, name2 in zip(names, WEEKDAYS0):
            self.assertEqual(name1, name2)

    def test_table_days(self):
        day_numbers = [ x[0] for x in self.table_iterator() ]
        dates = [ x for x in self.table_iterator() ]
        for day, date in zip(day_numbers, dates):
            self.assertEqual(day, date.day)

    def test_no_month_days(self):
        for d, attrs, href in self.iter_no_month_days():
            self.assertClasses(attrs, self.no_month_classes)

    def test_month_days(self):
        for day, attrs, href in self.iter_month_days():
            date = self.day_to_date(day)
            classes = self.classFunction(date)
            link = self.linkFunction(date)
            self.assertClasses(attrs, self.no_month_classes)
            self.assertEqual(link, href)
       

if __name__ == "__main__":
    unittest.main()


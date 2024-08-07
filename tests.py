from datetime import date
import calendar
import unittest
from unittest.mock import patch, Mock, call
from typing import Tuple, List
from html.parser import HTMLParser
from htmlcalendar import (htmlcalendar,
                          htmlday,
                          htmlmonth,
                          forward_iterator,
                          backwards_iterator,
                          nolist,
                          nostr,
                          noattrs,
                          )
import htmlcalendar as hc


VALID_HTML_TAGS = ["table", "th", "tr", "td", "a", "span", "h1", "h2", "h3",
                   "h4"]


def is_link(attrs):
    return "href" in dict(attrs)


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
        self.assertSanityError('<table><tr><th>a</th><th>b<th></tr><td>1</td>'
                               '<td>2</td></tr></table>')


class DayTestCase(unittest.TestCase):
    day = date(2023, 5, 8)
    parser_class = CalParser
    url = "https://nowhere"
    key = "onclick"
    value = "dial(home)"
    safe = False

    def setUp(self):
        self.parser = self.parser_class()

    def assertClassesInTag(self, attrs, classes):
        attrs = dict(attrs)
        self.assertIn("class", attrs)
        attr_classes = attrs["class"].split(" ")
        for cls in classes:
            self.assertIn(cls, attr_classes)

    def assertAttributeInTag(self, attrs, key, value):
        attrs = dict(attrs)
        self.assertIn(self.key, attrs)
        self.assertEqual(attrs[self.key], self.value)

    def assertLinksTo(self, attrs, url):
        attrs = dict(attrs)
        self.assertIn("href", attrs)
        self.assertEqual(attrs["href"], url)

    def parse_day(self, date, class_callback, link_callback, attrs_callback,
                  safe):
        html_day = htmlday(self.day, class_callback, link_callback,
                           attrs_callback, safe)
        self.parser.feed(html_day)
        return self.parser.result

    def test_empty_day(self):
        feed = self.parse_day(self.day, nolist, nostr, noattrs, False)
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
        def callback(x):
            return ["classy", "beautiful"]
        feed = self.parse_day(self.day, callback, nostr, noattrs, False)
        item = feed[0]
        self.assertEqual(item[0], "starttag")
        self.assertEqual(item[1], "td")
        self.assertClassesInTag(item[2], ["classy", "beautiful"])
        item = feed[1]
        self.assertEqual(item[0], "data")
        self.assertEqual(item[1], str(self.day.day))
        item = feed[2]
        self.assertEqual(item[0], "endtag")
        self.assertEqual(item[1], "td")

    def test_attrs(self):
        def callback(x):
            return {self.key: self.value}
        feed = self.parse_day(self.day, nolist, nostr, callback, False)
        item = feed[0]
        self.assertEqual(item[0], "starttag")
        self.assertEqual(item[1], "td")
        self.assertAttributeInTag(item[2], self.key, self.value)
        item = feed[1]
        self.assertEqual(item[0], "data")
        self.assertEqual(item[1], str(self.day.day))
        item = feed[2]
        self.assertEqual(item[0], "endtag")
        self.assertEqual(item[1], "td")

    def test_link_day(self):
        def callback(x):
            return self.url
        feed = self.parse_day(self.day, nolist, callback, noattrs, False)
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
        self.date_iterator = self.calendar.itermonthdates(self.year,
                                                          self.month)
        self.html = htmlmonth(self.month, self.year,
                              classes=self.classFunction,
                              links=self.linkFunction,
                              th_classes=self.th_classes,
                              table_classes=self.table_classes,
                              caltype=self.caltype,
                              locale=None, safe=True)
        self.parser = self.parser_class()
        self.parser.feed(self.html)
        self.data = self.parser.result

    def get_table_attrs(self):
        for item in self.data:
            if item[0] == "starttag" and item[1] == "table":
                return item[2]
        raise Exception("No <table> tag found")

    def header_iterator(self):
        attrs = []
        th = False
        for item in self.data:
            if item[0] == "endtag" and item[1] == "tr":
                break
            if item[0] == "starttag" and item[1] == "th":
                th = True
                attrs = item[2]
            if item[0] == "data" and th:
                yield item[1], attrs
            if item[0] == "endtag" and item[1] == "th":
                th = False
                attrs = []

    def cell_iterator(self):
        header = True
        attrs = []
        href = ""
        td = False
        for item in self.data:
            if item[1] == '\xa0':  # In case of fill row days
                break
            if item[0] == "endtag" and item[1] == "tr":
                header = False
            if header:
                continue
            if item[0] == "starttag" and item[1] == "tr":
                pass
            elif item[0] == "starttag" and item[1] == "td":
                td = True
                attrs = item[2]
            elif item[0] == "starttag" and item[1] == "a" and is_link(item[2]):
                href = dict(item[2])["href"]
            elif item[0] == "data" and td:
                yield item[1], attrs, href
            elif item[0] == "endtag" and item[1] == "a":
                href = ""
            elif item[0] == "endtag" and item[1] == "td":
                td = False
                attrs = []
            elif item[0] == "endtag" and item[1] == "tr":
                pass

    def iter_month_days(self):
        in_month = False
        for x in self.cell_iterator():
            if x[0] == '1':
                in_month = not in_month
            if in_month:
                yield x

    def iter_rows(self):
        row = None
        td = False
        for item in self.data:
            if item[0] == 'starttag' and item[1] == "tr":
                row = []
            if item[0] == 'starttag' and item[1] == "td":
                td = True
            if item[0] == 'data' and td:
                row.append(item[1])
            if item[0] == 'endtag' and item[1] == "td":
                td = False
            if item[0] == 'endtag' and item[1] == "tr":
                yield row
                row = []

    def day_to_date(self, day):
        return date(self.year, self.month, int(day))

    def assertClasses(self, attrs, classes):
        if classes:
            attrs_dict = dict(attrs)
            self.assertIn('class', attrs_dict)
            attrs_classes = set(attrs_dict['class'].split(" "))
            self.assertEqual(attrs_classes, set(classes))

    def test_sanity(self):
        html_sanity_checker(self.html)

    def test_table(self):
        attrs = self.get_table_attrs()
        self.assertClasses(attrs, self.table_classes)

    def test_header(self):
        names = [x[0] for x in self.header_iterator()]
        week_days = hc.WEEKDAYS0 if self.caltype == 0 else hc.WEEKDAYS1
        for name1, name2 in zip(names, week_days):
            self.assertEqual(name1, name2)

    def test_month_days(self):
        for day, attrs, href in self.iter_month_days():
            date = self.day_to_date(day)
            classes = self.classFunction(date)
            if classes:
                self.assertClasses(attrs, classes)
            link = self.linkFunction(date)
            if link:
                self.assertEqual(link, href)

    def test_fill_row_days(self):
        dates = list(self.date_iterator)
        if len(dates) <= 7 * 5:
            rows = list(self.iter_rows())
            last_row = rows[-1]
            for empty in last_row:
                self.assertEqual(empty, '\xa0')


class MonthTestCase2(MonthTestCase):
    year = 2023
    month = 9
    th_classes = ["title"]
    table_classes = ["tabla"]
    caltype = 1

    def classFunction(self, date):
        day = date.day
        return ['odd'] if day % 2 else ['even']

    def linkFunction(self, date):
        return f"https://lets-party.fake/{date.year}/{date.month}/{date.day}"


class MonthTestCase3(MonthTestCase):
    year = 2035
    month = 12
    th_classes = ["title"]
    table_classes = ["tabla"]
    caltype = 1

    def classFunction(self, date):
        return [str(date.weekday())]

    def linkFunction(self, date):
        return "https://helo.fake"


class MonthsIterator(unittest.TestCase):
    sequence: List[Tuple[int, int]] = []
    iterator_function = (backwards_iterator,)
    starting = date(2023, 1, 1)
    months = 3

    def setUp(self):
        self.iterator = self.iterator_function[0](self.starting, self.months)

    def test_values(self):
        for x, y in zip(self.sequence, self.iterator):
            self.assertEqual(x, y)


class Backward1TestCase(MonthsIterator):
    starting = date(2039, 1, 1)
    months = 3
    sequence = [
                (1, 2039),
                (12, 2038),
                (11, 2038),
                ]


class Backward2TestCase(MonthsIterator):
    starting = date(2045, 6, 13)
    months = 3
    sequence = [
                (6, 2045),
                (5, 2045),
                (4, 2045),
                (3, 2045),
                (2, 2045),
                (1, 2045),
                (12, 2044),
                (11, 2044),
                (10, 2044),
                (9, 2044),
                (8, 2044),
                (7, 2044),
                (6, 2044),
                (5, 2044),
                ]


class Forward1TestCase(MonthsIterator):
    iterator_function = (forward_iterator,)
    starting = date(2023, 2, 1)
    months = 3
    sequence = [
            (2, 2023),
            (3, 2023),
            (4, 2023),
            ]


class Forward2TestCase(MonthsIterator):
    iterator_function = (forward_iterator,)
    starting = date(2011, 6, 12)
    months = 8
    sequence = [
            (6, 2011),
            (7, 2011),
            (8, 2011),
            (9, 2011),
            (10, 2011),
            (11, 2011),
            (12, 2011),
            (1, 2012),
            (2, 2012),
            ]


class WhiteBoxHtmlCalendar1TestCase(unittest.TestCase):
    starting_date = date(2025, 9, 1)
    months = 5
    backwards = True
    caltype = 0
    th_classes = ['thclass']
    table_classes = ['tableclass']
    header = "h3"
    locale = None
    safe = False

    def setUp(self):
        self.classes = Mock()
        self.links = Mock()
        self.attrs = Mock()
        self.th_classes = Mock()
        self.table_classes = Mock()

    @patch('htmlcalendar.htmlmonth')
    def test_months(self, month_mock):
        result = htmlcalendar(self.starting_date,
                              months=self.months,
                              classes=self.classes,
                              links=self.links,
                              attrs=self.attrs,
                              th_classes=self.th_classes,
                              table_classes=self.table_classes,
                              caltype=self.caltype,
                              backwards=self.backwards,
                              header=self.header,
                              locale=self.locale,
                              safe=self.safe)

        # Sanity call check
        for item in result:
            html_sanity_checker(item)

        # Basic htmlmonths calls
        self.assertTrue(month_mock.called)
        self.assertEqual(month_mock.call_count, self.months)

        # Redundant htmlmonth calls checker
        iterator = backwards_iterator if self.backwards else forward_iterator
        calls = []
        for month, year in iterator(self.starting_date, self.months - 1):
            c = call(month,
                     year,
                     classes=self.classes,
                     links=self.links,
                     attrs=self.attrs,
                     th_classes=self.th_classes,
                     table_classes=self.table_classes,
                     caltype=self.caltype,
                     header=self.header,
                     locale=self.locale,
                     safe=self.safe)
            calls.append(c)
        self.assertEqual(len(month_mock.call_args_list), len(calls))
        self.assertListEqual(month_mock.call_args_list, calls)


class WhiteBoxHtmlCalendar2TestCase(WhiteBoxHtmlCalendar1TestCase):
    starting_date = date(2025, 9, 1)
    months = 5
    backwards = True
    caltype = 0
    th_classes = ['thclass']
    table_classes = ['tableclass']


class BlackBoxHtmlCalendarTestCase(unittest.TestCase):
    starting_date = date(2025, 9, 1)
    months = 5
    backwards = True
    caltype = 0
    th_classes = ['thclass']
    table_classes = ['tableclass']
    header = "h3"
    locale = None
    safe = True

    def setUp(self):
        self.classes = (lambda x: ["my_class"],)
        self.links = (lambda x: "https://nowhere",)
        self.attrs = (lambda x: {"onclick": "testcall()"})
        self.th_classes = self.th_classes
        self.table_classes = self.table_classes
        self.calendar = htmlcalendar(self.starting_date,
                                     months=self.months,
                                     classes=self.classes[0],
                                     links=self.links[0],
                                     th_classes=self.th_classes,
                                     table_classes=self.table_classes,
                                     caltype=self.caltype,
                                     backwards=self.backwards,
                                     header=self.header,
                                     locale=self.locale,
                                     safe=self.safe)
        self.calendar = "\n".join(self.calendar)

    def test_black_box(self):
        html_sanity_checker(self.calendar)
        parser = CalParser()
        parser.feed(self.calendar)
        month_counter = 0
        for item in parser.result:
            if item[0] == 'starttag' and item[1] == self.header:
                month_counter += 1
        self.assertEqual(month_counter, self.months)


if __name__ == "__main__":
    unittest.main()

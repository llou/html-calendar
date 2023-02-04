import importlib
from datetime import date
import unittest
from html.parser import HTMLParser
from htmlcalendar import (htmlcalendar, htmlday, htmlmonth, get_months, nolist,
        nostr)


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


class DayTestCase(unittest.TestCase):
    day = date(2023, 5, 8)
    parser = CalParser
    url = "https://nowhere"

    def setUp(self):
        self.parser = self.parser()

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


if __name__ == "__main__":
    unittest.main()


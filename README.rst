
HTML Calendar
=============

This module has the simple poupose of building html calendar tables with links
and formatting. It is totally framework agnostic.

The module provides the ``htmlcalendar`` Python function that takes an starting
date and a number of months for rendering the HTML Tables containing the
specified months with formated cells and HTML links on day's numbers.

Formatting is provided by passing a callback function as the ``classes``
parameters that takes the date and returns a list of CSS classes that are
applied to the date's cell.

Linking dates to URLs is also provided by a callback function passed as the
``links`` parameter that takes the date and returns a fully qualified HTML link
if required or ``None`` if not.

You can also format the days that are not in the month but appear in the table
with the option ``no_month_class``. And the classes for formatting the headers
and the table using the options ``th_classes`` and ``table_classes``.

I also support North American calendar with the option ``caltype`` putting its
value to 1.

.. code-block::

    from htmlcalendar import htmlcalendar

    def link(date):
        if date.weekday == 5:
            return "https://lets-party.domain"

    def css_class(date):
        if date.weekday == 5:
            return "party"

    html_table = htmlcalendar(links=link, classes=css_class)

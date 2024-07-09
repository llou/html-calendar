
HTML Calendar
=============

This module has the simple purpose of building html calendar tables with links
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

For formatting the headers and the table you can use css classes in a list with
the options ``th_classes`` and ``table_classes``.

Attributes dictionary is added for allowing further customization of the
calendar with the keyword ``attrs``. Then, for ensuring safety on the building
of the calendar the ``safe`` option is added to escape all the variables that
are rendered building the calendar when it is disabled.

It also supports North American calendar with the option ``caltype`` putting
its value to 1.

.. code-block:: python

  from flask import Flask
  from datetime import date
  from htmlcalendar import htmlcalendar

  app = Flask("party")

  def links(date):
	  if date.weekday() == 5:
		  return "https://github.com/llou/html-calendar"

  def css_class(date):
	  if date.weekday() == 5:
		  return ["party"]

  def attrs(date):
      return {"onclick": f"whatever({date.year}, {date.month}, {date.day})"}

  @app.route("/")
  def party_calendar():
	  return htmlcalendar(date.today(), months=1, links=links, classes=css_class)

You can read the documentation at https://html-calendar.readthedocs.io/en/latest/

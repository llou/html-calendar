
HTML Calendar
=============

A Python function that takes an starting date and a number of months to
generate and renders the HTML Tables containign these months with formated
cells and HTML links on days. It tries to be as symple and compatible as
possible.

Formatting is provided by the callback function ``classes`` that takes the date
and returns a list of CSS classes that applies to that day cell.

Linking is also provided by a callback function ``links`` that takes the date
and returns a fully qualified HTML link if required or the empty string if not.

You can also format the days that are not in the month but appear in the table
with the option ``no_month_class``. And the classes for formatting the headers
and the table using the options ``th_classes`` and ``table_classes``.

I also support North American calendar with the option ``caltype`` putting its
value to 1.

Localization of weekdays names is still pending.

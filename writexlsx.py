"""## Write Dataframe to Excel(xlsx) with customized styles

Similar to the `to_excel()` method of Pandas's Dataframe.
However, it will set a wider column width for `date` and `datetime`
objects. The font, the background color and the cell grid line will
be set accordingly.

## Main Feature
1. Set the font to *微软雅黑 + Arial*
1. The index always starts from 1 instead of 0
1. Set horizontal line but no vertical line
1. Set the background of the header to heavy blue and the forefont header to white
1. Enable the filter by default
1. Support *comma* and *percent* formatting when specifying the columns
1. Support multiple Dataframe in `list`, `tuple` or `dict`

## Plan
Plan to submit to `pip` when matured
"""

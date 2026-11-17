*** Settings ***
Documentation  Faceted layout "Faceted table items" on eea_folder (test fixture).
...            Version-independent: Plone selectors are in ui_plone*.robot.
Resource  z3ctable.robot
Test Setup  Open a manager browser
Test Teardown  Close all browsers


*** Test Cases ***
The folder items are listed in the results table
    Add content to the faceted folder  Document  Bravo  Alpha  Charlie
    Open the faceted folder
    The table lists  Alpha  Bravo  Charlie
    The items count is  3

A column header sorts the results
    Add content to the faceted folder  Document  Bravo  Alpha  Charlie
    Open the faceted folder
    No column is sorted
    Sort the column  Title  ascending
    The column is sorted  Title  ascending
    The titles are in this order  Alpha  Bravo  Charlie
    Sort the column  Title  descending
    The column is sorted  Title  descending
    The titles are in this order  Charlie  Bravo  Alpha

A search that matches nothing shows no table
    [Documentation]  The default "Portal type" criterion (Document) matches nothing: the folder holds a folder only
    Add content to the faceted folder  Folder  Archives
    Open the faceted folder
    The no results message is shown

The header checkbox selects and unselects every row
    Add content to the faceted folder  Document  Alpha  Bravo
    Open the faceted folder
    The table lists  Alpha  Bravo
    All rows are selected  ${True}
    Click the select all checkbox
    All rows are selected  ${False}
    Click the select all checkbox
    All rows are selected  ${True}

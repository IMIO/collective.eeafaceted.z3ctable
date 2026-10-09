*** Settings ***
Documentation  collective.eeafaceted.z3ctable keywords, built on the ui_plone${PLONE_MAJOR}.robot keywords.
...            Robot Framework 3.1 syntax (FOR ... END; shared with the Plone 4.3 environment, RF 3.2.2).
...            The faceted folder is eea_folder of the test fixture (layout faceted-table-items) with the
...            default eea criteria: c1 portal type (default Document), c2 hidden sorting.
Resource  ui_plone${PLONE_MAJOR}.robot


*** Variables ***
${TABLE}  css=#faceted_table
${TITLE_CELLS}  \#faceted_table tbody td.td_cell_Title
${ROW_CHECKBOXES}  \#faceted_table tbody input[name="select_item"]
${SELECT_ALL}  css=#select_unselect_items


*** Keywords ***
Open a manager browser
    Open test browser
    Enable autologin as  Manager

Add content to the faceted folder
    [Arguments]  ${type}  @{titles}
    ${folder_uid}=  Path to uid  /${PLONE_SITE_ID}/eea_folder
    FOR  ${title}  IN  @{titles}
        Create content  type=${type}  container=${folder_uid}  title=${title}
    END

Open the faceted folder
    Go to  ${PLONE_URL}/eea_folder
    Wait until page contains element  css=#faceted-results .table_faceted_results

The table lists
    [Arguments]  @{titles}
    Wait until page contains element  ${TABLE}
    ${count}=  Get length  ${titles}
    ${rows}=  Get element count  css=${TITLE_CELLS}
    Should be equal as integers  ${rows}  ${count}
    FOR  ${title}  IN  @{titles}
        Element should contain  ${TABLE}  ${title}
    END

The items count is
    [Arguments]  ${number}
    Element text should be  css=#search-results-number  ${number}
    Element should contain  css=.table_faceted_results  items matching your search terms.

The titles are in this order
    [Arguments]  @{titles}
    ${expected}=  Catenate  SEPARATOR=|  @{titles}
    Wait until keyword succeeds  10s  0.5s  Title cells are  ${expected}

Title cells are
    [Arguments]  ${expected}
    ${titles}=  Execute javascript
    ...  return Array.prototype.map.call(document.querySelectorAll('${TITLE_CELLS}'), function(e) {return e.textContent.trim();}).join('|');
    Should be equal  ${titles}  ${expected}

Sort the column
    [Documentation]  Click the sort arrow of the column header, ${order}: ascending or descending
    [Arguments]  ${column}  ${order}
    Click element  css=th.th_header_${column} a[title="Sort ${order}"]

The column is sorted
    [Documentation]  The header shows the active arrow, ${order}: ascending or descending
    [Arguments]  ${column}  ${order}
    ${arrow}=  Set variable if  '${order}' == 'ascending'  ▲  ▼
    Wait until element contains  css=th.th_header_${column} a.sort_arrow_enabled  ${arrow}

No column is sorted
    Page should not contain element  css=#faceted_table th a.sort_arrow_enabled

The no results message is shown
    Wait until element contains  css=.table_faceted_no_results  No results were found.
    Page should not contain element  ${TABLE}

Click the select all checkbox
    Click element  ${SELECT_ALL}

All rows are selected
    [Documentation]  ${selected}: True (every row checkbox checked) or False (none checked)
    [Arguments]  ${selected}
    ${rows}=  Get element count  css=${ROW_CHECKBOXES}
    Should be true  ${rows} > 0
    ${checked}=  Get element count  css=${ROW_CHECKBOXES}:checked
    ${expected}=  Set variable if  ${selected}  ${rows}  0
    Should be equal as integers  ${checked}  ${expected}
    Run keyword if  ${selected}  Checkbox should be selected  ${SELECT_ALL}
    ...  ELSE  Checkbox should not be selected  ${SELECT_ALL}

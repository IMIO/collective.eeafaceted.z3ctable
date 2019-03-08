// (un)select every checkboxes
function toggleCheckboxes(checkBoxId) {
    checkbox = $('input#select_unselect_items');
    if (checkbox[0].checked) {
        $('input[name="' + checkBoxId + '"]').each(function() {
            this.checked = true;
        });
    }
    else {
        $('input[name="' + checkBoxId + '"]').each(function() {
            this.checked = false;
        });
    }
}

// select all pages, select every checkboxes and disable it
function selectAllPages(checkBoxId) {
    checkbox = $('input#select_all_pages');
    select_unselect_items_checkbox = $('input#select_unselect_items')[0];
    if (checkbox[0].checked) {
        select_unselect_items_checkbox.disabled = true;
        $('input[name="' + checkBoxId + '"]').each(function() {
            this.checked = true;
            this.disabled = true;
        });
    }
    else {
        select_unselect_items_checkbox.disabled = false;
        $('input[name="' + checkBoxId + '"]').each(function() {
            this.disabled = false;
        });
    }
}

// helper method that returns selected checkboxes
function selectedCheckBoxes(checkBoxId) {
    selected_boxes = [];
    select_all_pages_checkbox = $('input#select_all_pages')[0];
    if (!select_all_pages_checkbox.checked) {
        i = 0;
        $('input[name="' + checkBoxId + '"]').each(function() {
            if (this.checked) {
                selected_boxes[i] = this.value;
                i = i + 1;
            }
        });
    } else {
        // do an ajax query to get every uids depending on current query
    }
    return selected_boxes;
}

// method initializing allPages checkbox
function initializeAllPagesCheckbox(checkBoxId) {
    checkbox = $('input#select_all_pages');
    if (checkbox[0].checked) {
        selectAllPages(checkBoxId);
    }
}

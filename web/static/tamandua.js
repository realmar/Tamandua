/*
 * Global Variables
 */
var expressionLineTemplate = null;
var expressionLines = [];

/*
 * Setup Functions
 */

function setup_selectizer(item) {
    item.selectize({
        create: true,
        sortField: 'text'
    });
}

function setup_datetimepicker(item) {
    item.datetimepicker();
}

/*
 * Creational/Destructional Functions
 */

function add_expression_line() {
    if(expressionLineTemplate === null) {
        // TODO: handle
        return;
    }

    var newExp = expressionLineTemplate.clone();

    newExp.appendTo("#expression-container");
    setup_selectizer(newExp.find(".expression-select"));
    newExp.find(".expression-remove-button").click(function () {
        remove_expression_line($(this).parent().parent());
    });

    expressionLines.push(newExp);
}

function remove_expression_line(item) {
    var index = expressionLines.indexOf(item);
    expressionLines.splice(index, 1);
    item.remove();
}

/*
 * Event Handlers
 */

function on_add_expression_line_button_click() {
    var addLine = true;

    // Check if an expression doesn't have any value
    // if so, then we will not create a new expression line (return)
    $.each(expressionLines, function () {
        expInput = $(this).find(".expression-input");
        if(!expInput.val()) {
            addLine = false;
        }
    });

    if(addLine) {
        add_expression_line();
    }
}

function on_add_from_dt_button_click() {

}

function on_remove_from_dt_button_click() {

}

function on_add_to_dt_button_click() {

}

function on_remove_to_dt_button_click() {

}

function on_get_sample_button_click() {

}

function on_get_all_button_click() {

}

function on_search_button_click() {

}

/*
 * Init
 */

function init_global_variables() {
    expressionLineTemplate = $("#expression-templates > .expression-line");
}

function register_event_handlers() {
    $("#add-expression-line-button").click(on_add_expression_line_button_click);
    $("#add-from-dt-button").click(on_add_from_dt_button_click);
    $("#remove-from-dt-button").click(on_remove_from_dt_button_click);
    $("#add-to-dt-button").click(on_add_to_dt_button_click);
    $("#remove-to-dt-button").click(on_remove_to_dt_button_click);
    $("#get-sample-button").click(on_get_sample_button_click);
    $("#get-all-button").click(on_get_all_button_click);
    $("#search-button").click(on_search_button_click);
}

function main() {
    init_global_variables();
    register_event_handlers();
    setup_datetimepicker($("#dt-from-picker"));
    setup_datetimepicker($("#dt-to-picker"));
    add_expression_line();
}

$(document).ready(main);
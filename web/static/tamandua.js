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

/* expression builder */

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

/* datetime */

function on_add_dt_button_click(item) {
    var parent = $(this).parent().parent();
    parent.find(".dt-add").hide();
    parent.find(".dt-search-mask").show();

}

function on_remove_dt_button_click(item) {
    var parent = $(this).parent().parent().parent();
    parent.find(".dt-search-mask").hide();
    parent.find(".dt-add").show();
}

/* API */

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
    /* expression builder */
    $("#add-expression-line-button").click(on_add_expression_line_button_click);

    /* datetime */
    $(".add-dt-button").click(on_add_dt_button_click);
    $(".remove-dt-button").click(on_remove_dt_button_click);

    /* API */
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
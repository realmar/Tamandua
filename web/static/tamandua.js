/*
 * Global Variables
 */
var expressionLineTemplate = null;
var expressionLines = [];
var footableInstance = null;

var datetimeFormat = "YYYY/MM/DD HH:mm:ss";

/*
 * API Routes
 */

var api = {
    columns: '/api/columns',
    search: '/api/search'
};

var methods = {
    post: 'POST',
    get: 'GET'
};

/*
 * Errors/Messaging
 */

uiresponses = {
    types: {
        info: {
            name: "info",
            id: "#result-info"
        },
        error: {
            name: "error",
            id: "#search-error"
        }
    },

    messages: {
        noresults: {
            type: "info",
            id: "#result-info-no-results"
        }
    },
    errors: {
        searcherror: {
            type: "error",
            id: "#search-error-generic"
        }
    },

    none: ""
};

function show_message(msg, data) {
    var box = $(uiresponses.types[msg.type].id);
    box.each(function () {
        $(this).hide();
    });

    if(data !== "") {
        $(msg.id).html(data);
    }

    $(msg.id).show();
    box.show();
}

function remove_messages_of_type(t) {
    $(t.id).hide();
}

function remove_all_messages() {
    for(var t in uiresponses.types) {
        remove_messages_of_type(uiresponses.types[t]);
    }
}

/*
 * UI Loading
 */

function show_loading_spinner() {
    $("#search-loading").show();
}

function hide_loading_spinner() {
    $("#search-loading").hide();
}

/*
 * Setup Functions
 */

function setup_selectizer(item) {
    var $select = item.selectize({
        create: true,
        sortField: 'text'
    });

    var selectize = $select[0].selectize;

    $('.selectize-input').click(function () {
        selectize.clear(true);
    });

    return selectize;
}

function setup_datetimepicker(item) {
    item.datetimepicker({
        format : 'DD/MM/YYYY HH:mm'
    });
}

/*
 * Creational/Destructional Functions
 */

function add_expression_line() {
    if(expressionLineTemplate === null) {
        return;
    }

    var newExp = expressionLineTemplate.clone();
    newExp.appendTo("#expression-container");

    instance = setup_selectizer(newExp.find(".expression-select"));

    newExp.find(".expression-remove-button").click(function () {
        on_remove_expression_line_button_click($(this).parent().parent());
    });

    expressionLines.push([newExp, instance]);
}

function on_remove_expression_line_button_click(item) {
    for(i in expressionLines) {
        if(expressionLines[i][0][0] === item[0]) {
            expressionLines.splice(i, 1);
        }
    }

    item.remove();
}

function reset_result_table() {
    remove_all_messages();
    $("#results").find(".remove").each(function () { $(this).remove(); });
    $("#result-container").empty();
    $("#result-container").html("<table id=\"result-table\" data-paging=\"true\" data-filtering=\"true\" data-sorting=\"true\"></table>");
}

/*
 * Event Handlers
 */

/* expression builder */

function has_empty_expression_fields() {
    var hasEmptyFields = false;

    $.each(expressionLines, function () {
        var expInput = $(this[0]).find(".expression-input");
        if(!expInput.val()) {
            hasEmptyFields = true;
        }
    });

    return hasEmptyFields;
}

function on_add_expression_line_button_click() {
    // Check if an expression doesn't have any value
    // if so, then we will not create a new expression line (return)

    if(!has_empty_expression_fields()) {
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

function handle_ajax_error(jqxhr, textStatus, error) {
    hide_loading_spinner();
    console.log("Error in async operation: " + [jqxhr, textStatus, error]);
    show_message(uiresponses.errors.searcherror, "Failed to get data from server: " + textStatus);
}

function get_rows(route, data, method, columns) {
    $.ajax({
        url: route,
        type: method,
        data: data,
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    })
        .done(function (rows) {
            hide_loading_spinner();

            if("message" in rows) {
                show_message(
                    uiresponses.errors.searcherror,
                    "An error on the server occured:<br>" +
                    "<span class=\"bold\">Details: </span>" + rows["message"] + "<br>");

                return;
            }

            /*
             * Verify result
             */

            if(rows.length === 0) {
                show_message(uiresponses.messages.noresults, uiresponses.none);
                return;
            }

            /*
             * Formatter
             */

            var find_element = function (elementName) {
                return columns.find(function (element) {
                    return element.name === elementName;
                });
            };

            var add_formatter = function (element, formatter, parser) {
                if(element !== undefined) {
                    element["formatter"] = formatter;
                    element["parser"] = parser;
                }
            };

            var format_code = function (elementName) {
                var code_formatter = function (value) {
                    value = value
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;');

                    return "<pre>" + value + "</pre>";
                };

                var codeParser = function (valueOrElement) {
                    if(valueOrElement instanceof Array) {
                        var finalStr = '';
                        for(i in valueOrElement) {
                            finalStr += valueOrElement[i];
                        }

                        return finalStr;
                    }else {
                        return String(valueOrElement);
                    }
                };

                add_formatter(find_element(elementName), code_formatter, codeParser);
            };

            /*
             * Create FooTable instance
             */

            format_code("loglines");

            var options = {
                toggleColumn: "first",

                columns : columns,
                rows: rows,

                paging: {
                    size: 20
                }
            };

            footableInstance = new FooTable.Table($("#result-table"), options, function () {
                footableInstance.sort('phdmxin_time', 'ASC');
            });
        })
        .fail(handle_ajax_error);
}

function get_json(route, data, method) {
    reset_result_table();

    if(method === methods.post) {
        data = JSON.stringify(data)
    }

    show_loading_spinner();

    $.ajax({
        url: api.columns,
        type: methods.get,
        dataType: "json"
    })
    .done(function (columns) {
        get_rows(route, data, method, columns);
    })
    .fail(handle_ajax_error);
}

function on_search_button_click() {
    /*
     * useful clojures for this function
     */

    var getDT = function (root, item) {
        if(root.is(":visible")) {
            try {
                return item.datetimepicker('date').format(datetimeFormat);
            } catch (e) {
                // console.log(e);
                return "";
            }
        }else{
            return "";
        }
    };

    var getFromDT = function () {
        return getDT($("#dt-from-search-mask"), $("#dt-from-picker"));
    };

    var getToDT = function () {
        return getDT($("#dt-to-search-mask"), $("#dt-to-picker"));
    };

    /*
     * Validate Fields
     */

    if(has_empty_expression_fields()) {
        show_message(uiresponses.errors.searcherror, "Some Field Values are empty, please delete them or fill in content.");
        return;
    }

    if(expressionLines.length === 0 && !getFromDT() && !getToDT()) {
        show_message(uiresponses.errors.searcherror, "The searchmask is empty. Specify some search criteria.");
        return;
    }

    if(expressionLines === null) {
        return;
    }

    /*
     * Build Expression
     */

    var expression = {
        fields: [],
        datetime: {
            start: "",
            end: ""
        }
    };

    $.each(expressionLines, function () {
        var jq = this[0];
        var s = this[1];

        var key = s.getValue();
        var value = jq.find(".expression-input").val();

        var h = {};
        h[key] = value;

        expression.fields.push(h);
    });

    expression.datetime.start = getFromDT();
    expression.datetime.end = getToDT();

    get_json(api.search, expression, methods.post);
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
    $("#search-button").click(on_search_button_click);
}

function main() {
    init_global_variables();
    register_event_handlers();
    setup_datetimepicker($("#dt-from-picker"));
    setup_datetimepicker($("#dt-to-picker"));
}

$(document).ready(main);
/*
 * Global Variables
 */
var expressionLineTemplate = null;
var expressionLines = [];

/*
 * API Routes
 */

var api = {
    'get': {
        'sample': '/api/get/sample',
        'all': '/api/get/all'
    },

    'search': '/api/search'
};

var methods = {
    'post': 'POST',
    'get': 'GET'
};

/*
 * Errors/Messaging
 */

uiresponses = {
    "types": {
        "info": {
            "name": "info",
            "id": "#result-info"
        },
        "error": {
            "name": "error",
            "id": "#search-error"
        }
    },

    "messages": {
        "noresults": {
            "type": "info",
            "id": "#result-info-no-results"
        }
    },
    "errors": {
        "searcherror": {
            "type": "error",
            "id": "#search-error-generic"
        }
    },

    "none": ""
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
 * Setup Functions
 */

function setup_selectizer(item) {
    var $select = item.selectize({
        create: true,
        sortField: 'text'
    });

    return $select[0].selectize;
}

function setup_datetimepicker(item) {
    item.datetimepicker();
}

function setup_checkbox(item) {
    item.checkboxpicker();
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

    instance = setup_selectizer(newExp.find(".expression-select"));

    newExp.find(".expression-remove-button").click(function () {
        remove_expression_line($(this).parent().parent());
    });

    expressionLines.push([newExp, instance]);
}

function remove_expression_line(item) {
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

function get_json(route, data, method) {
    reset_result_table();

    data['only_important'] = $("#only-important-checkbox").prop("checked");

    if(method === methods.post) {
        data = JSON.stringify(data)
    }

    $.ajax({
        url: route,
        type: method,
        data: data,
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    })
        .done(function (data) {
            if("exception" in data) {
                show_message(
                    uiresponses.errors.searcherror,
                    "An error on the server occured:<br>" +
                    "<span class=\"bold\">Type: </span>" + data["exception"]["type"] + "<br>" +
                    "<span class=\"bold\">Message: </span>" + data["exception"]["message"]);

                return;
            }

            if(
                !("columns" in data)            ||
                !("rows" in data)               ||
                data["columns"].length === 0    ||
                data["rows"].length === 0
            ) {
                show_message(uiresponses.messages.noresults, uiresponses.none);
                return;
            }

            $("#result-table").footable(data);
        })
        .fail(function (jqxhr, textStatus, error) {
            console.log("Error in async operation: " + [jqxhr, textStatus, error]);
            show_message(uiresponses.errors.searcherror, "Failed to get data from server: " + textStatus);
        });
}

function on_get_sample_button_click() {
    get_json(api.get.sample, {}, methods.get);
}

function on_get_all_button_click() {
    get_json(api.get.all, {}, methods.get);
}

function on_search_button_click() {
    /*
     * useful clojures for this function
     */

    var getDT = function (root, item) {
        if(root.is(":visible")) {
            try {
                return item.datetimepicker('date').format("YYYY/MM/DD HH:mm:ss");
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
        "fields": [],
        "datetime": {
            "start": "",
            "end": ""
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
    $("#get-sample-button").click(on_get_sample_button_click);
    $("#get-all-button").click(on_get_all_button_click);
    $("#search-button").click(on_search_button_click);
}

function main() {
    init_global_variables();
    register_event_handlers();
    setup_datetimepicker($("#dt-from-picker"));
    setup_datetimepicker($("#dt-to-picker"));
    setup_checkbox($("#only-important-checkbox"))
    // add_expression_line();
}

$(document).ready(main);
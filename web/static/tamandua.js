/*
 * Global Variables
 */
var expressionLineTemplate = null;
var expressionLines = [];

var datetimeFormat = 'YYYY/MM/DD HH:mm:ss';

var visibleColumns = [
    'phdmxin_time',
    'sender',
    'recipient'
];

/*
 * API Routes
 */

var maxPageSize = 200;

var api = {
    columns: '/api/columns',
    search: '/api/search/0/' + maxPageSize
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
            name: 'info',
            id: '#result-info'      // container
        },
        error: {
            name: 'error',
            id: '#search-error'     // container
        }
    },

    messages: {
        noresults: {
            type: 'info',
            id: '#result-info-no-results'       // p-tag
        },
        toomanyresults: {
            type: 'info',
            id: '#result-info-too-may-results'
        }
    },

    errors: {
        searcherror: {
            type: 'error',                      // mapping with types, to display the container
            id: '#search-error-generic'         // p-tag
        },
        receivedinvalid: {
            type: 'error',
            id: '#search-error-received-invalid'
        }
    },

    none: ''
};

function show_message(msg, data) {
    var box = $(uiresponses.types[msg.type].id);
    box.each(function () {
        $(this).hide();
    });

    if(data !== '') {
        $(msg.id).html(data);
    }

    $(msg.id).show();
    box.show();
}

function remove_messages_of_type(t) {
    $(t.id).hide();
    $(t.id).find('p').each(function () { $(this).hide(); });
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
    $('#search-loading').show();
}

function hide_loading_spinner() {
    $('#search-loading').hide();
}

/*
 * Setup Functions
 */

function setup_selectizer(item) {
    var $select = item.selectize({
        create: true,
        sortField: 'text',
        onFocus: function () {
            if(!item.data('noclear')) {
                this.clear(true);
            }
        }
    });

    return $select[0].selectize;
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
    newExp.appendTo('#expression-container');

    instance = setup_selectizer(newExp.find('.expression-select'));

    newExp.find('.expression-remove-button').click(function () {
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

/*
 * Event Handlers
 */

/* expression builder */

function has_empty_expression_fields() {
    var hasEmptyFields = false;

    $.each(expressionLines, function () {
        var expInput = $(this[0]).find('.expression-input');
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
    parent.find('.dt-add').hide();
    parent.find('.dt-search-mask').show();

}

function on_remove_dt_button_click(item) {
    var parent = $(this).parent().parent().parent();
    parent.find('.dt-search-mask').hide();
    parent.find('.dt-add').show();
}

/* API */

function handle_ajax_error(jqxhr, textStatus, error) {
    hide_loading_spinner();
    console.log('Error in async operation: ' + [jqxhr, textStatus, error]);

    try {
        show_message(
            uiresponses.errors.searcherror,
            'An error on the server occured:<br>' +
            '<span class="bold">Details: </span>' + jqxhr.responseJSON.message + '<br>');
    }catch (e) {
        show_message(uiresponses.errors.searcherror, 'Failed to get data from server: ' + textStatus);
    }
}

function empty_table() {
    show_loading_spinner();
    remove_all_messages();

    $('#results').find('.remove').remove();
    $(".pager").hide();

    var result_table = $("#result-table");

    result_table.trigger("destroy");
    // result_table.empty();
    result_table.find('thead').remove();
    result_table.find('tbody').remove();
    result_table.append('<thead style="display: none;"></thead><tbody></tbody>');
}

function append_rows(expression, columns, callback) {
    $.ajax({
        url: api.search,
        type: methods.post,
        data: JSON.stringify(expression),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json'
    })
    .done(function (data) {
        if( data &&
            data.hasOwnProperty('rows') &&
            data.hasOwnProperty('total_rows')
        ) {
            if(data['rows'].length === 0) {
                show_message(uiresponses.messages.noresults, '');
                hide_loading_spinner();
                return;
            }

            if(data['total_rows'] > maxPageSize) {
                show_message(uiresponses.messages.toomanyresults,
                    'Too many matches, only showing ' +
                        '<b>' + data['rows'].length + '</b> out of ' +
                        '<b>' + data['total_rows'] + '</b>. ' +
                    'Please do a more specific search.'
                )
            }

            $('#pager').prop('colspan', visibleColumns.length + 1);
            var result_table_tbody = $('#result-table > tbody');

            var rows = '';

            for(var r in data['rows']) {
                var visibleRow =
                    '<tr>' +
                        '<td class="toggle tab-col-visible">' +
                            '<span class="glyphicon glyphicon-plus tab-col-toggle-icon"></span>';

                var childRow =
                    '<tr class="tablesorter-childRow">' +
                        '<td colspan="' + (visibleColumns.length + 1) + '">' +
                            '<div>';

                var loglines = '';
                var childRowEnd = '</div></td>';
                var visibleRowMap = {};

                for (var i in columns) {
                    var rowData = '';

                    if(data['rows'][r].hasOwnProperty(columns[i])) {
                        rowData = data['rows'][r][columns[i]];

                        if(rowData instanceof Array) {
                            var replacement = '\n';
                            if(columns[i] === 'loglines') {
                                replacement = '';
                            }
                            rowData = rowData.join(replacement);
                        }
                    }

                    if(visibleColumns.indexOf(columns[i]) === -1) {
                        var tmp = '';

                        if(columns[i] === 'loglines') {
                            rowData = rowData.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                            rowData = '<pre><code>' + rowData + '</code></pre>';
                        }

                        tmp =
                            '<div class="inline tab-row">' +
                                '<div class="inline tab-col-left">' + columns[i] + '</div>' +
                                '<div class="inline tab-col-right">' + rowData + '</div>' +
                            '</div>';

                        if(columns[i] === 'loglines') {
                            loglines = tmp;
                        }else{
                            childRow += tmp;
                        }
                    }else{
                        visibleRowMap[columns[i]] = rowData;
                    }
                }

                var isFirst = true;
                for(var j in visibleColumns) {
                    if(visibleRowMap.hasOwnProperty(visibleColumns[j])) {
                        if(isFirst) {
                            visibleRow += visibleRowMap[visibleColumns[j]] + '</td>';
                        isFirst = false;
                        }else{
                            visibleRow += '<td class="tab-col-visible">' + visibleRowMap[visibleColumns[j]] + '</td>';
                        }
                    }else{
                        if(isFirst) {
                            visibleRow += '</td>';
                            isFirst = false;
                        }else{
                            visibleRow += '<td class="tab-col-visible"></td>';
                        }
                    }
                }

                rows += visibleRow + '</tr>' + childRow  + loglines + childRowEnd + '</tr>';
            }

            result_table_tbody.append($(rows));

            /* return [
                data['total_rows'],
                $(rows)
            ]; */
        }
        callback();
    })
    .fail(handle_ajax_error);
}

function reset_table(expression, callback) {
    empty_table();

    $.ajax({
        url: api.columns,
        type: methods.get,
        dataType: 'json'
    })
    .done(function (columns) {
        if(!columns instanceof Array || columns.length == 0) {
            show_message(uiresponses.errors.receivedinvalid, uiresponses.none);
            hide_loading_spinner();
            return;
        }

        var result_table_thead = $('#result-table > thead');

        result_table_thead.append('<tr></tr>');
        var tr_head = result_table_thead.find('tr');

        // validate received data

        for(var i in columns) {
            if($.type(columns[i]) !== 'string') {
                empty_table();
                show_message(uiresponses.errors.receivedinvalid, uiresponses.none);
                hide_loading_spinner();
                return;
            }
        }

        // add headers

        for(var i in visibleColumns) {
            tr_head.append('<th>' + visibleColumns[i] + '</th>');
        }

        append_rows(expression, columns, callback);
    })
    .fail(handle_ajax_error);
}

function initialize_table(expression, columns) {
    var jTable = $('#result-table');

    jTable
        .tablesorter({
            theme : 'default',
            widthFixed: true,

            cssChildRow: 'tablesorter-childRow',

            widgets: [ 'zebra', 'filter' ],
            widgetOptions : {
                zebra : [ 'normal-row', 'alt-row' ],

                filter_placeholder: { search : 'Search...' },
                filter_childRows  : true,
                filter_cssFilter  : 'tablesorter-filter',
                filter_startsWith : false,
                filter_ignoreCase : true
            }
        })
        .tablesorterPager({
            container: $(".pager"),
            countChildRows: false,
            removeRows: true,
            updateArrows: true,

            cssNext: '.next',
            cssPrev: '.prev',
            cssFirst: '.first',
            cssLast: '.last',
            cssGoto: '.gotoPage',

            cssPageDisplay: '.pagedisplay',
            cssPageSize: '.pagesize',

            processAjaxOnInit: true,
            output: '{startRow} to {endRow} ({totalRows})',
            page: 0,
            size: 20
        });

    var hide_child_rows = function() {
        $('.tablesorter-childRow td').hide();
        $("#pager").show();
        $("#result-table > thead").show();
    };

    // register events

    jTable.bind('pagerComplete', function (e, d) {
        hide_child_rows();
    });

    jTable.delegate('.toggle', 'click' ,function(e, d) {
        $(this).closest('tr').nextUntil('tr:not(.tablesorter-childRow)').find('td').toggle();
        return false;
    });

    jTable.trigger('pageSet', 0);

    hide_child_rows();
    hide_loading_spinner();
}

function on_search_button_click() {
    /*
     * useful clojures for this function
     */

    var getDT = function (root, item) {
        if(root.is(':visible')) {
            try {
                return item.datetimepicker('date').format(datetimeFormat);
            } catch (e) {
                // console.log(e);
                return '';
            }
        }else{
            return '';
        }
    };

    var getFromDT = function () {
        return getDT($('#dt-from-search-mask'), $('#dt-from-picker'));
    };

    var getToDT = function () {
        return getDT($('#dt-to-search-mask'), $('#dt-to-picker'));
    };

    /*
     * Validate Fields
     */

    if(has_empty_expression_fields()) {
        show_message(uiresponses.errors.searcherror, 'Some Field Values are empty, please delete them or fill in content.');
        return;
    }

    if(expressionLines.length === 0 && !getFromDT() && !getToDT()) {
        show_message(uiresponses.errors.searcherror, 'The searchmask is empty. Specify some search criteria.');
        return;
    }

    if(expressionLines === null) {
        return;
    }

    /*
     * Build Expression
     */

    var expression = {
        fields: [{'complete': 'True'}],
        datetime: {
            start: '',
            end: ''
        }
    };

    $.each(expressionLines, function () {
        var jq = this[0];
        var s = this[1];

        var key = s.getValue();
        var value = jq.find('.expression-input').val();

        var h = {};
        h[key] = value;

        expression.fields.push(h);
    });

    expression.datetime.start = getFromDT();
    expression.datetime.end = getToDT();

    reset_table(expression, initialize_table);
}

/*
 * Init
 */

function init_global_variables() {
    expressionLineTemplate = $('#expression-templates > .expression-line');
}

function register_event_handlers() {
    /* expression builder */
    $('#add-expression-line-button').click(on_add_expression_line_button_click);

    /* datetime */
    $('.add-dt-button').click(on_add_dt_button_click);
    $('.remove-dt-button').click(on_remove_dt_button_click);

    /* API */
    $('#search-button').click(on_search_button_click);
}

function main() {
    init_global_variables();
    register_event_handlers();
    setup_datetimepicker($('#dt-from-picker'));
    setup_datetimepicker($('#dt-to-picker'));
    setup_selectizer($(".pagesize"));
}

$(document).ready(main);
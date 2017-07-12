//region Globals

/*
 * Global Variables
 */
var expressionLineTemplate = null;
var expressionLines = [];
var allColumns = [];
var fieldsPerColumns = {};

var maxFieldsPerColumns = 20;

var currentColorLength = 0;

var datetimeFormat = 'YYYY/MM/DD HH:mm:ss';

var visibleColumns = [
    'phdmxin_time',
    'sender',
    'recipient'
];

var comparatorMap = {
    '=': 're_i',
    '!=': '!=',
    '&gt;': '>',
    '&lt;': '<',
    '&gt;=': '>=',
    '&lt;=': '<='
};

/*
 * dashboard
 */

var overviewHoursDefault = 24;
var lastOverviewHours = 0;
var overviewHours = overviewHoursDefault;

/*
 * API Routes
 */

var maxPageSize = 200;

var api = {
    columns: '/api/columns',
    count: '/api/count',
    advcount: '/api/advcount/',
    tags: '/api/tags',
    search: '/api/search/0/' + maxPageSize,
    fieldchoices: '/api/fieldchoices/%s/%d'
};

var methods = {
    post: 'POST',
    get: 'GET'
};

/*
 * Views
 */

//endregion

//region View Class

function SearchView() { }

SearchView.prototype = {
    setup: function () {
        $('#search-nav-link').addClass('navbar-item-active');
        $('#search-view').show()
    },

    teardown: function () {
        $('#search-nav-link').removeClass('navbar-item-active');
        $('#search-view').hide()
    }
};

function DashboardView() {
    this.interval = null;
}

DashboardView.get_precentage = function (value) {
    var total = parseInt($('#dashboard-overview-total').find('.dashboard-overview-list-item-right').html());
    return ((value / total) * 100).toFixed(2)
};

DashboardView.precentageVisualizer = function (precentage, colorRange) {
    var roundedPrecentage = Math.round(precentage);
    return '<div class="dashboard-list-precentage-visualizer" style="background-color: ' + colorRange[roundedPrecentage % (colorRange.length - 1)] + '; width: ' + roundedPrecentage + '%;"></div>'
};

DashboardView.precentageHtml = function (total, total_text, addPercentage, colorRange) {
    var totalPrecentage = DashboardView.get_precentage(total);
    var final = '';

    if(addPercentage) {
        final += DashboardView.precentageVisualizer(totalPrecentage, colorRange);
    }

    final += '<div class="dashboard-overview-list-item-left inline">' +
                total_text +
            ': </div>' +
            '<div class="dashboard-overview-list-item-right inline">' +
            parseInt(total);

    if(addPercentage) {
        final += ' (' + totalPrecentage + '%)';
    }

    final += '</div>';

    return final
};

DashboardView.go_to_field = function (fieldName, fieldValue, additionalFields) {
    change_view(new SearchView());

    for(var i in expressionLines) {
        expressionLines[i][0].remove();
    }

    expressionLines = [];

    if(additionalFields === undefined) {
        additionalFields = {};
    }

    if(Object.keys(additionalFields).length === 0) {
        additionalFields = {
            'fields': []
        }
    }

    var tmp = {};

    var exists = false;
    for(var i in additionalFields['fields']) {
        if(Object.keys(additionalFields['fields'][i])[0] === fieldName) {
            exists = true;
        }
    }

    if(!exists) {
        tmp[fieldName] = {
            'comparator': '=',
            'value': fieldValue
        };
    }

    additionalFields['fields'].push(tmp);

    /*add_expression_line();

    expressionLines[0][0].find('.expression-input').val(field);
    expressionLines[0][1].setValue('sender');

    additionalFields = additionalFields['fields'];*/

    var counter = 0;
    for(var i in additionalFields['fields']) {
        add_expression_line();

        var key = Object.keys(additionalFields['fields'][i])[0];

        var c = additionalFields['fields'][i][key]['comparator'];
        if(c === 're_i' || c ==='re') {
            c = '='
        }

        expressionLines[counter][0].find('.expression-comparator-button').html(c);
        expressionLines[counter][1].setValue(key);

        var optionselect = expressionLines[counter][0].find('.search-field-selection-select');

        if(optionselect.is(':visible')) {
            optionselect[0].selectize.createItem(additionalFields['fields'][i][key]['value']);
        }else{
            var v = additionalFields['fields'][i][key]['value'].replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            expressionLines[counter][0].find('.expression-input').val(v);
        }

        counter++;
    }

    $('.remove-dt-button').each(function () { on_remove_dt_button_click($(this)) });

    on_add_dt_button_click(
        $('#dt-from-picker').parent().parent().parent().parent().find('.add-dt-button')
    );

    $('#dt-from-picker').data("DateTimePicker").date(moment().subtract(overviewHours, 'hours'))

    on_search_button_click();
};

DashboardView.get_overview = function (callback) {
    var dt = {
        'datetime': {
            'start': moment().subtract(overviewHours, 'hours').format(datetimeFormat)
        }
    };

    var totalMailsQuery = $.extend({}, dt);

    var totalRejectQuery = $.extend({}, dt);
    totalRejectQuery['fields'] = [{
        'action': {
            'comparator': '=',
            'value': 'reject'
        }
    }];

    var totalVirusQuery = $.extend({}, dt);
    totalVirusQuery['fields'] = [{
        'virusresult': {
            'comparator': 're_i',
            'value': 'INFECTED'
        }
    }];

    function get_data(selector_arg, total_text, expression, addPrecentages, callback) {
        var selector = selector_arg;

        $.ajax({
            url: api.count,
            type: methods.post,
            data: JSON.stringify(expression),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        }).done(function (result) {
            selector.html(
                DashboardView.precentageHtml(result, total_text, addPrecentages, precentageBarFlow)
            );
            callback()
        });
    }

    get_data($('#dashboard-overview-total'), 'Total', totalMailsQuery, false, function () {
        get_data($('#dashboard-overview-virus'), 'Virus', totalVirusQuery, true, function () {});
        get_data($('#dashboard-overview-rejected'), 'Rejected', totalRejectQuery, true, function () {});
        callback();
    });
};

DashboardView.get_lists = function () {
    var dt = {
        'datetime': {
            'start': moment().subtract(overviewHours, 'hours').format(datetimeFormat)
        }
    };

    function makelist(field) {
        var query = $.extend({}, dt);
        query['advcount'] = {'field': 'sender'};

        return query;
    }

    function makelistdomain(field) {
        var query = makelist(field);
        query['advcount']['sep'] = '@';

        return query;
    }

    function get_data(selector_arg, total_selector_arg, total_text_arg, expression, field_arg, additionalSearchFields_arg) {
        var selector = selector_arg;
        var total_selector = total_selector_arg;
        var total_text = total_text_arg;
        var field = field_arg;
        var additionalSearchFields = additionalSearchFields_arg;

        $.ajax({
            url: api.advcount + 10,
            type: methods.post,
            data: JSON.stringify(expression),
            contentType: 'application/json; charset=utf-8',
            dataType: 'json'
        }).done(function (result) {
            selector.empty();

            function get_precentage(value) {
                var total = parseInt(result['total']);
                if(!isNaN(total)) {
                    return ((value / total) * 100).toFixed(2)
                }else{
                    return 0;
                }
            }

            if(total_selector !== null) {
                total_selector.html(DashboardView.precentageHtml(result['total'], total_text, true, precentageBarFlow));
            }

            for(var k in result['items']) {
                var localPrecentage = get_precentage(result['items'][k]['value']);
                var v = result['items'][k]['key'];
                var element = $('<div class="dashboard-list-item dashboard-list-overflow">' +
                    DashboardView.precentageVisualizer(localPrecentage, precentageBarColors) +
                    '<span class="dashboard-list-overflow">' + result['items'][k]['value'] + ' (' + localPrecentage + '%)</span> <span title="' + v + '" class="dashboard-list-data dashboard-list-overflow">' + v + '</span>');
                element.click(function () {
                    DashboardView.go_to_field(field, $(this).find('.dashboard-list-data').html(), additionalSearchFields)

                });
                selector.append(element);
            }
        }.bind(this));
    }

    var sendersQuery = makelist('sender');
    var senderDomainsQuery = makelistdomain('sender');
    var sendersAdditionalFields = {'fields': [{
        'deliverystatus': {
            'comparator': '=',
            'value': 'sent'
        }
    }]};

    var greylistedQuery = makelist('sender');
    var greylistedDomainsQuery = makelistdomain('sender');

    var spamSendersQuery = makelist('sender');
    var spamSendersDomainsQuery = makelistdomain('sender');

    var rejectReasonsQuery = {};

    $.extend(true, rejectReasonsQuery, dt);
    rejectReasonsQuery['advcount'] = {'field': 'rejectreason'};

    var greylistFields = {'fields': [{
        'rejectreason': {
            'comparator': 're_i',
            'value': 'Recipient address rejected: Greylisted'
        }
    }]};

    var spamSendersFields = {'fields': [{
        'spamscore': {
            'comparator': '>=',
            'value': 5
        }
    }]};

    var excludeGreylistingQuery = {};

    $.extend(true, excludeGreylistingQuery, greylistFields);
    excludeGreylistingQuery['fields'][0]['rejectreason']['comparator'] = '!=';

    $.extend(true, greylistedQuery, greylistFields);
    $.extend(true, greylistedDomainsQuery, greylistFields);

    $.extend(true, sendersQuery, sendersAdditionalFields);
    $.extend(true, senderDomainsQuery, sendersAdditionalFields);

    $.extend(true, spamSendersQuery, spamSendersFields);
    $.extend(true, spamSendersDomainsQuery, spamSendersFields);

    get_data($('#list-top-senders'), $('#dashboard-overview-delivered'), 'Delivered', sendersQuery, 'sender', excludeGreylistingQuery);
    get_data($('#list-top-senders-domain'), null, null, senderDomainsQuery, 'sender', excludeGreylistingQuery);

    get_data($('#list-top-greylisted'), $('#dashboard-overview-greylisted'), 'Greylisted', greylistedQuery, 'sender', greylistFields);
    get_data($('#list-top-greylisted-domain'), null, null, greylistedDomainsQuery, 'sender', greylistFields);

    get_data($('#list-top-senders-spam'), $('#dashboard-overview-spam'), 'Spam', spamSendersQuery, 'sender', spamSendersFields);
    get_data($('#list-top-senders-spam-domain'), null, null, spamSendersDomainsQuery, 'sender', spamSendersFields);

    get_data($('#list-top-reject-resons'), null, null, rejectReasonsQuery, 'rejectreason', {});
};

DashboardView.get_stats = function () {
    DashboardView.get_overview(DashboardView.get_lists);
};

DashboardView.prototype = {
    setup: function () {
        $('#dashboard-nav-link').addClass('navbar-item-active');
        $('#dashboard-view').show();

        // this.interval = setInterval(DashboardView.get_stats, 10000);
        DashboardView.get_stats();
    },

    teardown: function () {
        if(this.interval !== null) {
            window.clearInterval(this.interval);
        }

        $('#dashboard-nav-link').removeClass('navbar-item-active');
        $('#dashboard-view').hide()
    }
};

var currentView = null;

//endregion

//region error messaging

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

//endregion

//region misc

/*
 * Misc
 */

// generate colors
var colors = chroma.scale(
    [
        'red',
        'blue',
        'yellow',
        'green',
        'magenta',
        'navy',
        'hotpink',
        '#2A4858',
        '#d3a96a',
        '#800080',
        '#63c56c'
    ]
).colors(15);

var precentageBarColors = [];
var pbctmp = chroma.scale(['green', 'red']).colors(100);
for(var i in pbctmp) {
    precentageBarColors.push(chroma(pbctmp[i]).luminance(0.4).hex());
}

var precentageBarFlow = chroma.scale(['#E1F5FE', '#03A9F4']).colors(100);;

function get_color(pos) {
    return chroma(
        colors[pos % (colors.length - 1)]
    )
        .luminance(0.6)
        .hex();
}

function sort_columns(columns) {
    visibleColumns.reverse();

    for (var vc in visibleColumns) {
        var i = columns.indexOf(visibleColumns[vc]);
        if (i > -1) {
            columns.splice(i, 1);
            columns.splice(0, 0, visibleColumns[vc])
        }
    }

    visibleColumns.reverse();
}

//endregion

//region ui loading spinners

/*
 * UI Loading
 */

function show_loading_spinner() {
    $('#search-loading').show();
}

function hide_loading_spinner() {
    $('#search-loading').hide();
}

function hide_on_search() {
    $(".hide-on-search").hide();
}

function show_on_finished_search() {
    $('.hide-on-search').show();
}

//endregion

//region setup functions

/*
 * Setup Functions
 */

function setup_selectizer(item) {
    var $select = item.selectize({
        create: true,
        onFocus: function () {
            if(!item.data('noclear')) {
                this.clear(true);
            }
        },
        onChange: function (selectedItem) {
            var element = this.$wrapper;
            var textselect = element.parent().parent().find('.search-text-selection');
            var optionselect = element.parent().parent().find('.search-field-selection');

            var fields = fieldsPerColumns[selectedItem];

            if(fields !== undefined) {
                if(fields.length <= maxFieldsPerColumns) {
                    textselect.hide();
                    optionselect.show();

                    optionselect.find('select').remove();
                    optionselect.find('.search-field-selection-select').remove();
                    optionselect.append('<select class="search-field-selection-select"></select>');

                    var select = optionselect.find('select');

                    for(var i in fields) {
                        select.append('<option value="' + fields[i] + '">'  + fields[i] +'</option>')
                    }

                    select.selectize({
                        create: true
                    });

                    return;
                }
            }

            textselect.show();
            optionselect.hide();
        }
    });

    var inst = $select[0].selectize;
    inst.trigger('change', inst.getValue());

    return inst;
}

function setup_datetimepicker(item) {
    item.datetimepicker({
        format : 'DD/MM/YYYY HH:mm'
    });
}

//endregion

//region creational destructional

/*
 * Creational/Destructional Functions
 */

function add_expression_line() {
    if(expressionLineTemplate === null) {
        return;
    }

    var newExp = expressionLineTemplate.clone();
    newExp.appendTo('#expression-container');

    newExp.find(".expression-comparator-button").click(on_comperator_button_click);
    newExp.find(".expression-comparator-button").trigger('click');

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


//endregion

//region ajax error handling

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

//endregion

//region table

function empty_table() {
    show_loading_spinner();
    hide_on_search();
    remove_all_messages();

    $('#results').find('.remove').remove();
    $(".pager").hide();

    var result_table = $("#result-table");

    result_table.trigger('destroyPager');
    result_table.trigger('destroy');
    // result_table.empty();
    result_table.find('thead').remove();
    result_table.find('tbody').remove();
    result_table.append('<thead style="display: none;"></thead><tbody></tbody>');
}

function append_rows(expression, columns, callback) {
    allColumns = columns;

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
                        '<td colspan="' + (columns.length + 1) + '">' +
                            '<div class="relative">' +
                            '<button class="hide-show-empty-fields-button btn btn-default" data-shown="0">Toggle Empty Fields</button>';

                var loglines = '';
                var childRowEnd = '</div></td>';
                var rowsMap = {};

                for (var i in columns) {
                    var rowData = '';
                    var extraClass = '';

                    if(data['rows'][r].hasOwnProperty(columns[i])) {
                        rowData = data['rows'][r][columns[i]];

                        if(columns[i] === 'spamscore') {
                            var spamscore = parseFloat(rowData);
                            if(!isNaN(spamscore) && spamscore >= 5) {
                                extraClass = 'redbackground';
                            }
                        }else if(columns[i] === 'virusresult') {
                            if(rowData.indexOf('INFECTED') !== -1) {
                                extraClass = 'redbackground';
                            }
                        }

                        if(rowData instanceof Array) {
                            if(columns[i] === 'loglines') {
                                rowData = rowData.join('');
                            }else{
                                var t = '';
                                for(var j in rowData) {
                                    t += '<div class="inline single-item">' + rowData[j] + '</div><span class="margin-right-1">,</span>';
                                }
                                rowData = t;
                            }
                        }else{
                            rowData = '<div class="inline single-item">' + rowData + '</div>';
                        }
                    }

                    var tmp = '';

                    if(columns[i] === 'loglines') {
                        rowData = rowData.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                        rowData = '<div class="loglines"><pre><code>' + rowData + '</code></pre></div>';
                    }

                    tmp =
                        '<div class="inline tab-row">' +
                            '<div class="inline tab-col-left">' + columns[i] + '</div>' +
                            '<div class="inline tab-col-right ' + extraClass + '">' + rowData + '</div>' +
                        '</div>';


                    if(columns[i] === 'loglines') {
                        loglines =
                        '<div class="inline tab-row">' +
                            '<div class="inline tab-col-right" style="width: 100%;">' + rowData + '</div>' +
                        '</div>';
                    }else{
                        childRow += tmp;
                    }

                    rowsMap[columns[i]] = rowData;
                }

                var isFirst = true;
                for(var j in columns) {
                    if(columns[j] === 'loglines') {
                        continue;
                    }

                    if(isFirst) {
                        visibleRow += rowsMap[columns[j]] + '</td>';
                        isFirst = false;
                    }else{

                        visibleRow += '<td class="tab-col-visible">' + rowsMap[columns[j]] + '</td>';
                    }
                }

                visibleRow += '<td class="tab-col-visible">' + rowsMap['loglines'] + '</td>';
                rows += visibleRow + '</tr>' + childRow  + loglines + childRowEnd + '</tr>';
            }

            var rows_i = $(rows);

            rows_i.on('click', '.single-item', function () {
                var parent = $(this).parent();

                if(parent.hasClass('tab-col-visible')) {
                    var childRow = parent.parent().next();

                    if(!childRow.find('td').first().is(":visible")) {
                        return;
                    }

                   var loglines = childRow.find('.loglines').find('code');
                }else if (parent.hasClass('tab-col-right')) {
                   var loglines = parent.parent().parent().find('.loglines').find('code');
                }else{
                   return;
                }

                var searchValue = $(this).html();

                if($(this).hasClass('hightlight_text')) {
                    loglines.find('span').each(function () {
                        if($(this).html() === searchValue) {
                            $(this).replaceWith($(this).html());
                        }
                    });
                    $(this).removeClass('hightlight_text');
                    $(this).css({ 'background-color' : ''});
                }else {
                    var loglinesHTML = loglines.html();
                    var indexes = [];

                    var currentIndex = 0;
                    while((match = loglinesHTML.indexOf(searchValue, currentIndex)) > -1) {
                        if(match === currentIndex) {
                            break;
                        }

                        indexes.push(match);
                        currentIndex = ++match;
                    }

                    var newHTML = '';
                    var lastPos = 0;
                    var currentColor = get_color(currentColorLength);

                    for (var i in indexes) {
                        var ind = indexes[i];
                        var piece = loglinesHTML.slice(lastPos, ind);

                        newHTML += piece + '<span class="hightlight_text" style="background-color: ' + currentColor + ';">' + searchValue + '</span>';

                        lastPos = ind + searchValue.length;
                    }

                    currentColorLength++;
                    newHTML += loglinesHTML.slice(lastPos);

                    $(this).addClass('hightlight_text');
                    $(this).css({ 'background-color': currentColor });
                    loglines.html(newHTML);
                }
            });

            rows_i.on('click', 'button.hide-show-empty-fields-button', function () {
                var show_empty = $(this).data('shown') == 1;
                $(this).siblings('.tab-row').each(function () {
                  var tab_col_right_content = $(this).find('.tab-col-right').html();
                   if(tab_col_right_content === '' && !show_empty) {
                      $(this).hide();
                   }else{
                      $(this).show();
                   }
                });

                if(show_empty) {
                    $(this).data('shown', '0');
                }else{
                    $(this).data('shown', '1');
                }
            });

            rows_i.find('button.hide-show-empty-fields-button').trigger('click');

            result_table_tbody.append(rows_i);
        }
        callback(columns);
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

        sort_columns(columns);

        for(var i in columns) {
            // validate received data
            if($.type(columns[i]) !== 'string') {
                empty_table();
                show_message(uiresponses.errors.receivedinvalid, uiresponses.none);
                hide_loading_spinner();
                return;
            }

            if(columns[i] === 'loglines') {
                continue;
            }

            // add headers

            extraClass = '';
            if($.inArray(columns[i], visibleColumns) === -1) {
                extraClass = 'columnSelector-false'
            }
            tr_head.append('<th class="' + extraClass + '">' + columns[i] + '</th>');
        }

        tr_head.append('<th class="columnSelector-false">loglines</th>');

        append_rows(expression, columns, callback);
    })
    .fail(handle_ajax_error);
}

function hide_child_rows() {
    $('.tablesorter-childRow td').hide();
    $("#pager").show();
    $("#result-table > thead").show();
}

function update_tags() {
    var tagsContainer = $("#tags-container");
    tagsContainer.empty();

    $.getJSON(api.tags, function (tags) {
        var btn_click = function () {
            var ia = $(this).data('isactive');
            if(ia == 0) {
                $(this).data('isactive', '1');
            }else{
                $(this).data('isactive', '0');
            }

            $(this).toggleClass('btn-primary');

            var tagsContainer = $("#tags-container");
            allbuttons = tagsContainer.find('.button-tag');
            query = '/(';
            var isEmpty = true;

            allbuttons.each(function () {
                if($(this).data('isactive') == 0) {
                    query += $(this).html() + '|';
                    isEmpty = false;
                }
            });

            if(!isEmpty) {
                query = query.slice(0, -1);
                query += ')/';
            }else{
                query = '';
            }

            var result_table = $('#result-table');

            var filters = $.tablesorter.getFilters(result_table, true);
            filters[allColumns.indexOf('tags') - 1] = query;

            result_table.trigger('search', [ filters ]);
        };

        for(i in tags) {
            var isActive = '0';
            var extraClass = 'btn-primary';

            if(tags[i] === 'incomplete') {
                isActive = '1';
                extraClass = '';
            }

            var btn= $('<button type="button" class="btn btn-default margin-right-1 button-tag ' + extraClass + '" data-isactive="' + isActive + '">' + tags[i] + '</button>');

            btn.click(btn_click);
            tagsContainer.append(btn)
        }

        // lets wait for time before filtering
        setTimeout(btn_click, 500);
    });
}

function initialize_table(columns) {
    var jTable = $('#result-table');

    jTable
        .tablesorter({
            theme : 'default',
            widthFixed: true,

            sortList: [[0, 0]],

            cssChildRow: 'tablesorter-childRow',

            widgets: [ 'zebra', 'filter', 'columnSelector' ],
            widgetOptions : {
                zebra : [ 'normal-row', 'alt-row' ],

                filter_placeholder: { search : 'Search...' },
                filter_childRows  : false,
                filter_cssFilter  : 'tablesorter-filter',
                filter_startsWith : false,
                filter_ignoreCase : true,

                columnSelector_container : $('#columnSelector'),
                columnSelector_columns : {
                    0: 'disable'
                },
                columnSelector_saveColumns: true,
                columnSelector_layout : '<label><input type="checkbox"><div class="inline">{name}</div></label>',
                columnSelector_layoutCustomizer : null,
                columnSelector_name  : 'data-selector-name',
                columnSelector_mediaquery: false,
                columnSelector_breakpoints : [ '20em', '30em', '40em', '50em', '60em', '70em' ],
                columnSelector_priority : 'data-priority',
                columnSelector_cssChecked : 'checked'
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

    jTable.trigger('pageSet', 0);

    $('#popover')
        .popover({
            placement: 'right',
            html: true,
            content: $('#popover-target')
        });

    var columnsSelector = $("#columnSelector");
    var elements = columnsSelector.find('label').detach();

    var labelMap = {};

    elements.each(function () {
        var d = $(this).find('div');
        labelMap[d.html()] = $(this);
    });

    sort_columns(columns);
    for(var i in columns) {
        columnsSelector.append(labelMap[columns[i]]);
    }

    hide_child_rows();
    $(".columnSelectorWrapper").show();
    show_on_finished_search();
    update_tags();
    hide_loading_spinner();
}

//endregion

//region event handlers

/*
 * Event Handlers
 */

/* expression builder */

function has_empty_expression_fields() {
    var hasEmptyFields = false;

    $.each(expressionLines, function () {
        var expInput = $(this[0]).find('.expression-input');
        var optionselect = $(this[0]).find('.search-field-selection');

        if(optionselect.is(':visible')) {
            if(optionselect.find('.search-field-selection-select')[0].selectize.getValue() === '') {
                hasEmptyFields = true
            }
        }else{
            if(!expInput.val()) {
                hasEmptyFields = true;
            }
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
    var parent = null;

    try {
        parent = item.parent().parent();
    }catch(e) {
        parent = $(this).parent().parent();
    }

    parent.find('.dt-add').hide();
    parent.find('.dt-search-mask').show();

}

function on_remove_dt_button_click(item) {
    var parent = null;

    try {
        parent = item.parent().parent().parent();
    }catch(e) {
        parent = $(this).parent().parent().parent();
    }

    parent.find('.dt-search-mask').hide();
    parent.find('.dt-add').show();
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
        fields: [],
        datetime: {
            start: '',
            end: ''
        }
    };

    $.each(expressionLines, function () {
        var jq = this[0];
        var s = this[1];

        var key = s.getValue();

        var optionselect = jq.find('.search-field-selection');

        var value = jq.find('.expression-input').val();

        if(optionselect.is(':visible')) {
            value = optionselect.find('.search-field-selection-select')[0].selectize.getValue();
        }

        var h = {};
        h[key] = {
            "comparator": comparatorMap[jq.find(".expression-comparator-button").html()],
            "value": value
        };


        expression.fields.push(h);
    });

    expression.datetime.start = getFromDT();
    expression.datetime.end = getToDT();

    reset_table(expression, initialize_table);
}

function on_comperator_button_click() {
    var cycle = [];
    for(i in comparatorMap) {
        cycle.push(i);
    }

    var currCycle = $(this).html();
    var currCursor = 0;
    for(var i in cycle) {
        if(currCycle === cycle[i]) {
            currCursor = ++i;
            break;
        }
    }

    if(currCursor >= cycle.length) {
        currCursor = 0;
    }

    $(this).html(cycle[currCursor]);
}

/*
 * dashboard overview
 */

function get_overview_hours() {
    var val = parseInt($("#overview-hours").val());
    if(isNaN(val)) {
        return overviewHoursDefault;
    }else{
        return val;
    }
}

function on_overview_hours_focus() {
    lastOverviewHours = get_overview_hours();
}

function on_overview_hours_focus_loss() {
    overviewHours = parseInt($("#overview-hours").val());
    if(isNaN(overviewHours)) {
        overviewHours = lastOverviewHours;
    }
    
    $("#overview-hours").val(overviewHours);
    DashboardView.get_stats();
}

//endregion

//region view

/*
 * View
 */

function change_view(view) {
    if(currentView !== null) {
        currentView.teardown();
    }
    currentView = view;
    currentView.setup();
}

//endregion

//region initialization

/*
 * Init
 */

function init_global_variables() {
    expressionLineTemplate = $('#expression-templates > .expression-line');
}

function init_expression_template() {
    $.getJSON(api.columns, function (columns) {

        var removeFields = ['phdmxin_time', 'phdimap_time'];
        for(var i in removeFields) {
            columns.splice(columns.indexOf(removeFields[i]), 1);
        }

        sort_columns(columns);

        excludedColumns = [
            'phdmxin_qid',
            'phdimap_qid',
            'messageid',
            'phdmxin_time',
            'phdimap_time',
            'sender',
            'recipient',
            'connectclient',
            'connectip',
            'deliveryrelay',
            'spamscantime',
            'spamscore',
            'spamdesc',
            'username',
            'uid',
            'size',
            'saslusername'
        ];

        for(var i in columns) {
            (function () {
                const localColumn = columns[i];
                if(localColumn === 'loglines') {
                    return;
                }

                if(excludedColumns.indexOf(localColumn) === -1) {
                    $.ajax({
                        url: api.fieldchoices.replace('%s', localColumn)
                            .replace('%d', maxFieldsPerColumns + 1),
                        type: methods.get,
                        dataType: 'json'
                    }).done(function (result) {
                        fieldsPerColumns[localColumn] = result;
                    });
                }
            })();

            $('.expression-select').append('<option value="' + columns[i] + '">'  + columns[i] +'</option>')
        }

        add_expression_line();
    });
}

function init_overview_dashboard() {
    $('#overview-hours').val('24');
}

function deactivate_all_nav_elements() {
    $('.navbar-item').removeClass('navbar-item-active');
}

function register_event_handlers() {
    /* nav */
    $('#dashboard-nav-link').click(function () {
        deactivate_all_nav_elements();
        change_view(new DashboardView());
    });

    $('#search-nav-link').click(function () {
        deactivate_all_nav_elements();
        change_view(new SearchView());
    });

    /* expression builder */
    $('#add-expression-line-button').click(on_add_expression_line_button_click);

    /* datetime */
    $('.add-dt-button').click(on_add_dt_button_click);
    $('.remove-dt-button').click(on_remove_dt_button_click);

    /* API */
    $('#search-button').click(on_search_button_click);
    $(document).keypress(function (event) {
       if(event.which == 13) {
           on_search_button_click();
       }
    });

    /* Table */
    var jTable = $('#result-table');

    jTable.on('pagerComplete', function (e, d) {
        hide_child_rows();
        return false;
    });

    jTable.on('click', '.toggle', function(e, d) {
        $(this).closest('tr').nextUntil('tr:not(.tablesorter-childRow)').find('td').toggle();
        return false;
    });

    /* dashboard */

    $("#overview-hours").on('focusout', on_overview_hours_focus_loss);
    $("#overview-hours").on('focusin', on_overview_hours_focus);
}

//endregion

function main() {
    init_global_variables();
    register_event_handlers();
    init_expression_template();
    init_overview_dashboard();
    setup_datetimepicker($('#dt-from-picker'));
    setup_datetimepicker($('#dt-to-picker'));
    setup_selectizer($(".pagesize"));
    change_view(new DashboardView());
}

$(document).ready(main);
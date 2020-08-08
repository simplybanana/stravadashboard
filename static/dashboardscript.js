var dynamicTable = (function() {
    
    var _tableId, _table, 
        _fields, _headers, 
        _defaultText, _avg;
    
    /** Builds the row with columns from the specified names. 
     *  If the item parameter is specified, the memebers of the names array will be used as property names of the item; otherwise they will be directly parsed as text.
     */
    function _buildRowColumns(names,header,units) {
        var row = '';
        var background_color = '';
        if(units==' Ft'){
            background_color= "#33FF58";
           }
        else if(units==' Min'){
            background_color= "#33B2FF";
        }
        else{
            background_color= "#FF6347";
        };
        if(header){
            row += '<tr>';
            $.each(names, function(index, name) {
                var c = name;
                row += '<td>' + c + '</td>';
            });
            row += '</tr>';
        }
        else{
            for (var k in names){
                row += '<tr>';
                row += '<td>' + k + '</td>';
                for (var i in names[k]){
                    var x = names[k][i]
                    var di = x/_avg
                    var chec = di.toString()
                    if(x==0){
                       row += '<td></td>'
                       }
                    else if (di * 100 < 50){
                        row += '<td><span class="circle" style="--width:' + chec + 'px;--height:' + chec + 'px;--line-height:.5px;--background-color:'+ background_color +'"><div class="text">'+ x +units + '</div></span></td>'
                    }
                    else if(di * 100 > 300){
                        row += '<td><span class="circle" style="--width:' + chec + 'px;--height:' + chec + 'px;--line-height:3px;--background-color:'+ background_color+'"><div class="text">'+ x +units + '</div></span></td>'
                            }
                    else{
                        row += '<td><span class="circle" style="--width:' + chec + 'px;--height:' + chec + 'px;--line-height:' + chec + 'px;--background-color:'+background_color+'"><div class="text">'+  x +units + '</div></span></td>'
                    }
                }
                row += '</tr>';
            }
        }
        return row;
    }
    
    /** Builds and sets the headers of the table. */
    function _setHeaders() {
        // if no headers specified, we will use the fields as headers.
        _headers = (_headers == null || _headers.length < 1) ? _fields : _headers; 
        var h = _buildRowColumns(_headers,true);
        if (_table.children('thead').length < 1) _table.prepend('<thead></thead>');
        _table.children('thead').html(h);
    }
    
    function _setNoItemsInfo() {
        if (_table.length < 1) return; //not configured.
        var colspan = _headers != null && _headers.length > 0 ? 
            'colspan="' + _headers.length + '"' : '';
        var content = '<tr class="no-items"><td ' + colspan + ' style="text-align:center">' + 
            _defaultText + '</td></tr>';
        if (_table.children('tbody').length > 0)
            _table.children('tbody').html(content);
        else _table.append('<tbody>' + content + '</tbody>');
    }
    
    function _removeNoItemsInfo() {
        var c = _table.children('tbody').children('tr');
        if (c.length == 1 && c.hasClass('no-items')) _table.children('tbody').empty();
    }
    
    return {
        /** Configres the dynamic table. */
        config: function(tableId, fields, headers, defaultText,avg) {
            _tableId = tableId;
            _table = $('#' + tableId);
            _fields = fields || null;
            _headers = headers || null;
            _defaultText = defaultText || 'No items to list...';
            _setHeaders();
            _setNoItemsInfo();
            _avg = avg || 1000;
            return this;
        },
        /** Loads the specified data to the table body. */
        load: function(data, append,units) {
            if (_table.length < 1) return; //not configured.
            _setHeaders();
            _removeNoItemsInfo();
            var rows = '';
            //rows += '<tr><td>' + $.type(data) + '</tr></td>';
            rows += _buildRowColumns(data,false,units);
            /*
            $.each(data, function(index, item) {
                rows += _buildRowColumns(item,false);
            });*/
            var mthd = append ? 'append' : 'html';
            _table.children('tbody')[mthd](rows);
            return this;
        },
        /** Clears the table body. */
        clear: function() {
            _setNoItemsInfo();
            return this;
        }
    };
}());


$(document).ready(function(e) {
    var av = $("table").attr("avg")
    var dt = dynamicTable.config('data-table', 
                                 ['field2', 'field1', 'field3'], 
                                 ['Week Of', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'], //set to null for field names instead of custom header names
                                 'No Activities yet',av);
    var a =  JSON.parse($("table").attr("rows"));
    dt.load(a,false,"mi");
    $('#distance').click(function(e) {
        var avD = $("table").attr("avg");
        var ad =  JSON.parse($("table").attr("rows"));
        var dt = dynamicTable.config('data-table', 
                                 ['field2', 'field1', 'field3'], 
                                 ['Week Of', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'], //set to null for field names instead of custom header names
                                 'No Activities yet',avD);
        dt.load(ad,false," mi");
    });
    
    $('#elevation').click(function(e) {
        var avE = $("table").attr("avgE");
        var aE =  JSON.parse($("table").attr("el"));
        var dt = dynamicTable.config('data-table', 
                                 ['field2', 'field1', 'field3'], 
                                 ['Week Of', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'], //set to null for field names instead of custom header names
                                 'No Activities yet',avE);
        dt.load(aE,false," Ft");
    });
    
    $('#time').click(function(e) {
        var avT = $("table").attr("avgT");
        var aT =  JSON.parse($("table").attr("ti"));
        var dt = dynamicTable.config('data-table', 
                                 ['field2', 'field1', 'field3'], 
                                 ['Week Of', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun'], //set to null for field names instead of custom header names
                                 'No Activities yet',avT);
        dt.load(aT,false," Min");
    });
});
$(document).ready(function() {
    loadTimeLine();
    bindDatepicker();
});

function loadTimeLine() {
    document.getElementById("loading-text").innerHTML="Fetching repository information...";
    var groupsData, itemsData, optionsData, ratingData;
    var repoid = document.getElementById("repoid").getAttribute('src');
    hideElements();
    $.when(
        $.getJSON('/api/rating/'+repoid, function (data) {
            ratingData = data;
            document.getElementById("loading-text").innerHTML=" Building Pull Requests Rating...";
            buildingRating(data)
        }),
        $.getJSON('/api/items/'+repoid, function (data) {
            itemsData = data;
            document.getElementById("loading-text").innerHTML=" Fetch timeline data...";

        }),
        $.getJSON('/api/groups/'+repoid, function (data) {
            groupsData = data;
            document.getElementById("loading-text").innerHTML=" Fetch timeline options...";

        }),
        $.getJSON('/api/options/'+repoid, function (data) {
            optionsData = data;
            document.getElementById("loading-text").innerHTML=" Compiling timeline & rating. " +
                "This may take a couple of minutes while we slice & dice the data....";
        })
    ).then(function () {
        if(groupsData.hasOwnProperty('message')
                || itemsData.hasOwnProperty('message')
                || optionsData.hasOwnProperty('message')
                || ratingData.hasOwnProperty('message')){
            console.log('yes');
        }
        else{
            getRangesFromItems(itemsData);
            //console.log('yes1');
            showElements();
            //console.log('yes2');
            //console.log('no errors!');
            var container = document.getElementById('visualization');
            var myNode = document.getElementById("visualization");
                while (myNode.firstChild) {
                    myNode.removeChild(myNode.firstChild);
                }
            //console.log('yes3');
            // Create a DataSet (allows two way data-binding)
            var items = new vis.DataSet(itemsData);
            var groups = new vis.DataSet(groupsData);
            // Create a Timeline
            var timeline = new vis.Timeline(container);
            timeline.setOptions(optionsData);
            timeline.setItems(items);
            timeline.setGroups(groups);

            timeline.on('select', function (properties) {
              logEvent(properties);
            });
            function logEvent(properties) {
                var ss = items.get(properties.items);
                if (typeof ss[0] !== 'undefined') {
                    $("#prinfo tbody tr").remove();
                    insertRow('Title', ss[0].content);
                    insertRow('Author', ss[0].group);
                    insertRow('Created at', ss[0].start);
                    if (ss[0].className == 'grey') {
                        insertRow('Status', 'closed');
                        insertRow('Closed at', ss[0].end);
                    }
                    else
                        insertRow('Status', 'open');
                    insertRow('Rework', ss[0].rework);
                    insertRow('Report', ss[0].report);
                    //document.getElementById('prhint').style.display = 'table';
                }
                else {
                    //document.getElementById('prhint').style.display = 'none';
                }
            }
        }
    })
}

function getRangesFromItems(data){
    var items = new vis.DataSet(data);
    var rangeInd = items.get({
        filter: function (item) {
            var a = (item.isback == '0');
            //console.log(a);
            return a;
        }      
    });
    //console.log(rangeInd)
    if (rangeInd.length != 0){
        var myNode = document.getElementById("dateDiv");
        if (myNode == null){
        if (myNode == null){
            console.log("myNode prarmeter is null:", myNode);
            return;
        }
        var delnode = myNode.getElementsByClassName('datedivlol');
        //console.log(myNode);
        //console.log(delnode[0]);
        if (delnode == null){
            console.log("delnode parameter is null: ",delnode);
            return;
        }
        while(delnode[0]){
            myNode.removeChild(delnode[0]);
        }
        rangeInd.forEach(function (item, i, array) {
            var time_start = moment(item.start).format('DD-MM-YYYY');
            var time_end = moment(item.end).format('DD-MM-YYYY');
            var phrase = item.content;
            addNewDatarange(time_start, time_end, phrase);
        })
    }
}

function insertRow(text1, text2) {
    var tableRef = document.getElementById('prinfo').getElementsByTagName('tbody')[0];
    var newRow   = tableRef.insertRow(tableRef.rows.length);
    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    cell1.innerHTML = text1;
    cell2.innerHTML = text2;
}

function bindDatepicker() {
    $('.input-daterange input.tt').each(function() {
        $(this).datepicker({
            dateFormat: 'dd-mm-yy'
        });
    });
}

function addNewDatarange(time1, time2, phrase) {
    dateR(time1,time2, phrase);
    bindDatepicker();
}

function removeDaterange(element) {
    dateR(' ', ' ', ' ',element);
}

var dateR =(function(time1, time2, phrase, del) {
    var counter = 0;
    function addNew(time1, time2, phrase, del) {
        //если идет параметр на удаление, удаляем
        if(del != undefined){
            removeOne(del);
        }
        else{
            if (phrase == undefined)
                phrase = '';
            if (time1 == undefined)
                time1 = '';
            if (time2 == undefined)
                time2 = '';
            counter += 1;
            $("#dateDiv").find('div.list-group-item:last').after(function () {
                return '<div id="date'+counter+'div" class="list-group-item noline top10 datedivlol">'+
                                '<div class="form-group">'+
                                    '<div class="input-group multi-control-group input-daterange">'+
                                        '<input type="text" class="form-control" value="'+phrase+'" placeholder="Matching phrase...">'+
                                        '<span class="input-group-addon"> | </span>'+
                                        '<input type="text" class="form-control tt" data-date-format="dd-mm-yyyy" value="'+time1+'" placeholder="date">' +
                                        '<span class="input-group-addon">to</span>'+
                                        '<input type="text" class="form-control tt" data-date-format="dd-mm-yyyy" value="'+time2+'" placeholder="date">'+
                                        '<span class="input-group-btn">' +
                                            '<button id="date'+counter+'" class="btn btn-blockz" onclick="removeDaterange(this);">'+
                                                '<span class="glyphicon glyphicon-remove"></span>'+
                                            '</button>'+
                                        '</span>'+
                                    '</div>'+
                                '</div>'+
                            '</div>';
            });
        }
    }
    function removeOne(element) {
        counter-=1;
        var myid = element.id;
        var selector = '#'+ myid +'div';
        $("div").remove(selector);
    }
    return function (time1, time2, phrase ,del) {
        return addNew(time1, time2, phrase, del)
    }
})();


function readDataranges(){
    var deadline = false;
    var dataranges = {
        a: []
    };
    var repoid = document.getElementById("repoid").getAttribute('src');
    var ul = document.getElementById("dateDiv");
    var items = ul.getElementsByClassName("list-group-item");
    var nodates = true;
    for (var i = 1; i < items.length; ++i) {
        var item = items[i];
        var inputs = item.getElementsByTagName("input");
        //console.log(inputs);
        //console.log((item));
        if(inputs.length != 0 && inputs[1].value != '' && inputs[2].value != '') {
            dataranges.a.push({
                'id': item.id,
                'phrase': inputs[0].value,
                'start': inputs[1].value,
                'end': inputs[2].value
            });
            nodates = false;
        }
        // do something with items[i], which is a <li> element
    }
    if(nodates){
       console.log("no data in datarange!");
       return;
    }
    console.log(JSON.stringify(dataranges.a));
    $.post('/api/items/'+repoid, {'data': JSON.stringify(dataranges.a), 'repoid': repoid}, function() {
        console.log('update timeline');
        loadTimeLine()
    });
}

function buildingRating(data) {
    var tableRef = document.getElementById('rating-table').getElementsByTagName('tbody')[0];
    var keysarr = Object.keys(data);
    //console.log(keysarr);
    //console.log(data[keysarr[0]]);
    while(tableRef.rows[0])
        tableRef.removeChild(tableRef.rows[0]);
    keysarr.forEach(function (item, i, arr) {
        var newRow   = tableRef.insertRow(tableRef.rows.length);
        for(var k in data[arr[i]]){
           newRow.insertCell(newRow.length);
        }
        var ind = i+1;
        newRow.cells[0].innerHTML = "<b>"+ind+"</b>";
        newRow.cells[1].innerHTML = data[item]['login'];
        newRow.cells[2].innerHTML = data[item]['full_name'];
        newRow.cells[3].innerHTML = '<a href="'+data[item]['url']+'"style:="cursor: pointer;">'+data[item]['url']+'<a/>';
        newRow.cells[4].innerHTML = data[item]['opened'];
        newRow.cells[5].innerHTML = data[item]['intime'];
        newRow.cells[6].innerHTML = data[item]['delay'];
        newRow.cells[7].innerHTML = data[item]['closed'];
        newRow.cells[8].innerHTML = data[item]['rework'];
    });
}

function hideElements() {
    document.getElementById("loading-wrapper").style.display = 'block';
    document.getElementById("timeline-wrapper").style.display = 'none';
    document.getElementById("table-wrapper").style.display = 'none';
}


function showElements() {
    document.getElementById("loading-wrapper").style.display = 'none';
    document.getElementById("timeline-wrapper").style.display = 'block';
    document.getElementById("table-wrapper").style.display = 'block';
}
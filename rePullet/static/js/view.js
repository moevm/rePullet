$(document).ready(function() {
    loadTimeLine();
});

function loadTimeLine() {
    document.getElementById("loading-text").innerHTML="Fetching repository information...";
    var groupsData, itemsData, optionsData;
    var repoid = document.getElementById("repoid").getAttribute('src');
    document.getElementById("loading-text").innerHTML=" Fetching pull requests data...";
    $.when(
        $.getJSON('/api/items/'+repoid, function (data) {
            itemsData = data;
            document.getElementById("loading-text").innerHTML=" Fetch timeline options...";

        }),
        $.getJSON('/api/groups/'+repoid, function (data) {
            groupsData = data;
            document.getElementById("loading-text").innerHTML=" Fetch timeline options...";

        }),
        $.getJSON('/api/options/'+repoid, function (data) {
            optionsData = data;
            document.getElementById("loading-text").innerHTML=" Compiling timeline. " +
                "This may take a couple of minutes while we slice & dice the data....";
        })
    ).then(function () {
        if(groupsData.hasOwnProperty('message')
                || itemsData.hasOwnProperty('message'
                || optionsData.hasOwnProperty('message'))){
            console.log('yes');
        }
        else{
            console.log('no');
            var container = document.getElementById('visualization');
            // Create a DataSet (allows two way data-binding)
            var items = new vis.DataSet(itemsData);
            var groups = new vis.DataSet(groupsData);
            // Create a Timeline
            var timeline = new vis.Timeline(container);
            timeline.setOptions(optionsData);
            timeline.setItems(items);
            timeline.setGroups(groups);

            document.getElementById("loading-wrapper").style.display = 'none';
            document.getElementById("content-wrapper").style.display = 'block';

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
                    document.getElementById('prhint').style.display = 'table';
                }
                else {
                    document.getElementById('prhint').style.display = 'none';
                }
            }
        }
    })
}

function insertRow(text1, text2) {
    var tableRef = document.getElementById('prinfo').getElementsByTagName('tbody')[0];
    var newRow   = tableRef.insertRow(tableRef.rows.length);
    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    cell1.innerHTML = text1;
    cell2.innerHTML = text2;
}
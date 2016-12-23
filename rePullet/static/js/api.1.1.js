$(document).ready(function() {
    getTimeline();
});

function getLocationPathname(href) {
    var l = document.createElement("a");
    l.href = href;
    return l.pathname
}

function getOptionsString() {
    optionsString = "?";
    var obj = {}
    var cl_user = document.getElementById("cl-user").value;
    if(cl_user != ""){
        obj['cl'] = cl_user;
    }
    optionsString += jQuery.param(obj);
    document.getElementById("testjs").src = (optionsString.localeCompare("?") ? optionsString : "");
    return x = (optionsString.localeCompare("?") ? optionsString : "");
}

function getTimeline() {
    document.getElementById("preview-text").innerHTML="Fetching repository information...";
    var groupsData, itemsData, optionsData;
    var url = document.getElementById("urlrepo").getAttribute('src');
    if(!url){
        document.getElementById("preview-text").innerHTML="NO DATA";
        return
    }
    document.getElementById("preview-text").innerHTML=" Fetching pull requests data...";
    var optString = getOptionsString();
    //document.getElementById("repo").value = 'api/groups' + getLocationPathname(url);
    $.when(
        $.getJSON('/api/groups'+getLocationPathname(url)+optString, function (data) {
            groupsData = data;
            document.getElementById("preview-text").innerHTML=" Fetch timeline options...";

        }),
        $.getJSON('/api/options'+getLocationPathname(url)+optString, function (data) {
            optionsData = data;
            document.getElementById("preview-text").innerHTML=" Compiling timeline. " +
                "This may take a couple of minutes while we slice & dice the data....";
        }),
        $.getJSON('/api/items'+getLocationPathname(url)+optString, function (data) {
            itemsData = data;
        })
    ).then(function () {
        if(groupsData && itemsData && optionsData){
            // DOM element where the Timeline will be attached
            var container = document.getElementById('visualization');
            // Create a DataSet (allows two way data-binding)
            var items = new vis.DataSet(itemsData);
            var groups = new vis.DataSet(groupsData);
            // Create a Timeline
            var timeline = new vis.Timeline(container);
            timeline.setOptions(optionsData);
            timeline.setItems(items);
            timeline.setGroups(groups);
            document.getElementById("main-content").style.display = 'block';
            document.getElementById("vis-content").style.display = 'block';
            document.getElementById("preview-container").style.display = 'none';
            document.getElementById("preview-text").style.display = 'none';
            document.getElementById("preview-loading").style.display = 'none';
            timeline.on('select', function (properties) {
              logEvent(properties);
            });
            function logEvent(properties) {
              var ss = items.get(properties.items);
              if (typeof ss[0] !== 'undefined') {
                  $("#prhint tbody tr").remove();
                  insertRow('Title', ss[0].content);
                  insertRow('Author', ss[0].group);
                  insertRow('Created at', ss[0].start);
                  if(ss[0].className == 'grey'){
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
        else{
            document.getElementById("preview-text").innerHTML="NO DATA";
        }
    })
}

function insertRow(text1, text2) {
    var tableRef = document.getElementById('prhint').getElementsByTagName('tbody')[0];
    var newRow   = tableRef.insertRow(tableRef.rows.length);
    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    cell1.innerHTML = text1;
    cell2.innerHTML = text2;
}


$('.input-daterange input').each(function() {
    $(this).datepicker("clearDates");
});
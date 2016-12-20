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
        }
        else{
            document.getElementById("preview-text").innerHTML="NO DATA";
        }
    })
}


$('.input-daterange input').each(function() {
    $(this).datepicker("clearDates");
});
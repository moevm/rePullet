$(document).ready(function() {
    var groupsData, itemsData;
    var url = document.getElementById("url").getAttribute('src')
    document.getElementById('loading').style.display = 'block';
    if(!url){
        return
    }
    //document.getElementById("repo").value = 'api/groups' + getLocationPathname(url);
    $.when(
        $.getJSON('/api/groups'+getLocationPathname(url), function (data) {
            groupsData = data;
        }),
        $.getJSON('/api/items'+getLocationPathname(url), function (data) {
            itemsData = data
        })
    ).then(function () {
        if(groupsData && itemsData){
            // DOM element where the Timeline will be attached
            var container = document.getElementById('visualization');
            // Create a DataSet (allows two way data-binding)
            var items = new vis.DataSet(itemsData);
            var groups = new vis.DataSet(groupsData)
            // Configuration for the Timeline
            var options = {};
            // Create a Timeline
            var timeline = new vis.Timeline(container);
            timeline.setOptions(options);
            timeline.setItems(items);
            timeline.setGroups(groups);
        }
        else{
        }
    })
});

function getLocationPathname(href) {
    var l = document.createElement("a");
    l.href = href
    return l.pathname
}
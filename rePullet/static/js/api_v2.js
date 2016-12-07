$(document).ready(function() {
    document.getElementById("preview-text").innerHTML="Fetching repository information...";
    var groupsData, itemsData;
    var url = document.getElementById("urlrepo").getAttribute('src');
    if(!url){
        document.getElementById("preview-text").innerHTML="NO DATA";
        return
    }
    document.getElementById("preview-text").innerHTML="Fetching pull requests data...";
    //document.getElementById("repo").value = 'api/groups' + getLocationPathname(url);
    $.when(
        $.getJSON('/api/groups'+getLocationPathname(url), function (data) {
            groupsData = data;
            document.getElementById("preview-text").innerHTML="Compiling timeline. " +
                "This may take a couple of minutes while we slice & dice the data....";
        }),
        $.getJSON('/api/items'+getLocationPathname(url), function (data) {
            itemsData = data;
        })
    ).then(function () {
        if(groupsData && itemsData){
            // DOM element where the Timeline will be attached
            var container = document.getElementById('visualization');
            // Create a DataSet (allows two way data-binding)
            var items = new vis.DataSet(itemsData);
            var groups = new vis.DataSet(groupsData);
            // Configuration for the Timeline
            var options = {
                width: '100%',
                maxHeight: '500px'
            };
            // Create a Timeline
            var timeline = new vis.Timeline(container);
            timeline.setOptions(options);
            timeline.setItems(items);
            timeline.setGroups(groups);
            document.getElementById("preview-text").style.display = 'none'
            document.getElementById("preview-loading").style.display = 'none'
        }
        else{
            document.getElementById("preview-text").innerHTML="NO DATA";
        }
    })
});

function getLocationPathname(href) {
    var l = document.createElement("a");
    l.href = href;
    return l.pathname
}
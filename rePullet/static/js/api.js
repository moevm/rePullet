$(document).ready(function() {
    $("#asub1").click(function () {
        var groupsData, itemsData;
        var url = document.getElementById("repo").value
        if(!url){
            document.getElementById("repo").value = "fail"
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
                document.getElementById('loading').style.display = 'none';
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
                document.getElementById("repo").value = "fail2"
            }
        })
    })
});

function getLocationPathname(href) {
    var l = document.createElement("a");
    l.href = href
    return l.pathname
}
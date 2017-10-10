$(document).ready(function() {
    getTimeline();
    bindDatepicker();
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
    // if(!url){
    //     console.log('no data!');
    //     return
    // }
    document.getElementById("preview-text").innerHTML="Fetching repository information...";
    hideControlElements();
    var groupsData, itemsData, optionsData;
    var a = readDataranges();
    var optString = getOptionsString();
    var url = document.getElementById("urlrepo").getAttribute('src');
    document.getElementById("preview-text").innerHTML=" Fetching pull requests data...";
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
        $.ajax({
          url:'api/items'+getLocationPathname(url)+optString,
          type:"POST",
          data: a,
          contentType:"application/json; charset=utf-8",
          dataType:"json",
          success: function(data){
            itemsData = data;
          }
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

            showControlElements();

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
    })
}


//
// datetime range
//
var dateR =(function(time1, time2, del) {
    var counter = 0;
    function addNew(time1, time2, del) {
        //если идет параметр на удаление, удаляем
        if(del != undefined){
            removeOne(del);
        }
        else{
            counter += 1;
            $("#dateUl").find('li:last').after(function () {
                return '<li id="date'+counter+'li"><div class="div-gr"><div class="input-group input-daterange">' +
                    '<input type="text" data-date-format="dd-mm-yyyy" class="form-control" value="'+time1+'">' +
                    '<span class="input-group-addon">to</span>' +
                    '<input type="text" data-date-format="dd-mm-yyyy" class="form-control" value="'+time2+'">' +
                    '<span class="input-group-btn"><button id="date'+counter+'" class="btn btn-block" onclick="removeDaterange(this);">' +
                    '<span class="glyphicon glyphicon-remove"></span></button></span></div></div></li>';
            });
        }
    }
    function removeOne(element) {
        counter-=1;
        var myid = element.id;
        var selector = '#'+ myid +'li';
        $("li").remove(selector);
    }
    return function (time1, time2, del) {
        return addNew(time1, time2, del)
    }
})();


function addNewDatarange(time1, time2) {
    dateR(time1,time2);
    bindDatepicker();
}

function removeDaterange(element) {
    dateR(' ', ' ', element);
}

function bindDatepicker() {
    $('.input-daterange input').each(function() {
        $(this).datepicker({
            dateFormat: 'dd-mm-yy'
        });
    });
}

//
// Timeline actions
//

function updateTimeline() {

}

function sendDataranges(){
    getTimeline();
}

function readDataranges(){
    var dataranges = {
        a: []
    };

    var ul = document.getElementById("dateUl");
    var items = ul.getElementsByTagName("li");
    for (var i = 1; i < items.length; ++i) {
        var item = items[i];
        var inputs = item.getElementsByTagName("input");
        if(inputs[0].value != '' && inputs[1].value != '') {
            dataranges.a.push({
                'id': item.id,
                'start': inputs[0].value,
                'end': inputs[1].value
            });
        }
        // do something with items[i], which is a <li> element
    }
    console.log(JSON.stringify(dataranges.a));
    return JSON.stringify(dataranges.a);
}

function insertRow(text1, text2) {
    var tableRef = document.getElementById('prhint').getElementsByTagName('tbody')[0];
    var newRow   = tableRef.insertRow(tableRef.rows.length);
    var cell1 = newRow.insertCell(0);
    var cell2 = newRow.insertCell(1);
    cell1.innerHTML = text1;
    cell2.innerHTML = text2;
}


//
// visible actions
//

function hideControlElements(){
    document.getElementById('sideControl').style.display = 'none';
    if (window.matchMedia("(min-width: 768px)").matches) {
      document.getElementById('page-wrapper').style.marginLeft = '0px';
    }
}

function showControlElements() {
    if (window.matchMedia("(min-width: 768px)").matches) {
      document.getElementById('page-wrapper').style.marginLeft = '300px';
    }
    document.getElementById('sideControl').style.display = 'block';
    document.getElementById("main-content").style.display = 'block';
    document.getElementById("vis-content").style.display = 'block';
    document.getElementById("preview-container").style.display = 'none';
    document.getElementById("preview-text").style.display = 'none';
    document.getElementById("preview-loading").style.display = 'none';
}
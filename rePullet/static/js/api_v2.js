$(document).ready(function($) {
    getUserRepos();
});

function getUserRepos() {
    var reposData;
    $.when(
        $.getJSON('/api/user/repos', function (data) {
            reposData = data;
        })
    ).then(function () {
        console.log(reposData);
        for (var k = 0; k < reposData.length; k++){
            console.log(reposData[k]['id']);
            (function(e) {
                $("#repoTBody").find('tr:last').after(function () {
                    return '<tr>' +
                        '<td><input style="margin: 0 auto;" type="checkbox" name="check" class="checkbox" value="'+reposData[e]['id']+'"></td>' +
                        //'<td class="hidden-xs"><i class="fa fa-star icon-state-warning"></i></td>' +
                        // '<td class="hidden-xs">id</td>' +
                        '<td class="clickable" data-repo="'+reposData[e]['fullname']+'">'+reposData[e]['fullname']+'</td>' +
                        '<td class="clickable" data-repo="'+reposData[e]['fullname']+'">'+reposData[e]['name']+'</td>' +
                        '<td class="clickable" data-repo="'+reposData[e]['fullname']+'">'+reposData[e]['owner']+'</td>' +
                        // '<td></td>' +
                        // '<td>'+reposData[e]['fullname']+'</td>' +
                        '</tr>';
                });
            })(k);
        }
        $(".clickable").click(function() {
            window.location.assign('/view/'+$(this).data("repo"));
            //post('/view', {'r': $(this).data("repo")}, 'get')
        });
    })
}



//
// post
//
function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
         }
    }

    document.body.appendChild(form);
    form.submit();
}
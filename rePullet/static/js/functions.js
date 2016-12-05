$(document).ready(function() {
    $("#mainForm").submit(function(event) {
        event.preventDefault(); // <-- add this
        var url = document.getElementById("url").value
        $this = $(this)
        var url = $this.attr('action') + getLocationPathname(url);
        window.location.href = url;
        });
});

function getLocationPathname(href) {
    var l = document.createElement("a");
    l.href = href
    return l.pathname
}
/* Project specific Javascript goes here. */
$(document).ready(function(){
  $("#startDate").on("change",function(){
    $("#endDate").datepicker('setStartDate',$(this).val());
  });

  $("#cloudRange").slider();

  $("#search").on("click", function(){
    var url = "//" + window.location.host + window.location.pathname + "?";

    var scene = $("#scene").val();
    var path = $("#path").val();
    var row = $("#row").val();
    var sat = $("#sat").val();
    var status = $("#status").val();
    var maxcloud = $("#cloudRange").val();
    var start = $("#startDate").val();
    var end = $("#endDate").val();
    var bbox = $("#formBounds").attr('value');

    if (scene && scene != "")
      url = url + "name=" + scene + "&";
    if (path && path != "")
      url = url + "path=" + path + "&";
    if (row && row != "")
      url = url + "row=" + row + "&";
    if (sat && sat != "")
      url = url + "sat=" + sat + "&";
    if (status && status != "")
      url = url + "status=" + status + "&";
    if ( maxcloud && maxcloud != "")
      url = url + "max_cloud=" + maxcloud + "&";
    if (start && start != "")
      url = url + "start=" + start + "&";
    if (end && end != "")
      url = url + "end=" + end + "&";
    if (bbox && bbox != "")
      url = url + "bbox=" + bbox + "&";

    url = url.substring(0,url.length - 1);
    this.href = url;
  });
});

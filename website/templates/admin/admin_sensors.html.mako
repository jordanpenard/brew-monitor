<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Admin sensors</title>
</%block>

<%block name="title">
    <h1 class="title">Admin sensors</h1>
</%block>

<script>

function show_confirm(id, name, url) {
    $("#sensor_id").html(id);
    $("#popup-message").html("Are you sure you want to delete " + name + "?");
    $("#confirm-modal").modal('show');
    $("#modal-btn-yes").attr("onclick", "location.href='" + url + "'");
}

function edit(id, url) {
    name = $("#sensor_name_"+id).html()
    secret = $("#sensor_secret_"+id).html()
    $("#sensor_name_"+id).html('<input type="text" name="sensor_name" form="sensor_'+id+'" value="' + name + '">')
    $("#sensor_secret_"+id).html('<input type="text" name="sensor_secret" form="sensor_'+id+'" value="' + secret + '">')
    $("#edit_"+id).html('<i class="fas fa-save" style="width: 16px;" aria-hidden="true"></i>')
    $("#edit_"+id).attr("onclick", "form.submit()")
    $("#edit_"+id).attr("form", "sensor_"+id)
    $("#delete_"+id).prop("disabled", true)
}

</script>

<div class="modal fade" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel" aria-hidden="true" id="confirm-modal">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="popup-message"></h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <input type="hidden" id="sensor_id"></input>
      </div>
      <div class="modal-footer">
        <button class="btn btn-danger" id="modal-btn-yes">Yes</a>
        <button class="btn btn-secondary" data-dismiss="modal" id="modal-btn-no">No</a>
      </div>
    </div>
  </div>
</div>

<div class="column is-4 is-offset-4">
    <div class="box">
        <table class="table" id="sensor_table">
            <thead><tr>
                <th scope="col">ID</th>
                <th scope="col">Name</th>
                <th scope="col">Secret</th>
                <th scope="col">Owner</th>
                <th scope="col"></th>
            </tr></thead>
            % for sensor in sensors:
            <tr>
                <form id="sensor_${sensor.id}" method="post" action="${url_for('admin.edit_sensor', id=sensor.id)}"></form>
                <td>${sensor.id}</td>
                <td id="sensor_name_${sensor.id}">${sensor.name}</td>
                <td id="sensor_secret_${sensor.id}">${sensor.secret}</td>
                <td>${sensor.owner}</td>
                <td>
                    <button type="button" id="delete_${sensor.id}" onClick='show_confirm(${sensor.id}, "${sensor.name}", "${url_for('admin.delete_sensor', id=sensor.id)}")' class="btn btn-danger btn-sm"><i class="fas fa-times" style="width: 16px;" aria-hidden="true"></i></button>
                    &nbsp;
                    <button type="button" id="edit_${sensor.id}" onClick='edit(${sensor.id})' class="btn btn-primary btn-sm"><i class="fas fa-pen" style="width: 16px;" aria-hidden="true"></i></button>
                </td>
            </tr>
            % endfor
        </table>
    </div>
</div>

<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Admin sensors</title>
</%block>

<%block name="title">
    <h1 class="title">Admin sensors</h1>
</%block>

${parent.add_sensor_view()}

<script type="text/javascript">

function show_confirm(id, name, url) {
    $("#sensor_id").html(id);
    $("#popup-message").html("Are you sure you want to delete " + name + "?");
    $("#confirm-modal").modal('show');
    $("#modal-btn-yes").attr("onclick", "location.href='" + url + "'");
}

function edit(id, url) {
    name = $("#sensor_name_"+id).html()
    secret = $("#sensor_secret_"+id).html()
    owner = $("#sensor_owner_"+id).html()
    max_battery = $("#sensor_max_battery_"+id).html()
    min_battery = $("#sensor_min_battery_"+id).html()

    $("#sensor_name_"+id).html('<input type="text" name="sensor_name" form="sensor_'+id+'" value="' + name + '">')
    $("#sensor_secret_"+id).html('<input type="text" name="sensor_secret" form="sensor_'+id+'" value="' + secret + '">')
    $("#sensor_max_battery_"+id).html('<input type="text" name="sensor_max_battery" style="width:100px" form="sensor_'+id+'" value="' + max_battery + '">')
    $("#sensor_min_battery_"+id).html('<input type="text" name="sensor_min_battery" style="width:100px" form="sensor_'+id+'" value="' + min_battery + '">')
    $("#edit_"+id).html('<i class="fas fa-save" style="width: 16px;" aria-hidden="true"></i>')
    $("#edit_"+id).attr("onclick", "form.submit()")
    $("#edit_"+id).attr("form", "sensor_"+id)
    $("#delete_"+id).prop("disabled", true)
    
    owner_select = '<select name="sensor_owner_id" form="sensor_'+id+'">'
% for user in users:
    owner_select += '<option id="owner_select_${user.username}" value="${user.id}">${user.username}</option>'
% endfor
    owner_select += '</select>'
    
    $("#sensor_owner_"+id).html(owner_select)
    $("#owner_select_" + owner).prop("selected", true)
}

</script>

<div class="modal fade" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel" aria-hidden="true" id="confirm-modal">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="popup-message"></h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <input type="hidden" id="sensor_id" />
      </div>
      <div class="modal-body">
          <p>This will delete all associated data</p>
      </div>
      <div class="modal-footer">
        <a class="btn btn-danger" id="modal-btn-yes">Yes</a>
        <a class="btn btn-secondary" data-dismiss="modal" id="modal-btn-no">No</a>
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
                <th scope="col">Max battery</th>
                <th scope="col">Min battery</th>
                <th scope="col"></th>
            </tr></thead>
            % for sensor in sensors:
            <tr>
                <form id="sensor_${sensor.id}" method="post" action="${url_for('admin.edit_sensor', sensor_id=sensor.id)}"></form>
                <td>${sensor.id}</td>
                <td id="sensor_name_${sensor.id}">${sensor.name}</td>
                <td id="sensor_secret_${sensor.id}">${sensor.secret}</td>
                <td id="sensor_owner_${sensor.id}">${sensor.owner}</td>
                <td id="sensor_max_battery_${sensor.id}">${sensor.max_battery}</td>
                <td id="sensor_min_battery_${sensor.id}">${sensor.min_battery}</td>
                <td>
                    <button type="button" id="delete_${sensor.id}" onClick='show_confirm(${sensor.id}, "${sensor.name}", "${url_for('admin.delete_sensor', sensor_id=sensor.id)}")' class="btn btn-danger btn-sm"><i class="fas fa-times" style="width: 16px;" aria-hidden="true"></i></button>
                    &nbsp;
                    <button type="button" id="edit_${sensor.id}" onClick='edit(${sensor.id})' class="btn btn-primary btn-sm"><i class="fas fa-pen" style="width: 16px;" aria-hidden="true"></i></button>
                </td>
            </tr>
            % endfor
        </table>
    </div>
</div>

<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Admin projects</title>
</%block>

<%block name="title">
    <h1 class="title">Admin projects</h1>
</%block>

<script>

function show_confirm(id, name, url) {
    $("#project_id").html(id)
    $("#popup-message").html("Are you sure you want to delete " + name + "?")
    $("#confirm-modal").modal('show')
    $("#modal-btn-yes").attr("onclick", "location.href='" + url + "'")
}

function edit(id, url) {
    name = $("#project_name_"+id).html()
    owner = $("#project_owner_"+id).html()

    $("#project_name_"+id).html('<input type="text" name="project_name" form="project_'+id+'" value="' + name + '">')
    $("#edit_"+id).html('<i class="fas fa-save" style="width: 16px;" aria-hidden="true"></i>')
    $("#edit_"+id).attr("onclick", "form.submit()")
    $("#edit_"+id).attr("form", "project_"+id)
    $("#delete_"+id).prop("disabled", true)

    owner_select = '<select name="project_owner_id" form="project_'+id+'">'
    % for user in users:
        owner_select += '<option id="owner_select_${user['username']}" value="${user['id']}">${user['username']}</option>'
    % endfor
    owner_select += '</select>'
    
    $("#project_owner_"+id).html(owner_select)
    $("#owner_select_" + owner).prop("selected", true)
}

</script>

<div class="modal fade" tabindex="-1" role="dialog" aria-labelledby="mySmallModalLabel" aria-hidden="true" id="confirm-modal">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="popup-message"></h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <input type="hidden" id="project_id"></input>
      </div>
      <div class="modal-body">
          <p>This will delete all associated data</p>
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
        <table class="table" id="project_table">
            <thead><tr>
                <th scope="col">ID</th>
                <th scope="col">Name</th>
                <th scope="col">Owner</th>
                <th scope="col"></th>
                <th scope="col"></th>
            </tr></thead>
            % for project in projects:
            <tr>
                <form id="project_${project.id}" method="post" action="${url_for('admin.edit_project', id=project.id)}"></form>
                <td>${project.id}</td>
                <td id="project_name_${project.id}">${project.name}</td>
                <td id="project_owner_${project.id}">${project.owner}</td>
                <td>
                    <button type="button" id="delete_${project.id}" onClick='show_confirm(${project.id}, "${project.name}", "${url_for('admin.delete_project', id=project.id)}")' class="btn btn-danger btn-sm"><i class="fas fa-times" style="width: 16px;" aria-hidden="true"></i></button>
                    &nbsp;
                    <button type="button" id="edit_${project.id}" onClick='edit(${project.id})' class="btn btn-primary btn-sm"><i class="fas fa-pen" style="width: 16px;" aria-hidden="true"></i></button>
                </td>
            </tr>
            % endfor
        </table>
    </div>
</div>

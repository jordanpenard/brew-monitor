<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Admin projects</title>
</%block>

<%block name="title">
    <h1 class="title">Admin projects</h1>
</%block>

<script>

function show_confirm(id, name, url) {
    $("#project_id").html(id);
    $("#popup-message").html("Are you sure you want to delete " + name + "?");
    $("#confirm-modal").modal('show');
    $("#modal-btn-yes").attr("onclick", "location.href='" + url + "'");
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
            </tr></thead>
            % for project in projects:
            <tr>
                <td>${project.id}</td>
                <td>${project.name}</td>
                <td>${project.owner}</td>
                <td><button onClick='show_confirm(${project.id}, "${project.name}", "${url_for('admin.delete_project', id=project.id)}")' class="btn btn-danger"><i class="fas fa-times" style="width: 16px;" aria-hidden="true"></i></a></td>
            </tr>
            % endfor
        </table>
    </div>
</div>

<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Project List</title>
</%block>

<%block name="title">
    <h1>Project List</h1>
</%block>

## TODO(tr) Should contain the list of sensors/projects + a button to sensors/projects.

<%block name="elem_links_row">
% if show_add_project:
    <form id="add_project_form" action="${url_for('accessor.add_project')}" method="post" class="inline-form">
        <div class="input-group">
            <div class="input-group-prepend">
                <span class="input-group-text">New project</span>
            </div>
            <input id="project_name" type="text" name="name" class="form-control" placeholder="Project name" maxlength="64" required/>
            <div class="input-group-append">
                <button class="btn btn-outline-secondary" type="submit">
                    <i class="fas fa-plus-circle"></i>
                </button>
            </div>
        </div>
    </form>
    <br>
% endif
${parent.elem_links_row()}
</%block>

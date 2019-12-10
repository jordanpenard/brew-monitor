<%inherit file="../generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Project List</title>
</%block>

<%block name="title">
    <h1>Project List</h1>

    <script type="text/javascript">
        $('#accessor_project_nav_item').addClass('active');
    </script>
</%block>

## TODO(tr) Should contain the list of sensors/projects + a button to sensors/projects.

<%def name="render_project_card(item)">
    <script>
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        })
    </script>
    <div class="col-lg-3 col-md-4 col-sm-6 mb-3">
        <div class="card">
          <div class="card-header">
            <div style="float: left;">
                <a href="${item.get_link()}">${item.get_name()}</a>
            </div><div style="float: right;">
                % if item.is_linked():
                    <span style="vertical-align: middle;" class="badge badge-success"><i aria-hidden="true" class="fas fa-link"></i></span>
                % endif
                % if item.is_active():
                    <span style="vertical-align: middle;" class="badge badge-primary" data-toggle="tooltip" data-placement="top" title="${item.last_active_str()}">Active</span>
                % else:
                    <span style="vertical-align: middle;" class="badge badge-secondary" data-toggle="tooltip" data-placement="top" title="${item.last_active_str()}">Inactive</span>
                % endif
            </div>
          </div>
          <div class="card-body">
            <p class="card-text">
                Owner : ${item.owner}<br>
                % if item.last_temperature:
                    Temperature : ${item.last_temperature}&deg;C<br>
                % endif
                % if item.first_angle and item.last_angle:
                    &Delta;&Theta; : ${float(item.first_angle) - float(item.last_angle)}&deg;<br>
                % endif
                % if item.first_active and item.last_active:
                    Length : ${item.last_active - item.first_active}
                % endif
            </p>
          </div>
        </div>
    </div>
</%def>

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

<div class="row">
    % for item in elem_links:
        ${render_project_card(item)}
    % endfor
    % if not elem_links:
        <div class="col-12">No project.</div>
    % endif
</div>

</%block>

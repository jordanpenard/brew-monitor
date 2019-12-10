<%inherit file="../generic.html.mako" />

<script>
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    })
</script>

<%block name="head_title">
    <title>Brew Monitor - Sensor List</title>
</%block>

<%block name="title">
    <h1>Sensor List</h1>

    <script type="text/javascript">
        $('#accessor_sensor_nav_item').addClass('active');
    </script>
</%block>

## TODO(tr) Should contain the list of sensors/projects + a button to sensors/projects.

<%def name="render_sensor_card(item)">
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
            <p class="card-text">Owner : ${item.owner}</p>
          </div>
        </div>
    </div>
</%def>

<%block name="elem_links_row">
% if show_add_sensor:
    <form id="add_sensor_form" action="${url_for('accessor.add_sensor')}" method="post" class="inline-form">
        <div class="input-group">
            <div class="input-group-prepend">
                <span class="input-group-text">New sensor</span>
            </div>
            <input id="sensor_name" type="text" name="name" class="form-control" placeholder="Sensor name" maxlength="64" required/>
            <input id="sensor_secret" type="text" name="secret" class="form-control" placeholder="Sensor secret" maxlength="64" required/>
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
        ${render_sensor_card(item)}
    % endfor
    % if not elem_links:
        <div class="col-12">No sensor.</div>
    % endif
</div>

</%block>

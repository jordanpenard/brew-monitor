<%inherit file="../generic.html.mako" />

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

<%def name="render_icons(linked_project, last_active_str, battery_info)">
<div style="float: right;">
% if linked_project:
    <span style="vertical-align: middle;" class="badge badge-success" title="Project id ${linked_project | h}">
        <i aria-hidden="true" class="fas fa-link"></i>
    </span>
% endif
% if last_active_str:
    <i aria-hidden="true" class="fas fa-podcast" data-toggle="tooltip" data-placement="top" title="${last_active_str}"></i>
% endif
    <i class="fas ${battery_info['icon']}" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="${battery_info['tooltip']}"></i>
</div>
</%def>


<%def name="render_sensor_card(item)">
    <script type="text/javascript">
        $(function () {
          $('[data-toggle="tooltip"]').tooltip()
        })
    </script>
    <div class="col-lg-3 col-md-4 col-sm-6 mb-3">
        <div class="card">
          <div class="card-header">
            <div style="float: left;">
                <a href="${item.get_link()}">${item.get_label()}</a>
            </div>
            ${render_icons(
                item.linked_project,
                item.last_active_str() if item.is_active() else None,
                item.battery_info(),
            )}
          </div>
          <div class="card-body">
            <p class="card-text">
                Owner : ${item.owner}
            </p>
          </div>
        </div>
    </div>
</%def>

<%block name="elem_links_row">
% if show_add_sensor:
    ${parent.add_sensor_view()}
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

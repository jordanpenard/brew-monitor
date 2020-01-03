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

<%def name="render_sensor_card(item)">
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
                    <i style="color: #007bff" aria-hidden="true" class="fas fa-broadcast-tower" data-toggle="tooltip" data-placement="top" title="${item.last_active_str()}"></i>
                % endif
                % if item.last_battery and item.max_battery and item.min_battery:
                    <%
                        battery_pct = item.last_battery_pct()
                        if battery_pct > 80:
                            battery_logo = "fa-battery-full"
                            battery_color = "#28a745"
                        elif battery_pct > 60:
                            battery_logo = "fa-battery-three-quarters"
                            battery_color = "#28a745"
                        elif battery_pct > 40:
                            battery_logo = "fa-battery-half"
                            battery_color = "orange"
                        elif battery_pct > 20:
                            battery_logo = "fa-battery-quarter"
                            battery_color = "orange"
                        else:
                            battery_logo = "fa-battery-empty"
                            battery_color = "red"
                    %>
                    <i class="fas ${battery_logo}" style="color: ${battery_color}; float: right; margin: 5px 0px 0px 5px;" aria-hidden="true" data-toggle="tooltip" data-placement="top" title="${battery_pct}%"></i>
                % endif
                
            </div>
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

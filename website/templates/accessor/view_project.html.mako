<%inherit file="../generic.html.mako" />

<%namespace name="project" file="project.html.mako" />
<%namespace name="sensor" file="sensor.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - ${elem_name | h}</title>
</%block>

<%block name="title">
    <h1>
        ${elem_name | h}
        % if elem_obj:
            ${project.render_icons(
                elem_obj.active_sensor,
                elem_obj.is_active(),
                elem_obj.last_active_str(),
            )}
        % endif
    </h1>
</%block>

<h2>Linked sensor</h2>

<div class="row">
% if linked_elem is not None:
    ${sensor.render_sensor_card(linked_elem)}

    % if management_link is not None :
    <div class="col-6">
        <form action="${management_link}" method="POST">
            <button class="btn btn-danger" type="submit">
                <i class="fas fa-unlink"></i> Unlink sensor
            </button>
        </form>
    </div>
    % endif
% else:
    <div class="col-12">No linked elements.</div>
% endif

</div>

% if management_link is not None and management_items :
<form action="${management_link}" method="POST">
    <select name="sensor_id" required>
        <option value="" selected disabled>Choose new sensor</option>
    % for item in management_items:
        <option value="${item['value']}">${item['label'] | h}</option>
    % endfor
    </select>
    <button class="btn btn-success" type="submit">
        <i class="fas fa-link"></i> Link selected sensor
    </button>
</form>
% endif

% if elem_links :
<h2>Previously linked sensor</h2>

<div class="row">
    % for item in elem_links:
        ${sensor.render_sensor_card(item)}
    % endfor
</div>
% endif

<%include file="view_data.html.mako"/>

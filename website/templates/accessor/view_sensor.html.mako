<%inherit file="../generic.html.mako" />

<%namespace name="project" file="project.html.mako" />
<%namespace name="sensor" file="sensor.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - ${elem_name | h}</title>
</%block>

<%block name="title">
    <h1>
        ${elem_name | h} (sensor_id=${elem_id | h})
    % if elem_obj:
        ${sensor.render_icons(
            elem_obj.linked_project,
            elem_obj.last_active_str() if elem_obj.is_active() else None,
            elem_obj.battery_info(),
        )}
    % endif
    </h1>
</%block>

<h2>Linked project</h2>

<div class="row">
% if linked_elem is not None:
    ${project.render_project_card(linked_elem)}

    % if management_link is not None :
    <div class="col-6">
        <form action="${management_link}" method="POST">
            <button class="btn btn-danger" type="submit">
                <i class="fas fa-unlink"></i> Unlink project
            </button>
        </form>
    </div>
    % endif
% else:
    <div class="col-12">No linked elements.</div>
% endif

</div>

% if elem_links :
<h2>Previously linked project</h2>

<div class="row">
    % for item in elem_links:
        ${project.render_project_card(item)}
    % endfor
</div>
% endif

<%include file="view_data.html.mako"/>

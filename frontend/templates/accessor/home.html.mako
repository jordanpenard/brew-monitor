<%inherit file="../generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Projects</title>
</%block>

<%block name="title">
    <h1>Project list</h1>
    
    <script type="text/javascript">
        $('#accessor_nav_item').addClass('active');
    </script>
</%block>

This page will contain links to the different beer projects.<br />

This will also contain ways to register new sensors.<br />

Add probably aslo links for user management.<br />

<div class="row">
    % for proj in projects:
    <div class="col-lg-3 col-md-4 col-sm-6">
        <a href="${url_for('accessor.get_project', project_id=proj.id)}" target="_blank" class="btn btn-primary">${proj.name | h}</a>
    </div>
    % endfor
    % if not projects:
    <div class="col-12">
        No projects :(
    </div>
    % endif
</div>

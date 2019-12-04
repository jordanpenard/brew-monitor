<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - ${elem_class.title() | h} List</title>
</%block>

<%block name="title">
    <h1>${elem_class.title() | h} List</h1>
    
    <script type="text/javascript">
        $('#accessor_${elem_class | h}_nav_item').addClass('active');
    </script>
</%block>

## TODO(tr) Should contain the list of sensors/projects + a button to sensors/projects.

<%block name="elem_links_row">
% if management_link is not None:
    ## Management row
    <%
        target = management_link.pop('link')
        id = f'add_{elem_class}'
    %>
    <form id="${id}_form" action="${target}" target="_blank" method="post" class="inline-form">
        <div class="input-group">
            <button class="btn ${management_link['btn_class']}" type="submit">
        % if 'icon_classes' in management_link:
                <i class="${management_link['icon_classes']}"></i>
        % endif
                ${management_link['label'] | h}
            </button>
            <label for="${elem_class}_name" class="sr-only">Name:</label>
            <input id="${elem_class}_name" type="text" name="name" class="form-control" placeholder="${elem_class.title()} name" maxlength="64" required/>
        </div>
    </form>
% endif
${parent.elem_links_row()}
</%block>

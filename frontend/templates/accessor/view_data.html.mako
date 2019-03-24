<%!
    import json
%>
<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - ${elem_name}</title>
</%block>

<%block name="title">
    <h1>${elem_name}</h1>
    
    <script type="text/javascript">
        $('#accessor_nav_item').addClass('active');
    </script>
</%block>

<%def name="render_link(link_data)" >
    <a class="btn ${link_data['btn_class']}"
    % if link_data['link']:
        href="${link_data['link']}"
    % else:
        href="#"
    % endif
    % if link_data.get('target'):
        target="${link_data['target']}"
    % endif
    >
        ${link_data['label'] | h}
    % if link_data.get('last_active'):
        <br />(${link_data['last_active'] | h})
    % endif
    </a>
</%def>

<div class="row">
    % for link in elem_links:
        <div class="col-lg-3 col-md-4 col-sm-6">
            ${render_link(link)}
        </div>
    % endfor
    % if not elem_links:
        <div class="col-12">No links.</div>
    % endif
</div>

<h2>Data</h2>

<div id='data_links'>
    <div class="btn-group-sm">
    % for link in data_links:
        ${render_link(link)}
    % endfor
    </div>
</div>

<div class="row">
    <div class="col-12">
        <table id="${elem_id}_table" class="table table-striped"></table>

        <script type="text/javascript">
            $(document).ready(function () {
                function renderDatetime(data, disp_type, row, meta) {
                    if (!data) {
                        return '-';
                    }
                    if (disp_type === 'display') {
                        return data.label;
                    }
                    return data.timestamp;
                }
            
                dom = "<'row'<'col-sm-12 col-md-4'l><'col-sm-12 col-md-4'<'#download_links'>><'col-sm-12 col-md-4'f>>" +
                    "<'row'<'col-12'tr>>" +
                    "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>";
            
                var dt = $('#${elem_id}_table').DataTable({
                    searching: false,
                    dom: dom,
                    columns: [
                        {data: 'when', title: 'When', render: renderDatetime},
                        {data: 'gravity', title: 'Gravity', type: 'num'},
                        {data: 'temperature', title: 'Temperature (C)', type: 'num'}
                    ],
                    ## TODO(tr) js dump that protects " and <, > etc
                    data: ${json.dumps(datatable)}
                });
                
                ## Populate the links
                ## TODO(tr) This is dirty and I should generate the link data in JS.
                $('#download_links').html($('#data_links').html());
                $('#data_links').html('');
            });
        </script>
    </div>
</div>

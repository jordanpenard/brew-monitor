<%!
    import json
%>

<div id='data_links'>
    <div class="btn-group-sm">
    % for item in data_links:
        <a href="${item['link']}" class="btn ${item['btn_class']}" target="${item['target']}">${item['label']}</a>
    % endfor
    </div>
</div>

<h2>Data</h2>

% if datatable:
## Do not show if we have no data
<div class="row">
    <div class="col-12">
        <div id="${elem_id}_plot"></div>
    </div>
</div>
<script type="text/javascript">
    $(document).ready(function () {
        Plotly.newPlot('${elem_id}_plot', ${json.dumps(plot['data'])}, ${json.dumps(plot['layout'])});
    });
</script>
% endif

<div class="row">
    <div class="col-12">
        <table id="${elem_id}_table" class="table table-stripped"></table>

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

                function renderActions(data, disp_type, row, meta) {
                    if (disp_type === 'display' && data) {
                        ##return '<a href="' + data + '" class="btn btn-sm btn-danger">' +
                        ##    '<i class="fas fa-times"></i>' +
                        ##    '</a>';
                        return '<form action="' + data + '" method="POST">' +
                            '<button type="submit" class="btn btn-sm btn-danger">' +
                            '<i class="fas fa-times"></i>' +
                            '</button>' +
                            '</form>';
                    }
                    return data || '-';
                }

                dom = "<'row'<'col-sm-12 col-md-4'l><'col-sm-12 col-md-4'<'#download_links'>><'col-sm-12 col-md-4'f>>" +
                    "<'row'<'col-12'tr>>" +
                    "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>";
            
                var dt = $('#${elem_id}_table').DataTable({
                    searching: false,
                    dom: dom,
                    columns: [
                        {data: 'when', title: 'When', render: renderDatetime},
                        ##{data: 'gravity', title: 'Gravity', type: 'num'},
                        {data: 'angle', title: 'Angle (&deg;)', type: 'num'},
                        {data: 'temperature', title: 'Temperature (C)', type: 'num'},
                        {data: 'battery', title: 'Battery (V)', type: 'num-fmt'},
                        {data: 'delete_link', title: '-', render: renderActions, sortable: false, searchable: false, visible: ${'true' if allow_delete_datapoints else 'false'}}
                    ],
                    order: [0, 'desc'],
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

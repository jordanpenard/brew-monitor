<%inherit file="../generic.html.mako" />

<%def name="render_card(item)">
    <div class="col-lg-3 col-md-4 col-sm-6 mb-3">
        <div class="card">
          <div class="card-header">
            <div style="float: left;">
                <a class="stretched-link" href="${item['link']}">${item['label']}</a>
            </div><div style="float: right;">
                ${item['sensor_state'].value}
            </div>
          </div>
          <div class="card-body">
            <p class="card-text">${item['last_active']}</p>
            <p class="card-text">Owner : ${item['owner']}</p>
          </div>
        </div>
    </div>
</%def>

<%block name="elem_links_row">
<div class="row">
    % for item in elem_links:
        ${render_card(item)}
    % endfor
    % if not elem_links:
        <div class="col-12">No links.</div>
    % endif
</div>
</%block>

${next.body()}

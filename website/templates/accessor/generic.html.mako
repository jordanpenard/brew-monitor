<%inherit file="../generic.html.mako" />

<script>
    $(function () {
      $('[data-toggle="tooltip"]').tooltip()
    })
</script>

<%def name="render_card(item)">
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

<%inherit file="../generic.html.mako" />

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
    % if 'icon_classes' in link_data:
        <i class="${link_data['icon_classes']}"></i>
    % endif
        ${link_data['label'] | h}
    % if link_data.get('last_active'):
        <br />(${link_data['last_active'] | h})
    % endif
    </a>
</%def>

<%block name="elem_links_row">
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
</%block>

${next.body()}

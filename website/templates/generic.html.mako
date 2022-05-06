<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <%block name="head_title">
        <title>Brew Monitor</title>
    </%block>
    <%block name="viewport">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    </%block>
    <%block name="scripts">
        ## bootstrap
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
        ## datatable
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.18/js/jquery.dataTables.min.js"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.18/js/dataTables.bootstrap4.min.js"></script>
        ## plotly
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        ## font-awesome
        <script src="https://kit.fontawesome.com/e0ab70fa91.js"></script>
    </%block>
    <%block name="css">
        ## bootstrap
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        ## datatable
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.18/css/dataTables.bootstrap4.min.css">
        <style>
            html {
                position: relative;
                min-height: 100%;
            }
            body {
                /* Margin bottom by footer height */
                margin-bottom: 60px;
            }
            .footer {
                position: absolute;
                bottom: 0;
                width: 100%;
                /* Set the fixed height of the footer here */
                height: 60px;
                line-height: 60px; /* Vertically center the text there */
                background-color: #f5f5f5;
            }
            .nav-item.active a {
                text-decoration: underline;
            }
            #user_table tr td {
                vertical-align: middle;
            }
            h1 {
                margin-top: 30px;
                margin-bottom: 30px;
            }
            .fa-battery-full {
                color: #28a745;
                float: right;
                margin: 5px 0px 0px 5px;
            }
            .fa-battery-three-quarters {
                color: #28a745;
                float: right;
                margin: 5px 0px 0px 5px;
            }
            .fa-battery-half {
                color: orange;
                float: right;
                margin: 5px 0px 0px 5px;
            }
            .fa-battery-quarter {
                color: orange;
                float: right;
                margin: 5px 0px 0px 5px;
            }
            .fa-battery-empty {
                color: red;
                float: right;
                margin: 5px 0px 0px 5px;
            }
            .fa-podcast {
                color: #007bff;
                float: right;
                margin: 5px 0px 0px 5px;
            }
        </style>
    </%block>
</head>
<body>
    <div class="header">
        <%block name="header">
            <nav class="navbar navbar-inverse navbar-expand-lg navbar-light bg-light">
                <a class="navbar-brand" href="${url_for('home.home')}">Brew Monitor</a>
                ## Make navbar collapsible when the window is too small
                <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar_collapsible" aria-controls="navbar_collapsible" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbar_collapsible">
                    <ul class="nav navbar-nav mr-auto">
                        <li class="nav-item" id="accessor_project_nav_item">
                            <a class="nav-link" href="${url_for('accessor.all_projects')}">Project List</a>
                        </li>
                        <li class="nav-item" id="accessor_sensor_nav_item">
                            <a class="nav-link" href="${url_for('accessor.all_sensors')}">Sensor List</a>
                        </li>
                % if current_user.is_authenticated and current_user.is_admin:
                        <li class="nav-item dropdown" id="admin_nav_item">
                            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdownAdmin" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                            <i class="fas fa-tools"></i> Admin
                            </a>
                            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdownAdmin">
                              <a class="dropdown-item" href="${url_for('admin.all_users')}">Users</a>
                              <a class="dropdown-item" href="${url_for('admin.all_projects')}">Projects</a>
                              <a class="dropdown-item" href="${url_for('admin.all_sensors')}">Sensor</a>
                            </div>
                        </li>
                    % endif
                    </ul>
                    % if not current_user.is_authenticated:
                        <ul class="nav navbar-nav navbar-right">
                            <li class="nav-item" id="login_nav_item">
                                <a class="nav-link" href="${url_for('home.login')}">Login</a>
                            </li>
                        </ul>
    		        % else:
                        ## Show the current user information
                        <ul class="nav navbar-nav navbar-right">
                            <li class="nav-item" id="username_nav_item">
                                <a class="nav-link disabled">
                                    % if current_user.is_admin:
                                    <i class="fas fa-user"></i>
                                    % endif
                                    ${current_user.username}
                                </a>
                            </li>
                            <li class="nav-item" id="logout_nav_item">
                                <a class="nav-link" href="${url_for('home.logout')}">Logout</a>
                            </li>
                        </ul>
    		        % endif
                </div>

            </nav>
        </%block>
    </div>

    <main role="main" class="container">
        <%block name="title">
            <h1>Brew Monitor - Home</h1>
        </%block>
    
        ${next.body()}
    </main>

    <div class="footer">
        <%block name="footer">
            <footer class="footer">
                <span class="text-muted" style="padding: 0px 1rem;">
                    See <a target="_blank" href="https://github.com/jordanpenard/brew-monitor">jordanpenard/brew-monitor</a> for licencing.
                </span>
            </footer>
        </%block>
    </div>
</body>
</html>

<%def name="add_sensor_view()">
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
</%def>

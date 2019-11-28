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
        </style>
    </%block>
</head>
<body>
    <div class="header">
        <%block name="header">
            <nav class="navbar navbar-inverse navbar-expand-lg navbar-light bg-light">
                <a class="navbar-brand" href="${url_for('home.index')}">Brew Monitor</a>
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
                        <li class="nav-item" id="user_nav_item">
                            <a class="nav-link" href="#">User Management (pending)</a>
                        </li>
                    </ul>
                    <ul class="nav navbar-nav navbar-right">
                        <li class="nav-item" id="accessor_project_nav_item">
                            <a href="" class="nav-link" data-toggle="modal" data-target="#modalLoginForm">Login</a>
                        </li>
                    </ul>
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

    <div class="modal fade" id="modalLoginForm" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog" role="document">
	<div class="modal-content">
	  <form>
	    <div class="modal-header text-center">
              <h4 class="modal-title w-100 font-weight-bold">Sign in</h4>
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">
        	<span aria-hidden="true">&times;</span>
              </button>
	    </div>
	    <div class="modal-body mx-3">
              <div class="form-group">
        	<label for="username">Username</label>
        	<input type="text" class="form-control" id="username" placeholder="Username">
              </div>
              <div class="form-group">
        	<label for="password">Password</label>
        	<input type="password" class="form-control" id="password" placeholder="Password">
              </div>
              <div class="form-check">
        	<input type="checkbox" class="form-check-input" id="remember_me">
        	<label class="form-check-label" for="remember_me">Remember me</label>
              </div>
	    </div>
	    <div class="modal-footer d-flex justify-content-center">
              <button type="submit" class="btn btn-primary">Sign in</button>
	    </div>
	  </form>
	</div>
      </div>
    </div>

    <div class="footer">
        <%block name="footer">
            <footer class="footer">
                <span class="text-muted">
                    See <a href="https://github.com/jordanpenard/brew-monitor">brew-monitor</a> for licencing.
                </span>
            </footer>
        </%block>
    </div>
</body>
</html>

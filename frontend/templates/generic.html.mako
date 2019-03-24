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
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.19/js/jquery.dataTables.js"></script>
    </%block>
    <%block name="css">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.19/css/jquery.dataTables.css">
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
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <a class="navbar-brand" href="${url_for('home.index')}">Brew Monitor</a>
                ## Make navbar collapsible when the window is too small
                <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar_collapsible" aria-controls="navbar_collapsible" aria-expanded="false" aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbar_collapsible">
                    <ul class="navbar-nav">
                        <li class="nav-item" id="accessor_nav_item">
                            <a class="nav-link" href="${url_for('accessor.index')}">Project list</a>
                        </li>
                        <li class="nav-item" id="sensor_nav_item">
                            <a class="nav-link" href="#">Sensor management (pending)</a>
                        </li>
                        <li class="nav-item" id="user_nav_item">
                            <a class="nav-link" href="#">User management (pending)</a>
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
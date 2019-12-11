<%inherit file="generic.html.mako" />
<%namespace name="generic" file="generic.html.mako" />

<script type="text/javascript">
    $('#login_nav_item').addClass('active');
</script>

<%block name="head_title">
    <title>Brew Monitor - Login</title>
</%block>
<%block name="title">
</%block>

<br><br><br>
<div class="box text-center" style="margin: auto; max-width: 360px; padding: 30px; background-color: #f8f9fa; border-radius: .25rem; border: 1px solid rgba(0,0,0,.125);">
    <form method="POST" action="${url_for('home.check_login')}">
        <h3 class="mb-3 font-weight-normal">Please sign-in</h1>

        % if error:
            <div class="alert alert-danger" role="alert">
                ${error}
            </div>
        % endif

        <input class="form-control mb-3" type="text" name="username" placeholder="Username" autofocus="">
        <input class="form-control mb-3" type="password" name="password" placeholder="Password">

        <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" value="remember" id="remember">
            <label class="form-check-label" for="remember">Remember me</label>
        </div>
        <button class="btn btn-lg btn-primary btn-block" type="submit">Login</button>
    </form>
</div>

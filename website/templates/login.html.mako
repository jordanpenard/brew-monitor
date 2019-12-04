<%inherit file="generic.html.mako" />
<%namespace name="generic" file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Login</title>
</%block>

<div class="column is-4 is-offset-4">
    <h3 class="title">Login</h3>
    <div class="box">
        <form method="POST" action="${url_for('home.check_login')}">
            <div class="field">
                <div class="control">
                    <input class="input is-large" type="text" name="username" placeholder="Username" autofocus="">
                </div>
            </div>

            <div class="field">
                <div class="control">
                    <input class="input is-large" type="password" name="password" placeholder="Password">
                </div>
            </div>
            <div class="field">
                <label class="checkbox" name="remember">
                    <input type="checkbox">
                    Remember me
                </label>
            </div>
            <button class="button is-block is-info is-large is-fullwidth">Login</button>
        </form>
    </div>
</div>

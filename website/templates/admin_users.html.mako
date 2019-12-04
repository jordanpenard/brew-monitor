<%inherit file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Admin users</title>
</%block>

<%block name="title">
    <h1 class="title">Admin users</h1>
</%block>

<div class="column is-4 is-offset-4">
    <div class="box">
        <table class="table" id="user_table">
            <thead><tr>
                <th scope="col">ID</th>
                <th scope="col">Username</th>
                <th scope="col">Password</th>
                <th scope="col">Is admin</th>
                <th scope="col"></th>
            </tr></thead>
            % for user in users:
            <tr>
                <td>${user['id']}</td>
                <td>${user['username']}</td>
                <td>*****</td>
                <td><input disabled type="checkbox" 
                    % if user['is_admin']:
                    checked
                    % endif
                ></td>
                <td><a href="${url_for('home.delete_user', id=user['id'])}" 
                    % if user['id'] == current_user.id:
                        class="btn btn-danger disabled"
                    % else:
                        class="btn btn-danger"
                    % endif
                ><i class="fas fa-times" style="width: 16px;" aria-hidden="true"></i></a></td>
            </tr>
            % endfor
            <tr><form action="${url_for('home.add_user')}" method="post">
                <td></td>
                <td><input class="form-control" type="text" name="username"></td>
                <td><input class="form-control" type="password" name="password"></td>
                <td><input type="checkbox" name="is_admin"></td>
                <td><button class="btn btn-success" type="submit">
                    <i class="fas fa-plus-circle" aria-hidden="true"></i>
                </button></td>
            </form></tr>
        </table>
    </div>
</div>

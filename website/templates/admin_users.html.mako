<%!
    import json
%>
<%inherit file="generic.html.mako" />
<%namespace name="generic" file="generic.html.mako" />

<%block name="head_title">
    <title>Brew Monitor - Admin users</title>
</%block>

<div class="column is-4 is-offset-4">
    <h3 class="title">Admin users</h3>
    <br>
    <div class="box">
        <table class="table">
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
                <td><input type="button" value="Delete"></td>
            </tr>
            % endfor
            <tr>
                <td></td>
                <td><input type="text" name="username"></td>
                <td><input type="text" name="password"></td>
                <td><input type="checkbox" name="is_admin"></td>
                <td><input type="submit" value="Add"></td>
            </tr>
        </table>
    </div>
</div>

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


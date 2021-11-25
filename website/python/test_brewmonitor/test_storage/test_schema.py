import pytest

from brewmonitor import schema
from make_dummy_data import make_dummy_data
from test_brewmonitor.conftest import config_from_client


@pytest.mark.parametrize('table', schema.tables)
def test_initialise_db_creates_table(tmp_app, table):
    # initialise_db is called when we create the tmp_client.
    bm_config = config_from_client(tmp_app)

    with bm_config.db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
                select name from sqlite_master where type='table' and name=?;
            ''',
            (table.__name__,)
        )
        assert cursor.fetchone()[0], f'Table {table.__name__} should exist at start'


def test_initialise_db_keeps_content(tmp_app):
    # initialise_db is called when we create the tmp_client.
    # Let's populate the tables and make sure it's unaffected when calling initialise_db again
    bm_config = config_from_client(tmp_app)

    rows_by_table = {}
    count_req = 'select count(*) from {table};'

    with bm_config.db_connection() as conn:
        for t in schema.tables:
            assert conn.execute(count_req.format(table=t.__name__)).fetchone()[0] == 0

    make_dummy_data(bm_config, 'admin')

    with bm_config.db_connection() as conn:
        for t in schema.tables:
            rows_by_table[t.__name__] = conn.execute(count_req.format(table=t.__name__)).fetchone()[0]
            assert rows_by_table[t.__name__] != 0, f'make_dummy_data should create data in {t.__name__}'

    schema.initialise_db(bm_config)

    with bm_config.db_connection() as conn:
        for t in schema.tables:
            assert (
                conn.execute(count_req.format(table=t.__name__)).fetchone()[0] == rows_by_table[t.__name__]
            ), f'number of rows changed in {t.__name__}'

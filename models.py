
import datetime

from pony import orm
from pony.orm import (
    Required,
    Optional,
    Set,
    PrimaryKey,
    unicode,
    )


# TODO this assumes that the database exists and has the timescale extension activated
# CREATE DATABASE databasename;
# CREATE EXTENSION IF NOT EXISTS timescaledb;

class PonyDB:

    def __init__(self, database_info):
        self.db = orm.Database()
        self.database_info = database_info
        self.timescaled_tables = []

    def binddb(self):
        self.db.bind(**self.database_info)
        self.db.generate_mapping(create_tables=True, check_tables=True)

    def define_entities(self):

        class Device(self.db.Entity):
           name = Required(str)
           readings = Set('Reading')

        class Reading(self.db.Entity):

            time = Required(datetime.datetime, sql_type='TIMESTAMP WITH TIME ZONE', default=datetime.datetime.now(datetime.timezone.utc))
            device = Required(Device)
            PrimaryKey(device, time)

        self.timescaled_tables.append(Reading.__name__)

    def timescale_tables(self):
        for t in self.timescaled_tables:
            print(f"Timescaling {t}")
            self.db.execute("SELECT create_hypertable('{}', 'time');".format(t.lower()))

    def create_views(self):
        self.db.execute("CREATE VIEW view_device AS select *, TRUE as filtered from device where device = 1;")

    def define_views(self):
        # TODO map previous view as a Pony object
        class ViewDevice(self.db.Entity):
            table = 'view_device'
            name = Required(str)
            filtered = Required(bool)

    def get_db(self):
        return self.db

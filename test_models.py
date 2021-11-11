
import unittest
import datetime

from models import PonyDB

from pony import orm

from config import database_info

class Models_Test(unittest.TestCase):

    def setUp(self):

        self.ponydb = PonyDB(database_info)

        self.ponydb.define_entities()
        self.ponydb.binddb()

        orm.db_session.__enter__()

    def tearDown(self):
        orm.rollback()
        orm.db_session.__exit__()

    def test__emptyDB(self):
        pass

    def test__timescaleDB(self):
        self.ponydb.timescale_tables()
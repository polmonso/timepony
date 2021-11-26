
import unittest
import datetime

from models import PonyManager

from pony import orm

from config import database_info

'''testing that a new connection on a different test class succeeds'''

class Models_TestAgain(unittest.TestCase):

    def setUp(self):

        self.pony = PonyManager(database_info)

        self.pony.define_entities()
        self.pony.binddb()

        orm.db_session.__enter__()

    def tearDown(self):
        orm.rollback()
        orm.db_session.__exit__()

    def test__emptyDB(self):
        pass

    def test__timescaleDB(self):
        self.pony.timescale_tables()

    def test__createEntity(self):

        self.pony.db.Device(name='roger')

        devices = orm.select(d.name for d in self.pony.db.Device)[:].to_list()
        self.assertListEqual(devices, ['roger'])
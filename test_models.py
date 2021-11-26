
import unittest
import datetime

from models import PonyManager

from pony import orm

from config import database_info

class Models_Test(unittest.TestCase):

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

class ModelSubset_Test(unittest.TestCase):


    def setUp(self):

        self.pony = PonyManager(database_info)

        self.pony.define_other_entities()
        self.pony.binddb()

        orm.db_session.__enter__()

    def tearDown(self):
        orm.rollback()
        orm.db_session.__exit__()


    def test__createSolarEntity(self):

        self.pony.db.Solar(name='pol')

        devices = orm.select(d.name for d in self.pony.db.Solar)[:].to_list()
        self.assertListEqual(devices, ['pol'])

class ModelCross_Test(unittest.TestCase):


    def setUp(self):

        self.pony = PonyManager(database_info)

        self.pony.define_crossed_entities()
        self.pony.binddb()

        orm.db_session.__enter__()

    def tearDown(self):
        orm.rollback()
        orm.db_session.__exit__()


    def test__createSolarEntity(self):

        t = datetime.datetime(year=2022,month=11,day=10, hour=7, minute=30, tzinfo=datetime.timezone.utc)

        d = self.pony.db.Device(name='alberto')
        self.pony.db.SolarDeviceEvent(time=t, device=d)

        events = orm.select((e.time, e.device.name) for e in self.pony.db.SolarDeviceEvent)[:].to_list()
        self.assertListEqual(events, [(t,'alberto')])


class ModelPersistence_Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        pony = PonyManager(database_info)

        pony.define_entities()
        pony.define_other_entities()
        pony.binddb()
        pony.db.drop_all_tables(with_all_data=True)

        pony_cross = PonyManager(database_info)
        pony_cross.define_crossed_entities()
        pony_cross.binddb()
        pony_cross.db.drop_all_tables(with_all_data=True)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test__simplebind(self):

        pony = PonyManager(database_info)

        pony.define_entities()
        pony.binddb()

        pony_other = PonyManager(database_info)

        pony_other.define_other_entities()
        pony_other.binddb()

        orm.db_session.__enter__()

        pony.db.Device(name='roger')
        orm.db_session.__exit__()


        orm.db_session.__enter__()

        pony_other.db.Solar(name='pol')
        orm.db_session.__exit__()

        print("drop all entities and other entities tables")
        pony.db.drop_all_tables(with_all_data=True)
        pony_other.db.drop_all_tables(with_all_data=True)

    def test__anothersession(self):

        pony_other = PonyManager(database_info)

        pony_other.define_other_entities()
        pony_other.binddb()

        orm.db_session.__enter__()

        pony_other.db.Solar(name='alberto')
        orm.db_session.__exit__()
        pony_other.db.drop_all_tables(with_all_data=True)

    '''
    Some discoveries regarding this test.

    You can define entities with missing Set() fields. This is useful to reuse, say, Device
    for both SolarDeviceEvents and Readings without having to declare Readings in the solar
    ponyManager db object.

    entities defined in one ponyManager object can't be used verbatim in another, the second
    must declare them again. This is probably caused by the fact that entities are defined
    via a inner class which is in different define_entities functions
    It can't be the same because the reverse relations are different to achieve encapsulation

    > pony_crossed.db.SolarDeviceEvent(time=t, device=d)
    > type(d)
    <class 'models.PonyManager.define_entities.<locals>.Device'>
    > dd = pony_crossed.db.Device.get(name='roger')
    > dd
    Device[1]
    > type(dd)
    <class 'models.PonyManager.define_crossed_entities.<locals>.Device'>
    '''
    def test__crossedbind(self):
        pony = PonyManager(database_info)

        pony.define_entities()
        pony.binddb()

        pony_other = PonyManager(database_info)

        pony_other.define_other_entities()
        pony_other.binddb()

        pony_crossed = PonyManager(database_info)

        pony_crossed.define_crossed_entities()
        pony_crossed.binddb()

        orm.db_session.__enter__()

        d = pony.db.Device(name='roger')
        t = datetime.datetime(year=2022,month=11,day=10, hour=7, minute=30, tzinfo=datetime.timezone.utc)
        r = pony.db.Reading(time=t, device=d)

        orm.db_session.__exit__()

        orm.db_session.__enter__()

        d = pony_crossed.db.Device.get(name='roger')
        pony_crossed.db.SolarDeviceEvent(time=t, device=d)
        orm.db_session.__exit__()

        pony.db.drop_all_tables(with_all_data=True)
        pony_other.db.drop_all_tables(with_all_data=True)
        pony_crossed.db.drop_all_tables(with_all_data=True)

    @unittest.skip('Pony ORM must support extending reverse relations after entity declaration')
    def test__crossedbind_with_common(self):
        pony = PonyManager(database_info)

        pony.define_common_entities()
        pony.define_reading_entity()
        pony.binddb()

        pony_crossed = PonyManager(database_info)

        pony_crossed.define_common_entities()
        pony_crossed.define_solarDeviceEvent()
        pony_crossed.binddb()

        orm.db_session.__enter__()

        d = pony.db.Device(name='roger')
        t = datetime.datetime(year=2022,month=11,day=10, hour=7, minute=30, tzinfo=datetime.timezone.utc)
        r = pony.db.Reading(time=t, device=d)

        orm.db_session.__exit__()

        orm.db_session.__enter__()

        # d = pony_crossed.db.Device.get(name='roger')
        pony_crossed.db.SolarDeviceEvent(time=t, device=d)
        orm.db_session.__exit__()

        pony.db.drop_all_tables(with_all_data=True)
        pony_crossed.db.drop_all_tables(with_all_data=True)
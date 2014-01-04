
from StringIO import StringIO
from mock import MagicMock
from twisted.internet import protocol, reactor
from twisted.protocols import policies
from zope.interface import implements

from tc.server import Server
from tc.equipment import IEquipment, ReferenceableEquipment
from tc.tests import TestCase, IOPump, connect


class DummyEquipment:
    implements(IEquipment)
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
    def start(s): pass
    def stop(s): pass


class TestReferenceableEquipmentRegistration(TestCase):
    def test_registration(self):
        server_orig = Server()
        client, server, pump = connect(server_orig)
        d = client.getRootObject()
        def gotRoot(root):
            # create equipment
            dummy = DummyEquipment('foo@a', 'CAMERA')
            dummy.start = MagicMock()
            dummy.stop = MagicMock()
            r = ReferenceableEquipment(dummy, root)
            r.start()
            pump.pump() # remote call "register"

            # it was inserted on server?
            self.assertTrue('foo@a' in server_orig.cameras)

            # create equipment with duplicated name
            r2 = ReferenceableEquipment(DummyEquipment('foo@a', 'SCREEN'), root)
            r2.start()
            pump.pump() # remote call "register"
            pump.pump() # DuplicatedName exception

            # reactor.stop called on duplicated equipment
            self.assertEqual(reactor.stop.call_count, 1)
            
            # stop working equipment
            r.stop()
            pump.pump() # remote call "purge"

            self.assertFalse('foo@a' in server_orig.cameras)
            self.assertEqual(reactor.stop.call_count, 2)
            self.assertTrue(dummy.start.called)
            self.assertTrue(dummy.stop.called)
        d.addCallback(gotRoot)
        return d
        

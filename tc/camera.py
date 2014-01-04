
from twisted.internet import protocol, reactor
from twisted.protocols import basic
from zope import interface

from tc.common import get_logger
from tc.video import Pipeline, StreamingWindow
from tc.equipment import IEquipment, ReferenceableEquipment


__ALL__ = ['CameraWindow', 'CameraProtocol', 'CameraProtocolFactory']

LOG = get_logger(__name__)


class CameraEquipment(StreamingWindow):
    interface.implements(IEquipment)

    kind = 'CAMERA'
    _description = """
        %s ! tee name=t
            t. ! queue ! x264enc tune=zerolatency ! rtph264pay
                ! multiudpsink name=hdsink
            t. ! queue ! x264enc tune=zerolatency ! rtph264pay
                ! multiudpsink name=ldsink
            t. ! queue ! autovideosink
    """

    def __init__(self, tkroot, source, name):
        pipe = Pipeline(self._description % source)
        title = '%s - tc-camera' % name
        self.name = name
        StreamingWindow.__init__(self, tkroot, pipe, title)

        # self.pipe.hdsink.sync = True
        self.pipe.hdsink.send_duplicates = False
    
    def addClient(self, addr, port):
        # FIXME untested
        self.pipe.hdsink.emit('add', addr, port)

    def delClient(self, addr, port):
        # FIXME untested
        # FIXME delClient "works" even if client wasn't previously added 
        self.pipe.hdsink.emit('remove', addr, port)


class ReferenceableCameraEquipment(ReferenceableEquipment):

    def remote_addClient(self, addr, port):
        self.thing.addClient(addr, port)

    def remote_delClient(self, addr, port):
        self.thing.delClient(addr, port)

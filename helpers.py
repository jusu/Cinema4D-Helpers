#
# helpers.py -- first simple helpers for Cinema4D
#

import c4d
import socket, time, threading

#
# Misc
#

def frame(doc):
    """Get current frame number."""
    return doc.GetTime().GetFrame(doc.GetFps())

#
# Keying
#

def vectorIds(id):
    """Get IDs for X, Y, Z components of a vector id. For example, XYZ of c4d.ID_BASEOBJECT_GLOBAL_POSITION"""
    x = c4d.DescID(c4d.DescLevel(id, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_X, c4d.DTYPE_REAL, 0))
    y = c4d.DescID(c4d.DescLevel(id, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_Y, c4d.DTYPE_REAL, 0))
    z = c4d.DescID(c4d.DescLevel(id, c4d.DTYPE_VECTOR, 0), c4d.DescLevel(c4d.VECTOR_Z, c4d.DTYPE_REAL, 0))

    return (x, y, z)

def CreateKey(op, id, value, forFrame = None):
    doc = op.GetDocument()
    if not doc: raise Exception, "object must be in a document"

    if forFrame == None:
        forFrame = frame(doc)

    # First check if the track type already exists, otherwise create it...
    track=op.FindCTrack(id)
    if not track:
        track=c4d.CTrack(op,id)
        op.InsertTrackSorted(track)

    curve=track.GetCurve()
    key=curve.AddKey(c4d.BaseTime(forFrame, doc.GetFps()))

    if type(value)==int or type(value)==float:
        key["key"].SetValue(curve,value)
    else:
        key["key"].SetGeData(curve,value)

def addFloatKey(op, id):
    CreateKey(op, id, op[id])

def addVectorKey(op, id):
    ids = vectorIds(id)
    v = op[id]

    CreateKey(op, ids[0], v.x)
    CreateKey(op, ids[1], v.y)
    CreateKey(op, ids[2], v.z)

def addKey(op, id):
    t = type(op[id])
    if t == int or t == float:
        addFloatKey(op, id)
    else:
        addVectorKey(op, id)

#
# Udp
#

class Script:
    def __init__(self, name):
        self.name = name

        nth = self.readNth()
        nth += 1
        self.initialValue = nth
        self.writeNth(nth)

    def writeNth(self, n):
        try:
            f = open("/tmp/_c4d_nth" + self.name, "w")
            f.write(str(n))
            f.close()
        except IOError:
            print "Failed to write nth."

    def readNth(self):
        try:
            f = open("/tmp/_c4d_nth" + self.name)
            n = int(f.readline())
            f.close()
            return n
        except IOError:
            return 0

    def IsCurrent(self):
        return self.initialValue == self.readNth()

class Udp:
    HOST = 'localhost'
    bufsize = 1024
    timeout = 0.5

    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((Udp.HOST, port))
        self.sock.settimeout(Udp.timeout)

    def read(self):
        try:
            data, addr = self.sock.recvfrom(Udp.bufsize)
        except socket.timeout:
            data = None
            pass
        
        return data

    def close(self):
        self.sock.close()

def listen(name, port, handlers):
    """Listen to udp port, handle data with 'handlers'
    (dictionary of prefix-function values).

    Name: unique string.
    """

    scr = Script(name)

    def task():
        # wait to release socket
        time.sleep(1)

        udp = Udp(port)

        while scr.IsCurrent():
            data = udp.read()
            if data:
                p = data.partition(' ')

                try:
                    handlers[p[0]](p[2])
                except KeyError:
                    pass

        udp.close()

    t = threading.Thread(target=task)
    t.start()

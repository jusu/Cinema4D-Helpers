Cinema4D-Helpers
================

Python helpers and examples for Cinema4D.

01 receiving network data
-------------------------

Receive data from an external program thru a UDP socket.

- Select the python tag on 'Platonic' and fix the sys.path.insert() path to helpers.py

- Press play on timeline

- Send some test data to UDP port 16000 using the Max example patch, or a program such as netcat:

        echo position 100 -100 100 | nc -u localhost 16000


02 adding keyframes from python
-------------------------------

Add keyframes easily with:

    helpers.addKey(op.GetObject(), c4d.ID_BASEOBJECT_REL_POSITION)


[![githalytics.com alpha](https://cruel-carlota.pagodabox.com/fb131a1b0b63771e180734b6d263eb97 "githalytics.com")](http://githalytics.com/jusu/Cinema4D-Helpers)

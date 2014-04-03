#!/usr/bin/env python
import serial, sys, time, os

class Heli(object):
    def __init__(self):
        path = [x for x in os.listdir('/dev')
                    if x.startswith('tty.usb')][0]
        path = '/dev/'+path
        self._s = serial.Serial(path, 9600)

        self.yaw = 63
        self.pitch = 63
        self.throttle = 0
        self.trim = 63

    def send(self):
        msg = [self.yaw, self.pitch, self.throttle, self.trim]
        self._s.write(msg)
        self._s.flush()
        print('sent {}'.format(msg))

    def land(self):
        for _ in range(3):
            self._s.write([63, 63, 0, 63])
            self._s.flush()
            time.sleep(0.01)
        sys.exit()

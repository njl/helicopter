#!/usr/bin/env python
import serial, sys, time, os
import logging
from threading import Thread, Condition

logging.basicConfig(format='%(asctime)s %(levelname)-6s %(name)s %(message)s', level=logging.DEBUG)

class Heli(object):

    def __init__(self,):
        self.__connection_up = False
        self.__available = Condition()
        self.initialize()

        path = next(
                    (
                        x
                        for x in os.listdir('/dev')
                        if x.startswith('ttyACM')
                    ),
                    None,
                    )

        if not path:
            raise ConnectionError("Could find and connect to the helicopter controller")

        path = '/dev/'+path
        self.__serial_connection = serial.Serial(path, 9600)
        self.__serial_connection.flushInput() # cleans up anything lingering

        ser = self.__serial_connection
        my_heli = self

        def f():
            while my_heli.__connection_up is False:
                try:
                    ser_bytes = ser.readline()
                    read_str = ser_bytes.decode('utf-8').strip()

                    if read_str == "READY":
                        with my_heli.__available:
                            my_heli.__connection_up = True
                            my_heli.__available.notify()
                except:
                    Heli.__LOGGER.warn("Error while working with the serial connection", exc_info=1)

                    with my_heli.__available:
                        my_heli.__connection_up = None
                        my_heli.__available.notify()

        t = Thread(target=f, daemon=True,)
        t.start()

    def is_ready(self):
        """
            Returns C{True} if this helicopter is ready for flight.

            @rtype: bool
        """
        with self.__available:
            if self.__connection_up is False:
                self.__available.wait()

        if self.__connection_up is None:
            Heli.__LOGGER.error("Connection failed.")
            return False

        assert self.__connection_up is True

        Heli.__LOGGER.info("Ready to go!")
        return True

    def send(self):
        """
            Sends the configured desired state of the helicopter to the remote controller.

            Waits for the helicopter to be ready for flight L{automatically<Heli.is_ready>}.
        """
        if not self.is_ready():
            Heli.__LOGGER.error("Cannot send desired state: no connection available.")
            return

        msg = [self.yaw, self.pitch, self.throttle, self.trim]
        written_bytes = self.__serial_connection.write(msg)

        assert written_bytes == len(msg)

        self.__serial_connection.flush()

        Heli.__LOGGER.debug("Sent %d %d %d %d", *msg)

        # this is to wait for the arduino to get it, we could implement an ACK
        time.sleep(0.5)

    def land(self):
        """
            Resets the state of the helicopter to the L{initial<Heli.initial>} state (i.e. crash lands).
        """
        self.initialize()
        self.send()

    def initialize(self,):
        """
            Configures the desired state of the helicopter to neutral and no gaz.
        """
        self.yaw, self.pitch, self.throttle, self.trim = 63, 63, 0, 63


    __LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    heli  = Heli()

    heli.throttle = 30

    heli.send()

    time.sleep(5) # 5s in the air

    heli.land()

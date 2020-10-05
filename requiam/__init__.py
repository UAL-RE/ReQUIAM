__version__ = "0.12.2"


class TimerClass(object):
    """
    Purpose:
      Define timer object that records elapsed time

    Initiate:
      timer = TimerClass()
      timer._start()

    Stop
      timer._stop()

    Get information:
      timer.format

    Attributes
    ----------
    start : datetime object
            Starting value for timer
    stop  : datetime object
            Stopping value for timer
    delta : datetime object
            Time difference
    """

    from datetime import datetime as dt

    def __init__(self):
        self.start = 0
        self.stop = 0
        self.delta = 0
        self.format = ""

    def _start(self):
        self.start = self.dt.now()

    def _stop(self):
        self.stop = self.dt.now()
        self.delta = self.stop - self.start
        sec = self.delta.seconds + self.delta.microseconds / 1e6
        HH = int(sec // 3600)
        MM = int((sec // 60) - (HH * 60))
        SS = sec - (HH * 3600) - (MM * 60)
        self.format = "Total time: {0: 02d} hours  {1: 02d} minutes  {2: .2f} seconds".format(HH, MM, SS)

__version__ = "0.16.4"

from typing import Union
from datetime import datetime


class TimerClass:
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

    def __init__(self):
        self.start: Union[int, datetime] = 0
        self.stop: Union[int, datetime] = 0
        self.delta: Union[int, datetime] = 0
        self.format: str = ""

    def _start(self) -> None:
        self.start = datetime.now()

    def _stop(self) -> None:
        self.stop = datetime.now()
        self.delta = self.stop - self.start
        sec = self.delta.seconds + self.delta.microseconds / 1e6
        HH = int(sec // 3600)
        MM = int((sec // 60) - (HH * 60))
        SS = sec - (HH * 3600) - (MM * 60)
        self.format = f"Total time: {HH: 02d} hours  {MM: 02d} minutes  {SS: .2f} seconds"

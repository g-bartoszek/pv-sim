import random
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
from typing import Generator


@dataclass
class Measurement:
    timestamp: float
    value: float


def meter_value() -> float:
    """ Value returned by mock power consumption meter, in Watts """
    return random.uniform(0, 9000)


def generate_measurements(start: datetime, end: datetime, interval: timedelta, realtime: bool) -> Generator[Measurement, None, None]:
    """ 
    Generate random measurements for given period
    :param start: Start of the period
    :param end: End of the period
    :param interval: Interval between measurements
    :param realtime: If true, there will be an actual interval (sleep) between measurements
    """

    if realtime:
        def wait():
            time.sleep(interval.total_seconds())
    else:
        def wait():
            pass

    current = start

    while current <= end:
        yield(Measurement(timestamp=current.timestamp(), value=meter_value()))
        current += interval
        wait()

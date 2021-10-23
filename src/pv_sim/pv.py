from dataclasses import dataclass
import dataclasses
from datetime import datetime
import json
import logging
from math import radians, sin, cos
import math
from typing import Callable

LOGGER = logging.getLogger('PV')


@dataclass
class Result:
    timestamp: float
    measurement_value: float
    pv_value: float
    sum: float

    def __eq__(self, o: object) -> bool:
        return self.timestamp == o.timestamp \
            and math.isclose(self.measurement_value, o.measurement_value) \
            and math.isclose(self.pv_value, o.pv_value) \
            and math.isclose(self.sum, o.sum)


def process_measurement(date: datetime, value: float) -> Result:
    """ Sum reported usage power with generated PV power and return all the values """
    value_kv = value / 1000
    value_pv = generate_power(date)

    sum = value_kv + value_pv

    return Result(timestamp=date.timestamp(), measurement_value=value_kv, pv_value=value_pv, sum=sum)


def generate_power(date: datetime) -> float:
    """
    Generate simulated power for given time of day, in kW

    Generated power is approximated using solar zenith angle for a given time of day
    Time of year is fixed
    Location related data is fixed

    All the constants were chosen experimentally to mimic the profile from the challenge description

    Sources:
    * https://sinovoltaics.com/learning-center/basics/calculation-of-solar-insolation/
    * https://en.wikipedia.org/wiki/Solar_zenith_angle
    """

    # Difference between standard time and local time (the sun peaks at 14:00)
    dif = -2

    # time of day as float
    time_of_day = date.hour + (date.minute / 60) + dif

    # Declination angle ranage -23.45 to to 23.45
    declination_angle = 4
    latitude = 51

    # hour angle = 15deg * (time - 12)
    hour_angle = 15 * (time_of_day - 12)

    # cos(zenith angle) = sin(latitude)sin(declination angle) + cos(latitude)cos(declination angle)cos(hour angle)
    cos_za = (sin(radians(latitude)) * sin(radians(declination_angle))) + (cos(
        radians(latitude)) * cos(radians(declination_angle)) * cos(radians(hour_angle)))

    # this constant encapsulates "solar constant=1000/W/m^2", area of the PV panel, its efficiency, and other factors
    MAGIC_CONSTANT = 4.9

    # If cos_za < 0 then it's night time
    power = 0 if cos_za < 0 else cos_za * MAGIC_CONSTANT

    LOGGER.debug(f"Date: {date} Time of day: {time_of_day} Power: {power}")
    print(f"Date: {date} Time of day: {time_of_day} Power: {power}")

    return power


def handle_message(body: str, output: Callable[[str], None]):
    """ 
    Handle single measurement and write result to the output 
    :param body: message body
    :param output: output function
    """
    try:
        measurement = json.loads(body)
        date = datetime.fromtimestamp(measurement['timestamp'])
        result = process_measurement(date, measurement['value'])
        LOGGER.debug(result)

        output(result)

    except Exception as e:
        LOGGER.error(e)

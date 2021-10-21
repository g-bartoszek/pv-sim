from datetime import datetime
from pv_sim.pv import Result, generate_power, process_measurement, handle_message
from math import isclose
from unittest.mock import Mock, call


def time(h, m):
    return datetime(1999, 1, 1, hour=h, minute=m)


def test_value_generation():
    """
    Check if generated values are more or less of similar shape
    to the ones provided as an example in the challenge description
    """

    e = 0.2

    assert isclose(generate_power(time(0, 0)), 0, abs_tol=e)
    assert isclose(generate_power(time(4, 0)), 0, abs_tol=e)
    assert isclose(generate_power(time(5, 30)), 0, abs_tol=e)
    assert isclose(generate_power(time(8, 00)), 0.3, abs_tol=e)
    assert isclose(generate_power(time(11, 00)), 2.5, abs_tol=e)
    assert isclose(generate_power(time(12, 00)), 2.8, abs_tol=e)
    assert isclose(generate_power(time(14, 00)), 3.5, abs_tol=e)
    assert isclose(generate_power(time(16, 00)), 3.0, abs_tol=e)
    assert isclose(generate_power(time(20, 00)), 0.1, abs_tol=e)
    assert isclose(generate_power(time(21, 00)), 0.0, abs_tol=e)
    assert isclose(generate_power(time(23, 59)), 0.0, abs_tol=e)


def test_measurement_processing():
    """ Should return a sum of received value in kW and PV power generated for the given time of day """
    date = time(14, 00)
    measurement_value = 4500
    pv_value = generate_power(date)

    expected_sum = 4.5 + pv_value

    assert Result(timestamp=date.timestamp(), measurement_value=4.5,
                  pv_value=pv_value, sum=expected_sum) == process_measurement(date, measurement_value)


def test_handling_message():
    """ Should write result to output """
    output = Mock()

    handle_message(
        """{"timestamp": 1602486950.0, "value": 0 }""", output)

    output.assert_called_once_with(
        Result(timestamp=1602486950.0, measurement_value=0.0,
               pv_value=1.2544323765509333, sum=1.2544323765509333))


def test_handling_invalid_message():
    """ Should not crash if incoming message is invalid """
    output = Mock()

    handle_message(
        """{"timestamp": 1602486950.0, "value": 7083.443651304828}""", output)
    handle_message(
        """{"timestamp": "I'M NOT A TAMSTAMP!", "value": 7083.443651304828}""", output)
    handle_message(
        """{"timestamp": 1602486950.0, "value": "I'M NOT A VALUE!"}""", output)
    handle_message("I'M NOT A JSON!", output)

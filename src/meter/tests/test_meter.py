from meter.meter import generate_measurements
from datetime import datetime, timedelta
from unittest.mock import patch


@patch('time.sleep')
def test_generate_measurements(sleep):
    measurements = generate_measurements(start=datetime(2020, 1, 29, 22, 00), end=datetime(
        2020, 1, 30, 2, 00), interval=timedelta(hours=1), realtime=False)

    result = [r for r in measurements]

    # Check dates
    assert result[0].timestamp == datetime(2020, 1, 29, 22, 00).timestamp()
    assert result[1].timestamp == datetime(2020, 1, 29, 23, 00).timestamp()
    assert result[2].timestamp == datetime(2020, 1, 30, 00, 00).timestamp()
    assert result[3].timestamp == datetime(2020, 1, 30, 1, 00).timestamp()
    assert result[4].timestamp == datetime(2020, 1, 30, 2, 00).timestamp()

    # Check values
    for m in result:
        assert m.value >= 0 and m.value <= 9000

    # Check no sleeps
    sleep.assert_not_called()


@patch('time.sleep')
def test_generate_measurements_with_sleep(sleep):
    interval = timedelta(hours=1)

    measurements = generate_measurements(start=datetime(2020, 1, 29, 22, 00), end=datetime(
        2020, 1, 30, 2, 00), interval=interval, realtime=True)

    next(measurements)
    sleep.assert_not_called()

    next(measurements)
    sleep.assert_called_once_with(interval.total_seconds())
    sleep.reset_mock()

    next(measurements)
    sleep.assert_called_once_with(interval.total_seconds())

import datetime as dt


class TimerError(Exception):
    """a custom exception for timer errors"""


class Timer(object):
    def __init__(self):
        self.start_time = dt.datetime(1970, 1, 1, 0, 0, 0)

    def reset(self):
        """

        :return: resets the timer to current time
        """
        self.start_time = dt.datetime.now()

    def check_difference(self):
        """

        :return: returns the time passed in seconds from the start of the timer
        """
        return (dt.datetime.now() - self.start_time).total_seconds()

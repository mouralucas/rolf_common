import datetime


def get_timestamp_aware():
    """
    Created by: Lucas Penha de Moura - 25/11/2024
        Return the UTC timestamp aware datetime object.
    """
    return datetime.datetime.now(datetime.timezone.utc)

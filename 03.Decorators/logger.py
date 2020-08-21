from functools import wraps


def logger(original_function):
    from os.path import basename
    import logging
    from datetime import datetime
    logging.basicConfig(filename=f'$${basename(__file__)}$$.log', level=logging.INFO)

    @wraps(original_function)
    def wrapper(*args, **kwargs):
        date, time = str(datetime.now()).split()
        logging.info(
            f'{original_function.__name__}, date: {date}, time: {time}, args: {args}, kwargs: {kwargs}'
        )
        return original_function(*args, **kwargs)

    return wrapper

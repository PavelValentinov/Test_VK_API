from functools import wraps


def logger(filename):
    """Декоратор, принимающий в себя путь к файлу с логами"""
    import os
    path = os.makedirs('LOGS', exist_ok=True)
    logfile = str(os.path.join('LOGS', filename))

    def _logger(original_function):
        """Декоратор, принимающий в себя логируемую функцию"""

        import logging
        from datetime import datetime
        logging.basicConfig(filename=logfile, level=logging.INFO)

        @wraps(original_function)
        def wrapper(*args, **kwargs):
            """Метод, логирующий вызовы функции"""

            date, time = str(datetime.now()).split()
            logging.info(
                f' func_name: {original_function.__name__}, date: {date}, time: {time}, args: {args}, kwargs: {kwargs}'
            )
            return original_function(*args, **kwargs)

        return wrapper

    return _logger

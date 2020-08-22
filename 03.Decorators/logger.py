from functools import wraps


def logger(filename):
    """Декоратор, принимающий в себя путь к файлу с логами"""
    import os
    os.makedirs('LOGS', exist_ok=True)
    logfile = str(os.path.join('LOGS', filename))

    def _logger(original_function):
        """Декоратор, принимающий в себя логируемую функцию"""

        import logging
        from datetime import datetime
        logging.basicConfig(filename=logfile, level=logging.INFO)

        @wraps(original_function)
        def wrapper(*args, **kwargs):
            """Метод, логирующий вызовы функции"""

            result = original_function(*args, **kwargs)
            date, time = str(datetime.now()).split()
            logging.info(
                f' func_name: {original_function.__name__}, '
                f'date: {date}, '
                f'time: {time}, '
                f'args: {args}, '
                f'kwargs: {kwargs}, '
                f'result: {result}'
            )
            return original_function(*args, **kwargs)

        return wrapper

    return _logger

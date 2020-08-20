from datetime import date

from application import salary
from application.db import people

if __name__ == '__main__':
    print(date.today())
    print(people.get_employees())
    print(salary.calculate_salary())

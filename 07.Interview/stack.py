"""Стек - абстрактный тип данных, представляющий собой список элементов, организованных по принципу
LIFO(англ.last in — first out, «последним пришёл — первым вышел»). Чаще всего принцип работы стека сравнивают
со стопкой тарелок: чтобы взять вторую сверху, нужно снять верхнюю. Или с магазином в огнестрельном оружии
(стрельба начнётся с патрона, заряженного последним).

1. Необходимо реализовать класс Stack со следующими методами:
    - isEmpty - проверка стека на пустоту. Метод возвращает True или False.
    - push - добавляет новый элемент на вершину стека. Метод ничего не возвращает.
    - pop - удаляет верхний элемент стека. Стек изменяется. Метод возвращает верхний элемент стека.
    - peek - возвращает верхний элемент стека, но не удаляет его. Стек не меняется.
    - size - возвращает количество элементов в стеке.

2. Используя стек из задания 1 необходимо решить задачу на проверку сбалансированности скобок.
Сбалансированность скобок означает, что каждый открывающий символ имеет соответствующий ему закрывающий, и пары
скобок правильно вложены друг в друга.

Сбалансированными последовательности будут следующие скобки:
    - (((([{}]))))
    - [([])((([[[]]])))]{()}
    - {{[()]}}

Несбалансированными последовательности:
    - }{}
    - {{[(])]}}
    - [[{())}]

Программа ожидает на вход строку с скобками. На выход сообщение "Сбалансированно", если строка корректная
и "Небалансированно", если строка составлена неверно."""

from typing import List, Dict


class Stack:
    PARENTHESES: Dict[str, str] = {
        '(': ')',
        '[': ']',
        '{': '}'
    }

    def __init__(self):
        self.stack: List[str] = list()

    def size(self) -> int:
        """Проверка текущего размера стека """
        return len(self.stack)

    def is_empty(self) -> bool:
        """Проверка стека на пустоту"""
        return self.size() == 0

    def push(self, elem: str) -> None:
        """Добавление нового элемента на стек """
        self.stack.append(elem)

    def pop(self) -> str:
        """Добавление последнего элемента со стека """
        return self.stack.pop()

    def peek(self) -> str:
        """Проверка последнего элемента на стеке"""
        if self.size():
            return self.stack[-1]

    def check(self, string: str) -> bool:
        """Проверка сбалансированности строк"""
        for elem in string:
            if elem in self.PARENTHESES.keys():
                self.push(elem)
            elif elem in self.PARENTHESES.values():
                if self.PARENTHESES.get(self.peek()) == elem:
                    self.pop()
                else:
                    return False
        if self.is_empty():
            return True
        return False


if __name__ == '__main__':
    lines: List[str] = [
        '(((([{}]))))',
        '[([])((([[[]]])))]{()}',
        '{{[()]}}',
        '}{}',
        '{{[(])]}}',
        '[[{())}]',
        '()()',
        '[{({[([[[[[[(((({{{{}}}}))))]]]]]])]})}]',
        '({(((())))})[{(([])([]))}][({})]',
        ')()',
        '())',
        '()(',
    ]

    for line in lines:
        stack = Stack()
        result = stack.check(line)
        if result:
            print(f"{line} - сбалансировано")
        else:
            print(f"{line} - не сбалансировано")

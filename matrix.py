import math
import copy
from typing import List, Callable, Optional

Matrix = List[List[int]]


class Customer:
    def __init__(self, name: str, items: int):
        self.name = name
        self.items = items
        self.next: Optional['Customer'] = None


class SupermarketQueue:
    def __init__(self):
        self.head: Optional[Customer] = None
        self.tail: Optional[Customer] = None
        self.size: int = 0

    def is_empty(self) -> bool:
        return self.head is None

    def enqueue(self, name: str, items: int) -> None:
        new_customer = Customer(name, items)

        if self.is_empty():
            self.head = new_customer
            self.tail = new_customer
        else:
            self.tail.next = new_customer
            self.tail = new_customer

        self.size += 1
        print(f"-> Покупець '{name}' з {items} товарами доданий до черги.")
        return None

    def dequeue(self) -> Optional[Customer]:
        if self.is_empty():
            return None

        served_customer = self.head
        self.head = self.head.next

        if self.head is None:
            self.tail = None

        self.size -= 1
        print(
            f"<- Покупець '{served_customer.name}' обслужений і покинув чергу.")
        return served_customer

    def peek(self) -> Optional[Customer]:
        return self.head

    def display(self) -> None:
        current = self.head
        if current is None:
            print("Черга порожня.")
            return None

        print(f"Покупці у черзі (Розмір: {self.size}):")

        line = "Каса -> "
        while current:
            line += f"[{current.name} ({current.items} т.)]"
            if current.next:
                line += " -> "
            current = current.next
        line += " <- Кінець Черги"
        print(line)
        return None


A: Matrix = [
    [34, -8, 27, 7, 12],
    [-5, 23, 45, 67, -2],
    [13, -12, 34, -3, 25],
    [17, 56, -6, 17, 21],
    [0, 15, 4, 9, -14],
]


def selection_sort_column(matrix: Matrix, col_index: int, comparison_func: Callable[[int, int], bool]) -> None:
    rows = len(matrix)
    if rows == 0:
        return None

    for i in range(rows - 1):
        best_row_index = i

        for j in range(i + 1, rows):
            if comparison_func(matrix[j][col_index], matrix[best_row_index][col_index]):
                best_row_index = j

        if best_row_index != i:
            matrix[i][col_index], matrix[best_row_index][col_index] = \
                matrix[best_row_index][col_index], matrix[i][col_index]

    return None


def sort_matrix_columns(matrix: Matrix, ascending: bool = True) -> Matrix:
    if not matrix:
        return []

    cols = len(matrix[0])

    comparison_func = (lambda a, b: a < b) if ascending else (
        lambda a, b: a > b)

    sorted_m = copy.deepcopy(matrix)

    for j in range(cols):
        selection_sort_column(sorted_m, j, comparison_func)

    return sorted_m


def calculate_row_sum(row: List[int]) -> int:
    return sum(row)


def calculate_geometric_mean(fi_values: List[int]) -> float:
    n = len(fi_values)
    if n == 0:
        return 0.0

    positive_fi = [val for val in fi_values if val > 0]

    if not positive_fi:
        return 0.0

    log_sum = sum(math.log(x) for x in positive_fi)

    geometric_mean = math.exp(log_sum / len(positive_fi))

    return geometric_mean


def main_part1() -> None:
    print("--- ЧАСТИНА 1: СОРТУВАННЯ МАТРИЦІ ТА ОБЧИСЛЕННЯ ФУНКЦІЙ ---")

    matrix_to_sort = copy.deepcopy(A)

    print("\n1. Оригінальна матриця A:")
    for row in matrix_to_sort:
        print(f"\t{row}")

    sorted_matrix = sort_matrix_columns(matrix_to_sort, ascending=True)

    print("\n2. Відсортована матриця (стовпці за зростанням, метод вибору):")
    for row in sorted_matrix:
        print(f"\t{row}")

    fi_values = [calculate_row_sum(row) for row in sorted_matrix]

    print("\n3. Значення fi(aij) (суми елементів рядків відсортованої матриці):")
    for i, val in enumerate(fi_values):
        print(f"\tРядок {i+1} (fi_{i+1}): {val}")

    F_value = calculate_geometric_mean(fi_values)

    print(f"\n4. Значення F(fi(aij)) (середнє геометричне fi(aij) для > 0):")
    print(f"\tF: {F_value:.4f}")

    return None


def main_part2() -> None:
    print("\n--- ЧАСТИНА 2: ЧЕРГА ПОКУПЦІВ (Однозв'язний Список) ---")

    cash_register = SupermarketQueue()

    print("\n[Прибуття покупців]:")
    cash_register.enqueue("Олена", 15)
    cash_register.enqueue("Ігор", 5)
    cash_register.enqueue("Марія", 22)

    cash_register.display()

    print("\n[Обслуговування]:")
    next_customer = cash_register.peek()
    if next_customer:
        print(f"Наступний на обслуговування: {next_customer.name}")

    cash_register.dequeue()
    cash_register.display()

    print("\n[Прибуття]:")
    cash_register.enqueue("Петро", 10)
    cash_register.display()

    print("\n[Обслуговування]:")
    cash_register.dequeue()
    cash_register.dequeue()
    cash_register.display()
    cash_register.dequeue()
    cash_register.display()

    return None


if __name__ == "__main__":
    main_part1()
    main_part2()

# Тестовые примеры
from parse_expense import parse_expense
test_cases = [
    "еда ведро картошки 500 рублей",
    "транспорт такси 1500",
    "быт хозтовары мыло 75 р",
    "эдл малако 80",
    "развлечения кино билет 350"
]

for test in test_cases:
    category, item, price = parse_expense(test)
    print(f"Ввод: {test}")
    print(f"Результат: ({category}, {item}, {price})\n")
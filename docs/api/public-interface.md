# Публичный интерфейс ядра

Пакет `packages.core` содержит функции, которые не зависят от GUI и SQLite.

Пакет описан в `pyproject.toml` как `furniture-store-core`, поэтому его можно установить локально:

```bash
python -m pip install -e .
```

Опубликованная версия в TestPyPI:

```text
https://test.pypi.org/project/furniture-store-core/0.1.0/
```

Установка из TestPyPI:

```bash
python -m pip install --index-url https://test.pypi.org/simple/ furniture-store-core==0.1.0
```

## Пример использования

```python
from packages.core import OrderLine, calculate_order_total

lines = [OrderLine(product_id=1, quantity=2, unit_price=15000)]
total = calculate_order_total(lines)
print(total)
```

## `OrderLine`

Описывает строку заказа:

- `product_id`
- `quantity`
- `unit_price`

## `calculate_order_total(lines)`

Проверяет строки заказа и возвращает итоговую сумму с округлением до двух знаков.

Ошибки:
- пустой заказ;
- неположительный `product_id`;
- неположительное количество;
- отрицательная цена.

## `count_product_in_lines(lines, product_id)`

Возвращает суммарное количество товара, если один и тот же товар уже добавлен в заказ несколько раз.

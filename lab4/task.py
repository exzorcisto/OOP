# Задание 1: Обработка исключений

class BaseError(Exception):
    """Базовый класс для пользовательских исключений."""
    pass


class CustomError(BaseError):
    """Пользовательское исключение."""
    pass


class SpecificError(CustomError):
    """Специфическое пользовательское исключение."""
    pass


def divide(x, y):
    """Делит x на y, обрабатывая возможные исключения."""
    try:
        if y == 0:
            raise ZeroDivisionError("Деление на ноль!")
        if x < 0 or y < 0:
            raise CustomError("Оба числа должны быть неотрицательными")
        result = x / y
        return result
    except ZeroDivisionError as e:
        print(f"Произошла ошибка деления на ноль: {e}")
        return None
    except CustomError as e:
        print(f"Произошла пользовательская ошибка: {e}")
        return None
    except Exception as e:
        print(f"Произошла неожиданная ошибка: {e}")
        return None
    finally:
        print("Блок finally выполнен.")


# Задание 2: Работа с массивами объектов

class Item:
    """Предмет с названием и значением."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"Item(name='{self.name}', value={self.value})"

    def __repr__(self):
        return f"Item('{self.name}', {self.value})"


def find_max_value_item(matrix):
    """Находит объект с максимальным значением в двумерном списке."""
    if not matrix:
        return None

    max_item = None
    for row in matrix:
        for item in row:
            if max_item is None or item.value > max_item.value:
                max_item = item
    return max_item


# Задание 3: Наследование

class Animal:
    """Базовый класс для животных."""

    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Звук животного"

    def describe(self):
        return f"Это животное по имени {self.name}."


class Dog(Animal):
    """Производный класс для собак."""

    def __init__(self, name, breed):
        super().__init__(name)
        self.breed = breed

    def speak(self):
        return "Гав!"

    def describe(self):
        return f"Это {self.breed} по имени {self.name}. " + super().describe()

    def describe_with_conditional_calling(self, condition):
        if condition:
            return super().describe() + f" И он говорит: {self.speak()}"
        else:
            return f"Он говорит: {self.speak()} " + super().describe()

# Задание 4: Защищенные атрибуты

class Car:
    """Класс для автомобилей с защищенными атрибутами."""

    def __init__(self, make, model, _max_speed):
        self.make = make
        self.model = model
        self._max_speed = _max_speed  # Защищенный атрибут


class SportsCar(Car):
    """Производный класс для спортивных автомобилей."""

    def __init__(self, make, model, _max_speed, horsepower):
        super().__init__(make, model, _max_speed)
        self.horsepower = horsepower

    def get_max_speed(self):
        return self._max_speed  # Доступ к защищенному атрибуту


# Задание 5: Конструкторы и наследование (уже реализовано в Dog и SportsCar)

# Задание 6: Строковое представление (уже реализовано в Item)


if __name__ == '__main__':
    # Задание 1
    print("Задание 1:")
    print(divide(10, 2))
    print(divide(10, 0))
    print(divide(-5, 2))
    print(divide(5, 2))

    # Задание 2
    print("\nЗадание 2:")
    item1 = Item("Яблоко", 10)
    item2 = Item("Банан", 20)
    item3 = Item("Апельсин", 15)
    item4 = Item("Груша", 25)

    matrix = [
        [item1, item2],
        [item3, item4]
    ]
    max_item = find_max_value_item(matrix)
    if max_item:
        print(f"Объект с максимальным значением: {max_item}")
    else:
        print("Список пуст.")

    # Задание 3
    print("\nЗадание 3:")
    animal = Animal("Общее животное")
    dog = Dog("Бобик", "Дворняга")

    print(animal.speak())
    print(dog.speak())
    print(dog.describe())
    print(dog.describe_with_conditional_calling(True))
    print(dog.describe_with_conditional_calling(False))

    # Задание 4
    print("\nЗадание 4:")
    car = Car("Toyota", "Camry", 200)
    sports_car = SportsCar("Ferrari", "488", 330, 660)
    print(f"Максимальная скорость {sports_car.make} {sports_car.model}: {sports_car.get_max_speed()}")

    # Задание 6
    print("\nЗадание 6:")
    item5 = Item("Вишня", 30)
    print(f"Строковое представление: {str(item5)}")
    print(f"Представление для воссоздания: {repr(item5)}")
    #  Попробуем воссоздать объект через eval
    item6 = eval(repr(item5))
    print(f"Воссозданный объект: {item6}")
    print(item5 == item6)  # Сравнивает объекты по идентичности, а не по значению атрибутов
    print(item5.__dict__ == item6.__dict__) # Сравнивает по значениям атрибутов

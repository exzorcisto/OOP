
import sqlite3
from datetime import date
import os
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

# Custom Exceptions
class BaseError(Exception):
    """Base class for custom exceptions."""
    pass

class DatabaseError(BaseError):
    """Exception raised for database-related errors."""
    pass

class InvalidInputError(BaseError):
    """Exception raised for invalid input."""
    pass

class DataNotFoundError(BaseError):
    """Exception raised when data is not found."""
    pass


@dataclass
class City:
    pk_city: int
    name: str

    def __str__(self):
        return f"City(pk_city={self.pk_city}, name='{self.name}')"

    def __eq__(self, other):
        if isinstance(other, City):
            return self.pk_city == other.pk_city and self.name == other.name
        return False


@dataclass
class AutoMarket:
    pk_automarket: int
    name: str
    fk_city: int

    def __str__(self):
        return f"AutoMarket(pk_automarket={self.pk_automarket}, name='{self.name}', fk_city={self.fk_city})"

    def __eq__(self, other):
        if isinstance(other, AutoMarket):
            return (self.pk_automarket == other.pk_automarket and
                    self.name == other.name and
                    self.fk_city == other.fk_city)
        return False


@dataclass
class Auto:
    pk_auto: int
    name: str
    fk_automarket: int
    price: float
    year_of_release: date

    def __str__(self):
        return f"{self.pk_auto}. {self.name}, Автосалон - {self.fk_automarket}, {self.price}, {self.year_of_release}"

    def __eq__(self, other):
        if isinstance(other, Auto):
            return (self.pk_auto == other.pk_auto and
                    self.name == other.name and
                    self.fk_automarket == other.fk_automarket and
                    self.price == other.price and
                    self.year_of_release == other.year_of_release)
        return False

    def __lt__(self, other):
        if isinstance(other, Auto):
            return self.price < other.price
        return NotImplemented


class AbstractAutoSells(ABC):
    @abstractmethod
    def add_city(self, city: City):
        pass

    @abstractmethod
    def add_automarket(self, automarket: AutoMarket):
        pass

    @abstractmethod
    def add_auto(self, auto: Auto):
        pass

    @abstractmethod
    def find_autos_by_city(self, city_name: str):
        pass

    @abstractmethod
    def find_autos_by_price_range(self, min_price: float, max_price: float):
        pass

    @abstractmethod
    def find_autos_by_automarket(self, automarket_name: str):
        pass

    @abstractmethod
    def find_autos_by_year(self, year: int):
        pass

    @abstractmethod
    def list_all_autos(self):
        pass

    @abstractmethod
    def list_all_automarkets(self):
        pass

    @abstractmethod
    def list_all_cities(self):
        pass

    @abstractmethod
    def menu(self):
        pass


class AutoSells(AbstractAutoSells):

    _instance = None  # Static field to hold the singleton instance
    DATABASE_VERSION = 1.0  # Static field for database version

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


    def __init__(self, db_path="autosells.db"): # Changed extension to .db
        if hasattr(self, '_is_initialized'):
            return  # Prevent re-initialization
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(self.db_path)  # Connect to SQLite database
            self.cursor = self.conn.cursor()  # Create a cursor object
            self._create_tables() # Creates Tables.

            self.cities: Dict[int, City] = {}
            self.automarkets: Dict[int, AutoMarket] = {}
            self.autos: Dict[int, Auto] = {}
            self._load_data() # Load data from the database into the dictionaries

            self._is_initialized = True
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database: {e}")
        finally:
            # Ensure cursor exists even if connection fails
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            # No need to close connection here, as it might not be established

    def _load_data(self):
        """Loads data from the database into the dictionaries."""
        try:
            self.cities = self._load_cities()
            self.automarkets = self._load_automarkets()
            self.autos = self._load_autos()
        except DatabaseError as e:
            print(f"Error loading data: {e}")


    def _load_cities(self):
        try:
            self.cursor.execute("SELECT pk_city, name FROM Cities")
            rows = self.cursor.fetchall()
            return {row[0]: City(pk_city=row[0], name=row[1]) for row in rows}
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to load cities: {e}")

    def _load_automarkets(self):
        try:
            self.cursor.execute("SELECT pk_automarket, name, fk_city FROM AutoMarkets")
            rows = self.cursor.fetchall()
            return {row[0]: AutoMarket(pk_automarket=row[0], name=row[1], fk_city=row[2]) for row in rows}
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to load automarkets: {e}")

    def _load_autos(self):
        try:
            self.cursor.execute("SELECT pk_auto, name, fk_automarket, price, year_of_release FROM Autos")
            rows = self.cursor.fetchall()
            return {row[0]: Auto(pk_auto=row[0], name=row[1], fk_automarket=row[2], price=row[3], year_of_release=date.fromisoformat(row[4])) for row in rows}
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to load autos: {e}")
        except ValueError as e:
            raise DatabaseError(f"Failed to parse date: {e}")


    def _create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Cities (
                    pk_city INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS AutoMarkets (
                    pk_automarket INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    fk_city INTEGER NOT NULL,
                    FOREIGN KEY (fk_city) REFERENCES Cities (pk_city)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS Autos (
                    pk_auto INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    fk_automarket INTEGER NOT NULL,
                    price REAL NOT NULL,
                    year_of_release TEXT NOT NULL,  -- Store date as TEXT (ISO format)
                    FOREIGN KEY (fk_automarket) REFERENCES AutoMarkets (pk_automarket)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create tables: {e}")

    def _check_if_exists(self, table_name: str, pk_column: str, pk_value):
        try:
            self.cursor.execute(f"SELECT 1 FROM {table_name} WHERE {pk_column} = ?", (pk_value,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to check if exists: {e}")

    def add_city(self, city: City):
        if not self._check_if_exists("Cities", "pk_city", city.pk_city):
            try:
                self.cursor.execute("INSERT INTO Cities (pk_city, name) VALUES (?, ?)",
                                    (city.pk_city, city.name))
                self.conn.commit()
                self.cities[city.pk_city] = city  # Add to the dictionary
            except sqlite3.Error as e:
                raise DatabaseError(f"Database error: {e}")
        else:
            print(f"City with pk_city {city.pk_city} already exists.")

    def add_automarket(self, automarket: AutoMarket):
        if not self._check_if_exists("AutoMarkets", "pk_automarket", automarket.pk_automarket):
            try:
                self.cursor.execute("INSERT INTO AutoMarkets (pk_automarket, name, fk_city) VALUES (?, ?, ?)",
                                    (automarket.pk_automarket, automarket.name, automarket.fk_city))
                self.conn.commit()
                self.automarkets[automarket.pk_automarket] = automarket  # Add to the dictionary
            except sqlite3.Error as e:
                raise DatabaseError(f"Database error: {e}")
        else:
            print(f"AutoMarket with pk_automarket {automarket.pk_automarket} already exists.")


    def add_auto(self, auto: Auto):
        if not self._check_if_exists("Autos", "pk_auto", auto.pk_auto):
            try:
                self.cursor.execute("INSERT INTO Autos (pk_auto, name, fk_automarket, price, year_of_release) VALUES (?, ?, ?, ?, ?)",
                                    (auto.pk_auto, auto.name, auto.fk_automarket, auto.price, auto.year_of_release.isoformat()))  # Store date as ISO format string
                self.conn.commit()
                self.autos[auto.pk_auto] = auto  # Add to the dictionary
            except sqlite3.Error as e:
                raise DatabaseError(f"Database error: {e}")
        else:
            print(f"Auto with pk_auto {auto.pk_auto} already exists.")

    def find_autos_by_city(self, city_name: str) -> List[Auto]:
        result: List[Auto] = []
        for auto_id, auto in self.autos.items():
            automarket: Optional[AutoMarket] = self.automarkets.get(auto.fk_automarket)
            if automarket:
                city: Optional[City] = self.cities.get(automarket.fk_city)
                if city and city.name.lower() == city_name.lower():
                    result.append(auto)
        if not result:
            raise DataNotFoundError(f"No autos found in city {city_name}")
        return result

    def find_autos_by_price_range(self, min_price: float, max_price: float) -> List[Auto]:
         # Input validation
        if not isinstance(min_price, (int, float)) or not isinstance(max_price, (int, float)):
            raise InvalidInputError("Price must be a number.")
        if min_price > max_price:
            raise InvalidInputError("Min price cannot be greater than max price.")
        result = [auto for auto_id, auto in self.autos.items() if min_price <= auto.price <= max_price]
        if not result:
            raise DataNotFoundError(f"No autos found in the price range from {min_price} to {max_price}")
        return result

    def find_autos_by_automarket(self, automarket_name: str) -> List[Auto]:
        result: List[Auto] = []
        for auto_id, auto in self.autos.items():
            automarket: Optional[AutoMarket] = next((am for am_id, am in self.automarkets.items() if am.pk_automarket == auto.fk_automarket), None)
            if automarket and automarket.name.lower() == automarket_name.lower():
                result.append(auto)

        if not result:
            raise DataNotFoundError(f"No autos found in the automarket {automarket_name}")
        return result

    def find_autos_by_year(self, year: int) -> List[Auto]:
        if not isinstance(year, int):
            raise InvalidInputError("Year must be an integer.")

        result = [auto for auto_id, auto in self.autos.items() if auto.year_of_release.year == year]

        if not result:
             raise DataNotFoundError(f"No autos found in the year {year}")
        return result

    def list_all_autos(self) -> List[str]:
        if not self.autos:
            raise DataNotFoundError("No autos found in the database.")
        return [str(auto) for auto_id, auto in self.autos.items()]

    def list_all_automarkets(self) -> List[str]:
        if not self.automarkets:
            raise DataNotFoundError("No automarkets found in the database.")
        return [str(automarket) for automarket_id, automarket in self.automarkets.items()]

    def list_all_cities(self) -> List[str]:
        if not self.cities:
            raise DataNotFoundError("No cities found in the database.")
        return [str(city) for city_id, city in self.cities.items()]

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def scip(self):
        input("\nНажмите Enter чтобы выйти")

    def menu(self):
        while True:
            self.clear_console()
            print("\nМеню AutoSells:")
            print("1. Поиск автомобилей по городу")
            print("2. Поиск автомобилей по диапазону цен")
            print("3. Поиск автомобилей по автосалону")
            print("4. Поиск автомобилей по году выпуска")
            print("5. Список всех автомобилей")
            print("6. Список всех автосалонов")
            print("7. Список всех городов")
            print("8. Вывести всю базу данных")
            print("9. Сравнить два автомобиля по цене")
            print("0. Выход")

            choice = input("Выберите опцию: ")

            if choice == '1':
                self.clear_console()
                try:
                    city_name = input("Введите название города: ")
                    autos = self.find_autos_by_city(city_name)
                    print(f"Автомобили в городе {city_name}:")
                    for auto in autos:
                        print(auto)
                except DataNotFoundError as e:
                    print(e)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '2':
                self.clear_console()
                try:
                    min_price = float(input("Введите минимальную цену: "))
                    max_price = float(input("Введите максимальную цену: "))
                    autos = self.find_autos_by_price_range(min_price, max_price)
                    print(f"Автомобили в диапазоне цен от {min_price} до {max_price}:")
                    for auto in autos:
                        print(auto)
                except InvalidInputError as e:
                    print(e)
                except DataNotFoundError as e:
                    print(e)
                except ValueError:
                    print("Неверный ввод цены. Пожалуйста, введите число.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '3':
                self.clear_console()
                try:
                    automarket_name = input("Введите название автосалона: ")
                    autos = self.find_autos_by_automarket(automarket_name)
                    print(f"Автомобили в автосалоне {automarket_name}:")
                    for auto in autos:
                        print(auto)
                except DataNotFoundError as e:
                    print(e)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '4':
                self.clear_console()
                try:
                    year = int(input("Введите год выпуска: "))
                    autos = self.find_autos_by_year(year)
                    print(f"Автомобили {year} года выпуска:")
                    for auto in autos:
                        print(auto)
                except InvalidInputError as e:
                    print(e)
                except DataNotFoundError as e:
                    print(e)
                except ValueError:
                    print("Неверный ввод года. Пожалуйста, введите целое число.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '5':
                self.clear_console()
                try:
                    autos = self.list_all_autos()
                    print("Все автомобили:")
                    for auto in autos:
                        print(auto)
                except DataNotFoundError as e:
                    print(e)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '6':
                self.clear_console()
                try:
                    automarkets = self.list_all_automarkets()
                    print("Все автосалоны:")
                    for automarket in automarkets:
                        print(automarket)
                except DataNotFoundError as e:
                    print(e)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '7':
                self.clear_console()
                try:
                    cities = self.list_all_cities()
                    print("Все города:")
                    for city in cities:
                        print(city)
                except DataNotFoundError as e:
                    print(e)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '8': # Displays data from db
                try:
                    print("Cities:")
                    for city in self.list_all_cities():
                        print(city)

                    print("\nAutomarkets:")
                    for automarket in self.list_all_automarkets():
                        print(automarket)

                    print("\nAutos:")
                    for auto in self.list_all_autos():
                        print(auto)
                except DataNotFoundError as e:
                    print(e)
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '9':
                self.clear_console()
                try:
                    auto_id1 = int(input("Введите ID первого автомобиля для сравнения: "))
                    auto1: Optional[Auto] = self.autos.get(auto_id1)
                    auto_id2 = int(input("Введите ID второго автомобиля для сравнения: "))
                    auto2: Optional[Auto] = self.autos.get(auto_id2)

                    if auto1 and auto2:
                        if auto1 < auto2:
                            print(f"{auto1.name} дешевле, чем {auto2.name}")
                        elif auto2 < auto1:
                            print(f"{auto2.name} дешевле, чем {auto1.name}")
                        else:
                            print(f"{auto1.name} и {auto2.name} стоят одинаково")
                    else:
                        print("Один или оба автомобиля не найдены.")
                except ValueError:
                    print("Неверный ввод ID автомобиля. Пожалуйста, введите число.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                finally:
                    self.scip()

            elif choice == '0':
                break

            else:
                print("Неверный выбор. Попробуйте снова.")
                self.scip()

    def __str__(self):
        return f"AutoSells(cities={self.cities}, automarkets={self.automarkets}, autos={self.autos})"

    def __del__(self):  # Close the connection when the object is deleted
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                print(f"Error closing database connection: {e}")

    @staticmethod
    def get_database_version():
        return AutoSells.DATABASE_VERSION

    @staticmethod
    def print_database_version():
        print(f"Database Version: {AutoSells.DATABASE_VERSION}")

# Example usage:
if __name__ == '__main__':
    try:
        auto_sells = AutoSells()
        auto_sells.menu()

    except DatabaseError as e:
        print(f"A database error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during initialization: {e}")

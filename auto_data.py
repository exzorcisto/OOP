
import sqlite3
from datetime import date
import os
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List

@dataclass
class City:
    pk_city: int
    name: str

    def __str__(self):
        return f"City(pk_city={self.pk_city}, name='{self.name}')"


@dataclass
class AutoMarket:
    pk_automarket: int
    name: str
    fk_city: int

    def __str__(self):
        return f"AutoMarket(pk_automarket={self.pk_automarket}, name='{self.name}', fk_city={self.fk_city})"


@dataclass
class Auto:
    pk_auto: int
    name: str
    fk_automarket: int
    price: float
    year_of_release: date

    def __str__(self):
        return f"{self.pk_auto}. {self.name}, Автосалон - {self.fk_automarket}, {self.price}, {self.year_of_release}"


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
        self.conn = sqlite3.connect(self.db_path)  # Connect to SQLite database
        self.cursor = self.conn.cursor()  # Create a cursor object
        self._create_tables() # Creates Tables.

        self.cities: List[City] = []
        self.automarkets: List[AutoMarket] = []
        self.autos: List[Auto] = []
        self._load_data() # Load data from the database into the lists

        self._is_initialized = True


    def _load_data(self):
        """Loads data from the database into the lists."""
        self.cities = self._load_cities()
        self.automarkets = self._load_automarkets()
        self.autos = self._load_autos()

    def _load_cities(self):
        self.cursor.execute("SELECT pk_city, name FROM Cities")
        rows = self.cursor.fetchall()
        return [City(pk_city=row[0], name=row[1]) for row in rows]

    def _load_automarkets(self):
        self.cursor.execute("SELECT pk_automarket, name, fk_city FROM AutoMarkets")
        rows = self.cursor.fetchall()
        return [AutoMarket(pk_automarket=row[0], name=row[1], fk_city=row[2]) for row in rows]

    def _load_autos(self):
        self.cursor.execute("SELECT pk_auto, name, fk_automarket, price, year_of_release FROM Autos")
        rows = self.cursor.fetchall()
        return [Auto(pk_auto=row[0], name=row[1], fk_automarket=row[2], price=row[3], year_of_release=date.fromisoformat(row[4])) for row in rows]


    def _create_tables(self):
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

    def _check_if_exists(self, table_name: str, pk_column: str, pk_value):
        self.cursor.execute(f"SELECT 1 FROM {table_name} WHERE {pk_column} = ?", (pk_value,))
        return self.cursor.fetchone() is not None

    def add_city(self, city: City):
        if not self._check_if_exists("Cities", "pk_city", city.pk_city):
            self.cursor.execute("INSERT INTO Cities (pk_city, name) VALUES (?, ?)",
                                (city.pk_city, city.name))
            self.conn.commit()
            self.cities.append(city)  # Add to the list

    def add_automarket(self, automarket: AutoMarket):
        if not self._check_if_exists("AutoMarkets", "pk_automarket", automarket.pk_automarket):
            self.cursor.execute("INSERT INTO AutoMarkets (pk_automarket, name, fk_city) VALUES (?, ?, ?)",
                                (automarket.pk_automarket, automarket.name, automarket.fk_city))
            self.conn.commit()
            self.automarkets.append(automarket)  # Add to the list


    def add_auto(self, auto: Auto):
        if not self._check_if_exists("Autos", "pk_auto", auto.pk_auto):
            self.cursor.execute("INSERT INTO Autos (pk_auto, name, fk_automarket, price, year_of_release) VALUES (?, ?, ?, ?, ?)",
                                (auto.pk_auto, auto.name, auto.fk_automarket, auto.price, auto.year_of_release.isoformat()))  # Store date as ISO format string
            self.conn.commit()
            self.autos.append(auto)  # Add to the list

    def find_autos_by_city(self, city_name: str):
        result: List[Auto] = []
        for auto in self.autos:
            automarket = next((am for am in self.automarkets if am.pk_automarket == auto.fk_automarket), None)
            if automarket:
                city = next((c for c in self.cities if c.pk_city == automarket.fk_city), None)
                if city and city.name == city_name:
                    result.append(auto)
        return result

    def find_autos_by_price_range(self, min_price: float, max_price: float):
        return [auto for auto in self.autos if min_price <= auto.price <= max_price]

    def find_autos_by_automarket(self, automarket_name: str):
         result: List[Auto] = []
         for auto in self.autos:
            automarket = next((am for am in self.automarkets if am.pk_automarket == auto.fk_automarket), None)
            if automarket and automarket.name == automarket_name:
                result.append(auto)
         return result

    def find_autos_by_year(self, year: int):
        return [auto for auto in self.autos if auto.year_of_release.year == year]

    def list_all_autos(self):
        return [str(auto) for auto in self.autos]

    def list_all_automarkets(self):
        return [str(automarket) for automarket in self.automarkets]

    def list_all_cities(self):
        return [str(city) for city in self.cities]

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
            print("0. Выход")

            choice = input("Выберите опцию: ")

            if choice == '1':
                self.clear_console()
                city_name = input("Введите название города: ")
                autos = self.find_autos_by_city(city_name)
                if autos:
                    print(f"Автомобили в городе {city_name}:")
                    for auto in autos:
                        print(auto)
                else:
                    print(f"Нет автомобилей в городе {city_name}.")

                self.scip()

            elif choice == '2':
                self.clear_console()
                min_price = float(input("Введите минимальную цену: "))
                max_price = float(input("Введите максимальную цену: "))
                autos = self.find_autos_by_price_range(min_price, max_price)
                if autos:
                    print(f"Автомобили в диапазоне цен от {min_price} до {max_price}:")
                    for auto in autos:
                        print(auto)
                else:
                    print(f"Нет автомобилей в диапазоне цен от {min_price} до {max_price}.")

                self.scip()

            elif choice == '3':
                self.clear_console()
                automarket_name = input("Введите название автосалона: ")
                autos = self.find_autos_by_automarket(automarket_name)
                if autos:
                    print(f"Автомобили в автосалоне {automarket_name}:")
                    for auto in autos:
                        print(auto)
                else:
                    print(f"Нет автомобилей в автосалоне {automarket_name}.")

                self.scip()

            elif choice == '4':
                self.clear_console()
                year = int(input("Введите год выпуска: "))
                autos = self.find_autos_by_year(year)
                if autos:
                    print(f"Автомобили {year} года выпуска:")
                    for auto in autos:
                        print(auto)
                else:
                    print(f"Нет автомобилей {year} года выпуска.")

                self.scip()

            elif choice == '5':
                self.clear_console()
                autos = self.list_all_autos()
                if autos:
                    print("Все автомобили:")
                    for auto in autos:
                        print(auto)
                else:
                    print("Нет автомобилей в базе данных.")

                self.scip()

            elif choice == '6':
                self.clear_console()
                automarkets = self.list_all_automarkets()
                if automarkets:
                    print("Все автосалоны:")
                    for automarket in automarkets:
                        print(automarket)
                else:
                    print("Нет автосалонов в базе данных.")

                self.scip()

            elif choice == '7':
                self.clear_console()
                cities = self.list_all_cities()
                if cities:
                    print("Все города:")
                    for city in cities:
                        print(city)
                else:
                    print("Нет городов в базе данных.")

                self.scip()

            elif choice == '8': # Displays data from db
                print("Cities:")
                for city in self.list_all_cities():
                    print(city)

                print("\nAutomarkets:")
                for automarket in self.list_all_automarkets():
                    print(automarket)

                print("\nAutos:")
                for auto in self.list_all_autos():
                    print(auto)
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
            self.conn.close()

    @staticmethod
    def get_database_version():
        return AutoSells.DATABASE_VERSION

    @staticmethod
    def print_database_version():
        print(f"Database Version: {AutoSells.DATABASE_VERSION}")

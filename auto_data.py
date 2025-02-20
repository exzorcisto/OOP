
import sqlite3
from datetime import date
import os
from dataclasses import dataclass


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


class AutoSells:
    def __init__(self, db_path="autosells.db"): # Changed extension to .db
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)  # Connect to SQLite database
        self.cursor = self.conn.cursor()  # Create a cursor object
        self._create_tables() # Creates Tables.
        # Removed json loading/saving logic

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

    def add_automarket(self, automarket: AutoMarket):
        if not self._check_if_exists("AutoMarkets", "pk_automarket", automarket.pk_automarket):
            self.cursor.execute("INSERT INTO AutoMarkets (pk_automarket, name, fk_city) VALUES (?, ?, ?)",
                                (automarket.pk_automarket, automarket.name, automarket.fk_city))
            self.conn.commit()

    def add_auto(self, auto: Auto):
        if not self._check_if_exists("Autos", "pk_auto", auto.pk_auto):
            self.cursor.execute("INSERT INTO Autos (pk_auto, name, fk_automarket, price, year_of_release) VALUES (?, ?, ?, ?, ?)",
                                (auto.pk_auto, auto.name, auto.fk_automarket, auto.price, auto.year_of_release.isoformat()))  # Store date as ISO format string
            self.conn.commit()

    def find_autos_by_city(self, city_name: str):
        self.cursor.execute("""
            SELECT Autos.pk_auto, Autos.name, Autos.fk_automarket, Autos.price, Autos.year_of_release
            FROM Autos
            JOIN AutoMarkets ON Autos.fk_automarket = AutoMarkets.pk_automarket
            JOIN Cities ON AutoMarkets.fk_city = Cities.pk_city
            WHERE Cities.name = ?
        """, (city_name,))
        rows = self.cursor.fetchall()
        return [Auto(pk_auto=row[0], name=row[1], fk_automarket=row[2], price=row[3],
                     year_of_release=date.fromisoformat(row[4])) for row in rows]

    def find_autos_by_price_range(self, min_price: float, max_price: float):
        self.cursor.execute("""
            SELECT pk_auto, name, fk_automarket, price, year_of_release
            FROM Autos
            WHERE price BETWEEN ? AND ?
        """, (min_price, max_price))
        rows = self.cursor.fetchall()
        return [Auto(pk_auto=row[0], name=row[1], fk_automarket=row[2], price=row[3],
                     year_of_release=date.fromisoformat(row[4])) for row in rows]

    def find_autos_by_automarket(self, automarket_name: str):
        self.cursor.execute("""
            SELECT Autos.pk_auto, Autos.name, Autos.fk_automarket, Autos.price, Autos.year_of_release
            FROM Autos
            JOIN AutoMarkets ON Autos.fk_automarket = AutoMarkets.pk_automarket
            WHERE AutoMarkets.name = ?
        """, (automarket_name,))
        rows = self.cursor.fetchall()
        return [Auto(pk_auto=row[0], name=row[1], fk_automarket=row[2], price=row[3],
                     year_of_release=date.fromisoformat(row[4])) for row in rows]

    def find_autos_by_year(self, year: int):
       self.cursor.execute("""
           SELECT pk_auto, name, fk_automarket, price, year_of_release
           FROM Autos
           WHERE SUBSTR(year_of_release, 1, 4) = ?
       """, (str(year),))
       rows = self.cursor.fetchall()
       return [Auto(pk_auto=row[0], name=row[1], fk_automarket=row[2], price=row[3],
                     year_of_release=date.fromisoformat(row[4])) for row in rows]

    def list_all_autos(self):
        self.cursor.execute("SELECT pk_auto, name, year_of_release, price FROM Autos")
        rows = self.cursor.fetchall()
        return [f"{row[0]}. {row[1]} ({date.fromisoformat(row[2]).year}), {row[3]}" for row in rows] # added date processing

    def list_all_automarkets(self):
        self.cursor.execute("SELECT pk_automarket, name FROM AutoMarkets")
        rows = self.cursor.fetchall()
        return [f"{row[0]}. {row[1]}" for row in rows]

    def list_all_cities(self):
        self.cursor.execute("SELECT pk_city, name FROM Cities")
        rows = self.cursor.fetchall()
        return [f"{row[0]}. {row[1]}" for row in rows]

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
        return f"AutoSells(cities={self.list_all_cities()}, automarkets={self.list_all_automarkets()}, autos={self.list_all_autos()})"

    def __del__(self):  # Close the connection when the object is deleted
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


# auto_data.py
import json
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
    def __init__(self, db_path="autosells.txt"):
        self.db_path = db_path
        self.data = self._load_data()
        if not self.data:
            self.data = {"cities": [], "automarkets": [], "autos": []}

    def _load_data(self):
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_data(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def _check_if_exists(self, table_name: str, pk_column: str, pk_value):
        for item in self.data.get(table_name, []):
            if item.get(pk_column) == pk_value:
                return True
        return False

    def add_city(self, city: City):
        if not self._check_if_exists("cities", "pk_city", city.pk_city):
            self.data["cities"].append({"pk_city": city.pk_city, "name": city.name})
            self._save_data()

    def add_automarket(self, automarket: AutoMarket):
        if not self._check_if_exists("automarkets", "pk_automarket", automarket.pk_automarket):
            self.data["automarkets"].append({"pk_automarket": automarket.pk_automarket, "name": automarket.name,
                                             "fk_city": automarket.fk_city})
            self._save_data()

    def add_auto(self, auto: Auto):
        if not self._check_if_exists("autos", "pk_auto", auto.pk_auto):
            self.data["autos"].append({"pk_auto": auto.pk_auto, "name": auto.name, "fk_automarket": auto.fk_automarket,
                                      "price": auto.price, "year_of_release": auto.year_of_release.isoformat()})
            self._save_data()

    def find_autos_by_city(self, city_name: str):
        autos_list = []
        for auto in self.data["autos"]:
            for automarket in self.data["automarkets"]:
                if auto["fk_automarket"] == automarket["pk_automarket"]:
                    for city in self.data["cities"]:
                        if automarket["fk_city"] == city["pk_city"] and city["name"] == city_name:
                            autos_list.append(Auto(pk_auto=auto["pk_auto"], name=auto["name"],
                                                  fk_automarket=auto["fk_automarket"], price=auto["price"],
                                                  year_of_release=date.fromisoformat(auto["year_of_release"])))

        return autos_list

    def find_autos_by_price_range(self, min_price: float, max_price: float):
        autos_list = []
        for auto in self.data["autos"]:
            if min_price <= auto["price"] <= max_price:
                autos_list.append(Auto(pk_auto=auto["pk_auto"], name=auto["name"],
                                      fk_automarket=auto["fk_automarket"], price=auto["price"],
                                      year_of_release=date.fromisoformat(auto["year_of_release"])))
        return autos_list

    def find_autos_by_automarket(self, automarket_name: str):
        autos_list = []
        for auto in self.data["autos"]:
            for automarket in self.data["automarkets"]:
                if auto["fk_automarket"] == automarket["pk_automarket"] and automarket["name"] == automarket_name:
                    autos_list.append(Auto(pk_auto=auto['pk_auto'], name=auto['name'],
                                          fk_automarket=auto['fk_automarket'], price=auto['price'],
                                          year_of_release=date.fromisoformat(auto['year_of_release'])))

        return autos_list

    def find_autos_by_year(self, year: int):
        autos_list = []
        for auto in self.data["autos"]:
            if date.fromisoformat(auto["year_of_release"]).year == year:
                autos_list.append(Auto(pk_auto=auto["pk_auto"], name=auto["name"],
                                      fk_automarket=auto["fk_automarket"], price=auto["price"],
                                      year_of_release=date.fromisoformat(auto["year_of_release"])))
        return autos_list

    def list_all_autos(self):
        autos_list = []
        for auto in self.data["autos"]:
            year_of_release = date.fromisoformat(auto["year_of_release"]).year
            autos_list.append(f"{auto['pk_auto']}. {auto['name']} ({year_of_release}), {auto['price']}")
        return autos_list

    def list_all_automarkets(self):
        automarkets_list = []
        for automarket in self.data["automarkets"]:
            automarkets_list.append(f"{automarket['pk_automarket']}. {automarket['name']}")
        return automarkets_list

    def list_all_cities(self):
        cities_list = []
        for city in self.data["cities"]:
            cities_list.append(f"{city['pk_city']}. {city['name']}")
        return cities_list

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

            elif choice == '8':
                print(f"{self=}")

                self.scip()

            elif choice == '0':
                break

            else:
                print("Неверный выбор. Попробуйте снова.")

                self.scip()

    def __str__(self):
      return f"AutoSells(cities={self.list_all_cities()}, automarkets={self.list_all_automarkets()}, autos={self.list_all_autos()})"

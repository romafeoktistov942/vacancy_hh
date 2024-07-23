import json
from abc import ABC, abstractmethod
from src.vacancy import WorkVacancy
import os


class BaseConnector(ABC):

    @abstractmethod
    def create_vacancy_list(self) -> list:
        pass

    @abstractmethod
    def add_vacancy(self) -> None:
        pass

    @abstractmethod
    def get_info(self, key_name: str, value_name: str | int) -> list:
        pass

    @abstractmethod
    def delete_vacancy(self) -> None:
        pass

    @staticmethod
    def filter_vacancy(
        dict_vacancy: dict, key_name: str, value_name: int | str
    ):
        pass


class Connector(BaseConnector):

    def __init__(self, name_file: str) -> None:
        self._vacancy_list = []
        self._finish_list = []
        self.name_file = name_file

    @staticmethod
    def filter_vacancy(vacancy_dict: dict, key: str, value: int | str) -> bool:
        return vacancy_dict[key] == value

    def create_vacancy_list(self) -> list:
        """
        Метод класса для формирования списка вакансий по новому
        :param name_file: название файла, в котором хранится спаршенная информация с hh.ru
        :return: список вакансий после обработки классом WorkVacancy
        """

        with open(self.name_file, "r", encoding="utf-8") as file:
            read_vacancy_file = json.load(file)
            for item in read_vacancy_file:
                if item["salary"] is None or item["area"] is None:
                    continue
                else:
                    self._vacancy_list.append(
                        WorkVacancy(
                            item["name"],
                            item["alternate_url"],
                            item["area"]["name"],
                            item["salary"]["from"],
                            item["salary"]["to"],
                            item["salary"]["currency"],
                            item["snippet"]["requirement"],
                        )
                    )
        return self._vacancy_list

    def add_vacancy(self) -> None:
        vacancy_list = self.create_vacancy_list()
        new_vac = []

        with open(self.name_file, "w", encoding="utf-8") as file:
            for f in vacancy_list:
                salary_from = f.salary_from
                salary_to = f.salary_to
                currency = f.salary_currency

                new_vac.append(
                    {
                        "name": f.name_vacancy,
                        "url": f.url_vacancy,
                        "area": f.city,
                        "salary_from": salary_from,
                        "salary_to": salary_to,
                        "currency": currency,
                        "snippet": f.snippet_requirement,
                    }
                )

            return json.dump(new_vac, file, indent=4)

    def get_info(self, key_name: str, value_name: str | int) -> list:
        """
        Метод класс возвращающий информацию по вакансиям по ключевым словам полученным о пользователя
        :param key_name: наименование ключа в словаре из списка вакансий, по которому
                         ведется сортировка вакансий
        :param value_name: значение ключа для словаря, содержащегося в списке вакансий,
                           получаемый от пользователя. Для осуществления подбора вакансий
        :return: список отфильтрованных вакансий в соответствии с заданным условием
        """
        with open(self.name_file, "r", encoding="utf-8") as file:
            top_list = json.load(file)
            for item in top_list:
                if self.filter_vacancy(item, key_name, value_name) is True:
                    self._finish_list.append(item)
                else:
                    continue
            return self._finish_list

    def __str__(self, *args):
        return f"{self.get_info(*args)}"

    def delete_vacancy(self) -> None:
        """Метод удаляющий файл *.json содержащий вакансии сформированный в соответсвии с заданной структурой"""
        os.remove(self.name_file)

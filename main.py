from src.work_API import HH
from src.user_interface import interface
from src.connector import Connector


def main():
    user_input = input("Введите название вакансии: ")
    user_request = HH(f"./data/{user_input}_vacancies.json")

    print("Ожидаем получения данных по вакансиям...")

    user_request.load_vacancies(user_input)

    print("Данные записаны")

    connect = Connector(f"./data/{user_input}_vacancies.json")
    connect.add_vacancy()
    interface(f"./data/{user_input}_vacancies.json")


if __name__ == "__main__":
    main()

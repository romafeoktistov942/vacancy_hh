from abc import ABC, abstractmethod
import psycopg2
import csv


class ManagerBase(ABC):

    @abstractmethod
    def create_database(self):
        pass

    @abstractmethod
    def del_database(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def del_table(self):
        pass

    @abstractmethod
    def get_companies_and_vacancies_count(self) -> list:
        pass

    @abstractmethod
    def get_all_vacancies(self) -> list:
        pass

    @abstractmethod
    def get_avg_salary(self) -> list:
        pass

    @abstractmethod
    def get_vacancies_with_higher_salary(self) -> list:
        pass

    @abstractmethod
    def get_vacancies_with_keyword(self, keyword: str) -> list:
        pass


class DBManager(ManagerBase):
    """Класс извлекающий информацию из таблиц работодателей и их вакансий"""

    def __init__(self, database: dict) -> None:
        self.host = database["host"]
        self.port = database["port"]
        self.user = database["user"]
        self.password = database["password"]

    def _open_connect(self) -> list:
        """Метод класса DatabasePostgres осуществляющий открытие соединения и указателя к БД"""
        auto_commit = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
        )
        conn.set_isolation_level(auto_commit)
        cur = conn.cursor()
        return [conn, cur]

    def _connect_to_db(self) -> list:
        """Метод класса DatabasePostgres осуществляющий открытие соединения и указателя к БД"""
        auto_commit = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database="info_employers",
        )
        conn.set_isolation_level(auto_commit)
        cur = conn.cursor()
        return [conn, cur]

    @staticmethod
    def _close_connect(conn, cur) -> list:
        """Метод класса DatabasePostgres осуществляющий закрытие указателя и соединения к БД"""
        cl_cur = cur.close()
        cl_conn = conn.close()
        return [cl_cur, cl_conn]

    def create_database(self) -> None:
        """Метод класса DatabasePostgres осуществляющий создание БД"""

        self.del_database()

        conn, cur = self._open_connect()
        try:
            cur.execute("CREATE DATABASE info_employers;")
            conn.commit()
        except psycopg2.errors.DuplicateDatabase:
            print("База данных уже существует")
        finally:
            cl_cur, cl_conn = self._close_connect(conn, cur)

    def del_database(self) -> None:
        """Метод класса DatabasePostgres осуществляющий удаление БД"""
        conn, cur = self._open_connect()

        try:
            cur.execute("DROP DATABASE IF EXISTS info_employers;")
            conn.commit()
        except psycopg2.errors.ObjectInUse:
            print("База данных используется и не может быть удалена")
        finally:
            cl_cur, cl_conn = self._close_connect(conn, cur)

    def create_schema(self) -> None:
        """Метод класса DatabasePostgres осуществляющий создание схемы БД"""
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path TO info_employers")
        cur.execute("CREATE SCHEMA IF NOT EXISTS info_employers;")

        conn.commit()

        cl_cur, cl_conn = self._close_connect(conn, cur)

    def create_path_to_database(self) -> None:
        conn, cur = self._connect_to_db()

        cur.execute("SET search_path TO info_employers")
        conn.commit()

        cl_cur, cl_conn = self._close_connect(conn, cur)

    def create_table(self) -> None:
        """Метод класса DatabasePostgres осуществляющий формирование таблиц БД"""
        conn, cur = self._connect_to_db()

        self.create_database()
        self.create_schema()
        cur.execute("SET search_path='info_employers';")

        try:
            cur.execute(
                f"CREATE TABLE info_employers.employers("
                f"id_employer INT PRIMARY KEY,"
                f"company_name VARCHAR(100) NOT NULL,"
                f"url_employer_to_pars TEXT NOT NULL,"
                f"url_employer TEXT NOT NULL,"
                f"url_vacancies_employer_to_pars TEXT NOT NULL,"
                f"open_vacancies int NOT NULL"
                f");"
            )
        except psycopg2.errors.DuplicateTable:
            cur.execute("truncate table info_employers.employers cascade")
        try:
            cur.execute(
                f"CREATE TABLE info_employers.logo("
                f"id_logo_company VARCHAR(50) PRIMARY KEY,"
                f"id_employer INT NOT NULL,"
                f"picture_original TEXT NOT NULL,"
                f"picture_240 TEXT NOT NULL,"
                f"picture_90 TEXT NOT NULL,"
                f"FOREIGN KEY (id_employer) REFERENCES employers(id_employer)"
                f");"
            )
        except psycopg2.errors.DuplicateTable:
            cur.execute("truncate table info_employers.logo cascade")
        try:
            cur.execute(
                f"CREATE TABLE info_employers.vacancies("
                f"id_vacancy INT PRIMARY KEY,"
                f"id_employer INT NOT NULL,"
                f"name_vacancy VARCHAR(100) NOT NULL,"
                f"url_vacancy TEXT NOT NULL,"
                f"FOREIGN KEY (id_employer) REFERENCES employers(id_employer)"
                f");"
            )
        except psycopg2.errors.DuplicateTable:
            cur.execute("truncate table info_employers.vacancies cascade")
        try:
            cur.execute(
                f"CREATE TABLE info_employers.salary("
                f"id_salary VARCHAR(50) PRIMARY KEY,"
                f"id_vacancy INT NOT NULL,"
                f"salary_to INT,"
                f"salary_from INT,"
                f"currency VARCHAR(5),"
                f"gross VARCHAR(5),"
                f"FOREIGN KEY (id_vacancy) REFERENCES vacancies(id_vacancy)"
                f");"
            )
        except psycopg2.errors.DuplicateTable:
            cur.execute("truncate table info_employers.salary cascade")
        try:
            cur.execute(
                f"CREATE TABLE info_employers.city("
                f"id_vacancy_city VARCHAR(50) PRIMARY KEY,"
                f"id_vacancy INT NOT NULL,"
                f"id_city VARCHAR(20),"
                f"name_city VARCHAR(100),"
                f"url_city_to_pars TEXT,"
                f"FOREIGN KEY (id_vacancy) REFERENCES vacancies(id_vacancy)"
                f");"
            )
        except psycopg2.errors.DuplicateTable:
            cur.execute("truncate table info_employers.city cascade")
        try:
            cur.execute(
                f"CREATE TABLE info_employers.snippet("
                f"id_snippet VARCHAR(50) PRIMARY KEY,"
                f"id_vacancy INT NOT NULL,"
                f"requirement TEXT NOT NULL,"
                f"responsibility TEXT NOT NULL,"
                f"FOREIGN KEY (id_vacancy) REFERENCES vacancies(id_vacancy)"
                f");"
            )
        except psycopg2.errors.DuplicateTable:
            cur.execute("truncate table info_employers.snippet cascade")

        conn.commit()

        cl_cur, cl_conn = self._close_connect(conn, cur)

    def del_table(self) -> None:
        """Метод класса DatabasePostgres осуществляющий удаление таблиц БД"""
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")

        cur.execute("DROP TABLE info_employers.employers CASCADE;")
        cur.execute("DROP TABLE IF EXISTS info_employers.logo;")
        cur.execute("DROP TABLE info_employers.vacancies CASCADE;")
        cur.execute("DROP TABLE IF EXISTS info_employers.salary;")
        cur.execute("DROP TABLE IF EXISTS info_employers.city;")
        cur.execute("DROP TABLE IF EXISTS info_employers.snippet;")

        conn.commit()

        cl_cur, cl_conn = self._close_connect(conn, cur)

    def load_info_in_table(
        self, path_to_file_csv: str, table_name: str
    ) -> None:
        """Метод класса DatabasePostgres осуществляющий заполнение данными таблиц БД"""
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")

        with open(path_to_file_csv, newline="", encoding="utf-8") as file:
            reader_csv = csv.reader(file)
            header = next(reader_csv)
            for row in reader_csv:
                query = (
                    f"INSERT INTO {table_name} ({', '.join(header)}) VALUES"
                    f"({', '.join(['%s'] * len(row))}) ON CONFLICT ({header[0]}) DO NOTHING;"
                )
                cur.execute(query, row)

        conn.commit()

        cl_cur, cl_conn = self._close_connect(conn, cur)

    def get_companies_and_vacancies_count(self) -> list:
        """
        Метод получения списка всех компаний и количества вакансий у каждой компании
        :return all_info: список из наименований компаний и количество вакансий.
        """
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")

        query = (
            f"SELECT DISTINCT(company_name), COUNT(*) as count_vacancy FROM employers"
            f" JOIN vacancies USING (id_employer)"
            f" GROUP BY company_name"
            f" ORDER BY COUNT(*);"
        )
        cur.execute(query)
        conn.commit()
        all_info = cur.fetchall()

        cl_cur, cl_conn = self._close_connect(conn, cur)

        return all_info

    def get_all_vacancies(self) -> list:
        """
        Метод получения списка всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.
        :return all_info: список из наименований компаний, наименований вакансий, ссылок на вакансии,
                          уровня дохода 'до', уровня дохода 'от'
        """
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")

        query = (
            f"SELECT DISTINCT(company_name), name_vacancy, url_vacancy, salary_to, salary_from"
            f" FROM employers"
            f" JOIN vacancies USING (id_employer)"
            f" JOIN salary USING (id_vacancy);"
        )
        cur.execute(query)
        conn.commit()
        all_info = cur.fetchall()

        cl_cur, cl_conn = self._close_connect(conn, cur)

        return all_info

    def get_avg_salary(self) -> list:
        """
        Метод получения средней зарплаты по вакансиям.
        :return all_info: список из среднего уровня дохода 'до', среднего уровня дохода 'от'
        """
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")

        query = f"SELECT AVG(salary_to), AVG(salary_from) FROM salary;"
        cur.execute(query)
        conn.commit()
        all_info = cur.fetchall()

        cl_cur, cl_conn = self._close_connect(conn, cur)

        return all_info

    def get_vacancies_with_higher_salary(self) -> list:
        """
        Метод получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        :return all_info: список содержащий обработанную информацию
        """
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")
        query = (
            f"SELECT * FROM vacancies"
            f" JOIN salary USING (id_vacancy)"
            f" JOIN employers USING (id_employer)"
            f" WHERE salary_to > (SELECT AVG(salary_to) FROM salary) AND"
            f" salary_from > (SELECT AVG(salary_from) FROM salary);"
        )
        cur.execute(query)
        conn.commit()
        all_info = cur.fetchall()

        cl_cur, cl_conn = self._close_connect(conn, cur)

        return all_info

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """
        Метод получает список всех вакансий, в названии которых содержатся переданные в метод слова
        :return all_info: список содержащий обработанную информацию
        """
        conn, cur = self._connect_to_db()
        cur.execute("SET search_path='info_employers';")

        query = (
            f"SELECT * FROM vacancies"
            f" JOIN salary USING (id_vacancy)"
            f" JOIN employers USING (id_employer)"
            f" WHERE name_vacancy LIKE '%{keyword}%';"
        )
        cur.execute(query)
        conn.commit()
        all_info = cur.fetchall()

        cl_cur, cl_conn = self._close_connect(conn, cur)

        return all_info

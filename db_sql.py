import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
class Subs_db():

    def __init__(self):
        
        load_dotenv()

        self.conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT')
        )
        self.conn.autocommit = True

    def insert_user_history_search(self, user_id):
        """
        Получение списка истории пользователя

        Parameters
        ----------
            user_id: int 
            vacancy: str

        Returns
        -------
        Nothing
        """
        try:
            cur = self.conn.cursor()
            check_numb_query = 'SELECT vacancy_name FROM subscriptions.users_history_search WHERE user_id = %s ORDER by vacancy_date;'
            cur.execute(check_numb_query, (user_id, ))  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()

            check_query = '''
            SELECT 1 FROM subscriptions.users_history_search
            WHERE user_id = %s AND LOWER(vacancy_name) = LOWER(%s)
            '''
            cur.execute(check_query, (user_id, vacancy))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()

            if not exists: # Если запись не существует
                
                if len(rows) >=5:
                    old_vacancy_name = rows[0][0]
                    delete_one_vac = 'DELETE FROM subscriptions.users_history_search WHERE user_id = %s AND vacancy_name= %s'
                    cur.execute(delete_one_vac,(user_id,old_vacancy_name))

                insert_new_vac = 'INSERT INTO subscriptions.users_history_search (user_id, vacancy_name) VALUES (%s, %s)'
                cur.execute(insert_new_vac,(user_id,vacancy))                   
                cur.close()
                return
            
            cur.close()
            return
        except Exception as error:
            print('There are some problems in insert_users_history_search function:', error )
        
    def get_user_history_search(self, user_id):
        """
        Получение списка вакансий пользователя

        Parameters
        ----------
            user_id: int 

        Returns
        -------
        list[vacancies]
        """
        try:
            cur = self.conn.cursor()
            query = 'SELECT vacancy_name FROM subscriptions.users_history_search WHERE user_id = %s ORDER by vacancy_date DESC;'
            cur.execute(query, (user_id, ))  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if not rows:
                return "No vacancies found."
            vacancies = [row[0] for i,row in enumerate(rows) if i <5]
            
            cur.close()
            
            return vacancies
        except Exception as error:
            print('There are some problems in get_user_history_search:', error )
            return "Произошла ошибка вывода вакансий"


    def delete_user_sub_company(self, user_id, company):
        try:
            cur = self.conn.cursor()
            check_numb_query = 'SELECT vacancy FROM subscriptions.user_subscriptions_company WHERE user_id = %s AND company ILIKE %s;'
            cur.execute(check_numb_query, (user_id,company ))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            if not exists:
                print('Данной вакансии нет в подписках')
                return False
            delete_query = '''
            DELETE FROM subscriptions.user_subscriptions_company
            WHERE user_id = %s AND company = %s
            '''
            cur.execute(delete_query, (user_id, company))  # Выполнение запроса с подстановкой параметров
        
            cur.close()
        except Exception as error:
            print('There are some problems in delete_user_sub function:', error )      
    def insert_user_sub_company(self, user_id, company):
        """
        Ввод вакансии

        Parameters
        ----------
            user_id: int 
            company: str

        Returns
        -------
        Nothing.
        """
        try:
            cur = self.conn.cursor()
            check_numb_query = 'SELECT company FROM subscriptions.user_subscriptions_company WHERE user_id = %s;'
            cur.execute(check_numb_query, (user_id, ))  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if len(rows) >6:
                return 'Слишком много подписок'
            check_query = '''
            SELECT 1 FROM subscriptions.user_subscriptions_company
            WHERE user_id = %s AND company = %s
            '''
            cur.execute(check_query, (user_id, company))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()

            if not exists:  # Если запись не существует
                
                insert_query = '''
                INSERT INTO subscriptions.user_subscriptions_company (user_id, company)
                VALUES (%s, %s)
                '''

                # Выполнение запроса
                cur.execute(insert_query, (user_id, company))


            # Закрытие курсора и соединения
            cur.close()
        except Exception as error:
            print('There are some problems in insert_user_sub_company function:', error )    
    def insert_user_sub(self, user_id, name_vacancy:str, filter):
        """
        Ввод вакансии

        Parameters
        ----------
            user_id: int 
            name_vacancy: str

        Returns
        -------
        Nothing.
        """
        try:
            cur = self.conn.cursor()
            filter_dict = json.loads(filter)
            subcategory_key = next(iter(filter_dict['Categories']))
            if isinstance(filter_dict['Categories'],dict):
                if filter_dict['Categories'][subcategory_key] == 'Другое':
                    name_vacancy = 'Категория: '+subcategory_key
                else:
                    name_vacancy = 'Категория: '+filter_dict['Categories'][subcategory_key]

            else:
                name_vacancy = name_vacancy

            check_numb_query = 'SELECT vacancy FROM subscriptions.user_subscriptions WHERE user_id = %s;'
            cur.execute(check_numb_query, (user_id, ))  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if len(rows) >6:
                cur.close()
                return 'Слишком много подписок'
            check_query = '''
            SELECT 1 FROM subscriptions.user_subscriptions
            WHERE user_id = %s AND LOWER(vacancy) = LOWER(%s) and filter::jsonb=%s::jsonb
            '''
            cur.execute(check_query, (user_id, name_vacancy,filter))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            
            insert_query = '''
                INSERT INTO subscriptions.user_subscriptions (user_id, vacancy, filter)
                VALUES (%s, %s, %s)
                '''
            
            if not exists:  # Если запись не существует
                


                # Выполнение запроса
                cur.execute(insert_query, (user_id, name_vacancy,filter))
                cur.close()
                return 'Succes'
            else:
                cur.close()
                return 'Double subscribe'

            # Закрытие курсора и соединения
            
        except Exception as error:
            print('There are some problems in insert_user_sub function:', error )
            return 'Error'

    def delete_user_sub(self, user_id, vacancy):
        try:
            cur = self.conn.cursor()
            check_numb_query = 'SELECT vacancy FROM subscriptions.user_subscriptions WHERE user_id = %s AND vacancy ILIKE %s;'
            cur.execute(check_numb_query, (user_id,vacancy ))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            if not exists:
                print('Данной вакансии нет в подписках')
                return False
            delete_query = '''
            DELETE FROM subscriptions.user_subscriptions
            WHERE user_id = %s AND vacancy = %s
            '''
            cur.execute(delete_query, (user_id, vacancy))  # Выполнение запроса с подстановкой параметров
        
            cur.close()
        except Exception as error:
            print('There are some problems in delete_user_sub function:', error )
    def all_users_id(self):   
        try:
            cur = self.conn.cursor()
            query = 'SELECT user_id FROM lorabot.users ;'
            cur.execute(query)  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if not rows:
                return "No users found."
            users = [row[0] for row in rows]
            
            cur.close()
            return users
        except Exception as error:
            print('There are some problems in select function:', error )
            return "Произошла ошибка вывода вакансий"
        
    def users_id_with_urgent_notif(self):
        """
        Returns
        -------
        list[str(user_id), ...]
        """   
        try:
            cur = self.conn.cursor()
            query = 'SELECT user_id FROM lorabot.users WHERE urgent_notif=true;'
            cur.execute(query)  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if not rows:
                return "No users found."
            users = [row[0] for row in rows]
            
            cur.close()
            return users
        except Exception as error:
            print('There are some problems in users_id_with_urgent_notif function:', error )
            return "Произошла ошибка вывода вакансий"

    def check_user_id_on_urgent_notif(self,user_id):
        """
        Returns
        -------
        True or False
        """   
        try:
            cur = self.conn.cursor()
            query = 'SELECT urgent_notif FROM lorabot.users WHERE user_id=%s;'
            cur.execute(query,(user_id,))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            if exists:
                cur.close()
                return exists[0]
            else:
                cur.close()
  
        except Exception as error:
            print('There are some problems in check_user_id_with_urgent_notif function:', error )
            return "Check user_id error"      
    def add_urgent_notif(self,user_id):

        try:
            cur = self.conn.cursor()
            
            check_query = 'SELECT user_id FROM lorabot.users WHERE user_id = %s and urgent_notif=false'
            cur.execute(check_query,(user_id,))
            exists = cur.fetchone()
            if not exists:

                return 'Urgent notif is already true'
            
            else:
                query = '''
                        UPDATE lorabot.users
	                    SET urgent_notif=true
	                    WHERE user_id = %s
                        '''
                cur.execute(query,(user_id,))  # Выполнение запроса с подстановкой параметров
 
        except Exception as error:
            print('There are some problems in del_urgent_notif function:', error )        
    def del_urgent_notif(self,user_id):

        try:
            cur = self.conn.cursor()
            
            check_query = 'SELECT user_id FROM lorabot.users WHERE user_id = %s and urgent_notif=true'
            cur.execute(check_query,(user_id,))
            exists = cur.fetchone()
            if not exists:

                return 'Urgent notif is already false'
            
            else:
                query = '''
                        UPDATE lorabot.users
	                    SET urgent_notif=false
	                    WHERE user_id = %s
                        '''
                cur.execute(query,(user_id,))  # Выполнение запроса с подстановкой параметров
 
        except Exception as error:
            print('There are some problems in del_urgent_notif function:', error )

    def all_subs_user(self, user_id):
        """
        Выводит все вакансии определённого пользователя

        Parameters
        ----------
            user_id: int 

        Returns
        -------
        Возвращает str со всеми вакансиями по дате добавления
        """
        try:
            cur = self.conn.cursor()
            query = 'SELECT vacancy,filter FROM subscriptions.user_subscriptions WHERE user_id = %s ORDER by subscription_date DESC;'
            cur.execute(query, (user_id, ))  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if not rows:
                return "No vacancies found."
            filters = [row[1] for row in rows]
            filters_formatted = []
            for filter in filters:
                text = ''
                experience = filter['Experience']
                schedule =  filter['Schedule']
                salary = filter['Salary']
                education = filter['Education']

                if salary != 0:
                    
                    text+=f'зарплата: от {salary}'

                if schedule !='Не указано':
                    if 'зарплата' in text:
                        text+=', '
                    text+=f'график: '
                    for i,elem in enumerate(schedule):
                        if i != len(schedule) - 1:
                            text+=f'{elem}'
                            text+=', '
                        else:
                            text+=f'{elem}'
                if experience!='Не указано':
                    if 'зарплата' in text or 'график' in text:
                        text+=', '
                    text+=f'опыт: '
                    for i,elem in enumerate(experience):
                        if i != len(experience) - 1:
                            text+=f'{elem}'
                            text+=', '
                        else:
                            text+=f'{elem}'
                if education !='Не указано':
                    if 'зарплата' in text or 'график' in text or 'опыт' in text:
                        text+=', '
                    text+=f'образование: '
                    for i,elem in enumerate(education):
                        if i != len(education) - 1:
                            text+=f'{elem}'
                            text+=', '
                        else:
                            text+=f'{elem}'
                text = f'({text.lower()})' if text !='' else ''
                
                filters_formatted.append(text)    
                    
            vacancies = [row[0] for row in rows]
            
            cur.close()
            
            vacancies_str = '\n'.join(f"{i+1}. {vacancy} {filters_formatted[i]}" for i, vacancy in enumerate(vacancies))
            return vacancies_str
        except Exception as error:
            print('There are some problems in select function:', error )
            return "Произошла ошибка вывода вакансий"
    def number_subs(self, user_id):
        try:
            cur = self.conn.cursor()
            query = 'SELECT vacancy FROM subscriptions.user_subscriptions WHERE user_id = %s;'
            cur.execute(query, (user_id, ))  # Выполнение запроса с подстановкой параметров
            rows = cur.fetchall()
            if not rows:
                return "No vacancies found."
            vacancies = [row[0] for row in rows]
            number_vacancies = len(vacancies)
            cur.close()
            
            return number_vacancies
        except Exception as error:
            print('There are some problems in select function:', error )
            return "Произошла ошибка вывода числа вакансий"
        


    def insert_vacation(self, name: str, salary_min:str, salary_max:str, description: str, short_description: str,  VacancyId:str, date_added:str,
                         full_description: str, vip_status: bool,filter:dict):
        """
        Ввод вакансии

        Parameters
        ----------
            name_vacancy: str
            salary: str 
            description: str
            short_description: str 
            full_description: str
            date_added: str "DD.MM.YY"(Example: '13.06.2024 22:22')
            VacancyId= str
            

        Returns
        -------
        Nothing.
        """
        
        # Преобразование строки в объект datetime
        date_obj = datetime.strptime(date_added, "%d.%m.%Y %H:%M") - timedelta(hours=9)

        # Преобразование объекта datetime в строку формата TIMESTAMP для PostgreSQL
        timestamp_str = date_obj.strftime('%Y-%m-%d %H:%M:%S') 
        try:
            
            cur = self.conn.cursor()

            check_query = '''
            SELECT 1 FROM subscriptions.vacancies
            WHERE name_vacancy = %s AND salary_min = %s AND salary_max = %s AND description = %s AND VacancyId = %s AND added_date = %s
            '''
            cur.execute(check_query, (name, salary_min, salary_max, description, VacancyId, timestamp_str))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            if not exists:  # Если запись не существует
                
                insert_query = '''
                INSERT INTO subscriptions.vacancies (name_vacancy, salary_min,salary_max, description,short_description,full_description,VacancyId, added_date,vip_status,filter)
                VALUES (%s, %s, %s,%s,%s,%s,%s,%s,%s,%s)
                '''

                # Выполнение запроса
                cur.execute(insert_query, (name, salary_min,salary_max, description,short_description,full_description,VacancyId, timestamp_str,vip_status,filter))

                tsvector_query = ''' UPDATE subscriptions.vacancies
                SET description_tsvector = to_tsvector('russian', full_description)
                WHERE description_tsvector IS NULL
                '''
                cur.execute(tsvector_query)

            # Закрытие курсора и соединения
            cur.close()
        except Exception as error:
            print('There are some problems in insert_vacation function:', error )

    def insert_urgent_vacation(self, name: str, salary_min:str, salary_max:str, description: str, short_description: str,  VacancyId:str, date_added:str):
        """
        Ввод вакансии

        Parameters
        ----------
            name_vacancy: str
            salary: str 
            description: str
            short_description: str 
            date_added: str "DD.MM.YY"(Example: '13.06.2024 22:22')
            VacancyId= str
            

        Returns
        -------
        Nothing.
        """
        
        # Преобразование строки в объект datetime
        date_obj = datetime.strptime(date_added, "%d.%m.%Y %H:%M") - timedelta(hours=9)

        # Преобразование объекта datetime в строку формата TIMESTAMP для PostgreSQL
        timestamp_str = date_obj.strftime('%Y-%m-%d %H:%M:%S') 
        try:
            
            cur = self.conn.cursor()
            check_query = '''
            SELECT 1 FROM subscriptions.urgent_vacancies
            WHERE name_vacancy = %s AND salary_min = %s AND salary_max = %s AND description = %s AND VacancyId = %s AND added_date = %s
            '''
            cur.execute(check_query, (name, salary_min, salary_max, description, VacancyId, timestamp_str))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            if not exists:  # Если запись не существует
                
                insert_query = '''
                INSERT INTO subscriptions.urgent_vacancies (name_vacancy, salary_min,salary_max, description,short_description,VacancyId, added_date)
                VALUES (%s, %s, %s,%s,%s,%s,%s)
                '''

                # Выполнение запроса
                cur.execute(insert_query, (name, salary_min,salary_max, description,short_description, VacancyId, timestamp_str))
            # Закрытие курсора и соединения
            cur.close()
        except Exception as error:
            print('There are some problems in insert_urgent_vacation function:', error )




    def delete_all_vacancies(self):
        try:
            cur = self.conn.cursor()
            query = 'DELETE FROM subscriptions.vacancies;'
            cur.execute(query)  # Выполнение запроса с подстановкой параметров
            cur.close()
            
        except Exception as error:
            print('Произошла ошибка удаления вакансий:', error )
            return "Произошла ошибка удаления вакансий"
    def delete_all_urgent_vacancies(self):
        try:
            cur = self.conn.cursor()
            query = 'DELETE FROM subscriptions.urgent_vacancies;'
            cur.execute(query)  # Выполнение запроса с подстановкой параметров
            cur.close()
            
        except Exception as error:
            print('Произошла ошибка удаления вакансий:', error )
            return "Произошла ошибка удаления вакансий"        
    def get_vacancies(self,name_vac:str, salary_vac=None, schedule = None,experience = None,education=None, category=None,subcategory=None,is_subs=False):
        
        try:
            cur = self.conn.cursor()
            query = '''SELECT description, vacancyid FROM subscriptions.vacancies WHERE 1=1
                    '''
            
            params = []
            if name_vac and name_vac.lower() != 'все вакансии':  # Если name_vac не пустое и не "Все вакансии"
                name_vac = ' & '.join(name_vac.split())
                query += ''' AND description_tsvector @@ to_tsquery('russian', %s) '''
                params.append(name_vac)
            if salary_vac:
                query += ''' AND (
                            (salary_min ~ '^[0-9]+$' AND CAST(regexp_replace(salary_min, '[^0-9]', '', 'g') AS INTEGER) >= %s)
                            OR
                            (salary_max ~ '^[0-9]+$' AND CAST(regexp_replace(salary_max, '[^0-9]', '', 'g') AS INTEGER) >= %s)
                            OR
                            salary_min ILIKE 'Договорная'
                            OR
                            salary_max ILIKE 'Договорная'
                        )'''
                params.extend([salary_vac, salary_vac])
            if isinstance(schedule,list) and schedule !=[]:
                query += " AND ("

                # Создаем список условий для schedule
                conditions = []
                for elem in schedule:
                    conditions.append("(filter->>'Schedule' = %s)")
                    params.append(elem)
                
                # Соединяем условия с 'OR'
                query += " OR ".join(conditions) + ")"     
                        

            if isinstance(experience,list) and experience !=[]:
                query += " AND ("

                # Создаем список условий для schedule
                conditions = []
                for elem in experience:
                    conditions.append("(filter->>'Experience' = %s)")
                    params.append(elem)
                
                # Соединяем условия с 'OR'
                query += " OR ".join(conditions) + ")"  

            if isinstance(education,list) and education != []:
                query += " AND ("

                # Создаем список условий для schedule
                conditions = []
                for elem in education:
                    conditions.append("(filter->>'Education' = %s)")
                    params.append(elem)
                
                # Соединяем условия с 'OR'
                query += " OR ".join(conditions) + ")"  
            if isinstance(category,str) and category != '':
                query += " AND  EXISTS("

                # Создаем список условий для schedule
                # conditions = []
                category = f'{category}'
                subcategory = f'["{subcategory}"]'
                query+=('''SELECT 1
                FROM jsonb_each(filter::jsonb->'Categories') AS category(key, value)
                WHERE key = %s AND value @> %s::jsonb
                                  ''')
                params.extend([category,subcategory])
                
                # Соединяем условия с 'OR'
                query += ")" 
            print(params)
            print(query)     
        # Завершаем запрос сортировкой
            if is_subs:
                query += " ORDER BY added_date DESC;"
            else:
                query += " ORDER BY vip_status DESC, added_date DESC;"
            cur.execute(query, tuple(params))
            print(params)
            rows = cur.fetchall()
            if not rows:
                return "Not vacancies found"
            vacancies = [[desc, vid] for desc, vid in rows]
            cur.close()
            return vacancies
        except Exception as error:
            print(f'Ошибка получения вакансии {name_vac}: ', error)
    def get_vacancies_in_subs(self,name_vac:str, salary_vac):
        name_vac = ' & '.join(name_vac.split())
        try:
            cur = self.conn.cursor()
            query = '''SELECT description, vacancyid
                    FROM subscriptions.vacancies WHERE (
                        (salary_min ~ '^[0-9]+$' AND CAST(regexp_replace(salary_min, '[^0-9]', '', 'g') AS INTEGER) >= %s)
                        OR
                        (salary_max ~ '^[0-9]+$' AND CAST(regexp_replace(salary_max, '[^0-9]', '', 'g') AS INTEGER) >= %s)
                        OR
                        salary_min ILIKE 'Договорная'
                        OR
                        salary_max ILIKE 'Договорная'
                    )
                    AND
                    description_tsvector @@ to_tsquery('russian',%s) 
                    ORDER by added_date DESC;'''
            cur.execute(query, (salary_vac, salary_vac, name_vac,))
            rows = cur.fetchall()
            if not rows:
                return "Not vacancies found"
            vacancies = [[desc, vid] for desc, vid in rows]
            cur.close()
            return vacancies
        except Exception as error:
            print(f'Ошибка получения вакансии {name_vac}: ', error)
    def get_filter_sub(self,sub_id):
        try:
            cur = self.conn.cursor()
            query = '''SELECT filter
                    FROM subscriptions.user_subscriptions WHERE id=%s
                    ;'''
            cur.execute(query, (sub_id,))
            exists = cur.fetchone()
            if not exists:
                cur.close()
                return "Filter not found"
            
            cur.close()
            return exists[0]
        except Exception as error:
            print(f'Ошибка получения filter sub_id {sub_id}: ', error)                    
    def get_urgent_vacancy(self,vacancy_id):
        try:
            cur = self.conn.cursor()
            query = '''SELECT description
                    FROM subscriptions.urgent_vacancies WHERE vacancyid=%s
                    ;'''
            cur.execute(query, (vacancy_id,))
            exists = cur.fetchone()
            if not exists:
                cur.close()
                return "Vacancy not found"
            
            cur.close()
            return exists[0]
        except Exception as error:
            print(f'Ошибка получения вакансии {vacancy_id}: ', error)        
    def send_subs_vacancies(self,data=1):
        try:
            result = []
            cur = self.conn.cursor()
            subs_query = '''SELECT user_id,vacancy,subscription_date,filter,id FROM subscriptions.user_subscriptions
                        ORDER BY user_id'''
            cur.execute(subs_query)
            subs_rows = cur.fetchall()
            if not subs_rows:
                return "Not subs found"
            for row in subs_rows:
                user_id = row[0]
                vacancy = ' & '.join(row[1].split())
                # vacancy = '%'+row[1]+'%'
                sub_date = row[2]
                filter = row[3]
                sub_id = row[4]
                
                salary = filter['Salary']
                education_list = filter['Education']
                experience_list = filter['Experience']
                schedule_list = filter['Schedule']
                category = filter.get('Categories','Не указано')
                
                if category != 'Не указано':
                    vacancy = ''
                    category_name = next(iter(filter['Categories']))
                    subcategory_name = filter['Categories'][category_name]
                else:
                    category_name = ''
                    subcategory_name=''
                if data == 1:
                    vacancy_query = '''SELECT name_vacancy,short_description,vacancyid FROM subscriptions.vacancies
                            WHERE 
                            added_date >= (CURRENT_TIMESTAMP - INTERVAL '21 hours')
                            AND timestamp %s <= added_date 
                            
                            '''
                else:
                    vacancy_query = '''SELECT name_vacancy,short_description,vacancyid FROM subscriptions.vacancies
                            WHERE 
                            added_date >= (CURRENT_TIMESTAMP - INTERVAL '6 hours')
                            AND timestamp %s <= added_date 
                            
                            '''
                if vacancy:
                    vacancy_query +="AND description_tsvector @@ to_tsquery('russian',%s)"
                    params = [sub_date,vacancy]
                else:
                    params = [sub_date]
                    

                if category != 'Не указано':
                    vacancy_query += " AND  EXISTS("

                    # Создаем список условий для schedule
                    # conditions = []
                    category_name = f"{category_name}"
                    subcategory_name_sql =f'["{subcategory_name}"]'
                    vacancy_query+=('''SELECT 1
                    FROM jsonb_each(filter::jsonb->'Categories') AS category(key, value)
                    WHERE key = %s AND value @> %s::jsonb 
                                    ''')
                    params.extend([category_name,subcategory_name_sql])
                    
                    # Соединяем условия с 'OR'
                    vacancy_query += ")" 
                if salary:
                    vacancy_query += ''' AND (
                                (salary_min ~ '^[0-9]+$' AND CAST(regexp_replace(salary_min, '[^0-9]', '', 'g') AS INTEGER) >= %s)
                                OR
                                (salary_max ~ '^[0-9]+$' AND CAST(regexp_replace(salary_max, '[^0-9]', '', 'g') AS INTEGER) >= %s)
                                OR
                                salary_min ILIKE 'Договорная'
                                OR
                                salary_max ILIKE 'Договорная'
                            )'''
                    params.extend([salary, salary])
                if isinstance(education_list,list):

                    vacancy_query += " AND ("
                    # Создаем список условий для schedule
                    conditions = []
                    for elem in education_list:
                        conditions.append("(filter->>'Education' = %s)")
                        params.append(elem)
                    # Соединяем условия с 'OR'
                    vacancy_query += " OR ".join(conditions) + ")" 
                if isinstance(experience_list,list):
                    vacancy_query += " AND ("
                    # Создаем список условий для schedule
                    conditions = []
                    for elem in experience_list:
                        conditions.append("(filter->>'Experience' = %s)")
                        params.append(elem)
                    # Соединяем условия с 'OR'
                    vacancy_query += " OR ".join(conditions) + ")" 

                if isinstance(schedule_list,list):

                    vacancy_query += " AND ("
                    # Создаем список условий для schedule
                    conditions = []
                    for elem in schedule_list:
                        conditions.append("(filter->>'Schedule' = %s)")
                        params.append(elem)
                    # Соединяем условия с 'OR'
                    vacancy_query += " OR ".join(conditions) + ")"


                vacancy_query+= 'ORDER by added_date DESC;'
                print(params)
                cur.execute(vacancy_query,tuple(params))
                vacancies_rows = cur.fetchall()
                count_vac = len(vacancies_rows)
                if vacancies_rows:
                    for vac in vacancies_rows:
                        description_vac=vac[1]
                        vacancy_id = vac[2]
                        name_sub = row[1]
                        result.append([user_id,description_vac,vacancy_id, name_sub, count_vac,sub_id,category_name,subcategory_name])
                print(vacancy_query)
            
            
            return result

                # print(user_id,vacancy)
                # check_date_sub_query = '''  
                # '''

        except Exception as error:
            print(f'Ошибка в функции send_subs_vacancies: ', error)

    def all_urgent_vacancies(self):
        """
        Returns
        -------
        list of dict

                vacancy_id,
                name_vacancy,
                short_description,
                description
            
            
        Если вакансии не найдены, возвращается строка "Not vacancies found".    
        """
        try:
            result = []
            cur = self.conn.cursor()
            urgent_vacancies_query = '''SELECT vacancyid, name_vacancy, short_description,description FROM subscriptions.urgent_vacancies
                        '''
            cur.execute(urgent_vacancies_query)
            vacancies_rows = cur.fetchall()
            if not vacancies_rows:
                return "Not vacancies found"
            for row in vacancies_rows:
                vacancy_id = row[0]
                name_vacancy = row[1]
                short_description = row[2]
                description = row[3]

                result.append({
                    'vacancy_id' : vacancy_id,
                    'name_vacancy' : name_vacancy,
                    'short_description' : short_description,
                    'description' : description
                })
            return result
        except Exception as error:
            print(f'Ошибка в функции send_urgent_vacancies: ', error)
    def list_urgent_vacancies(self):
        """
        Returns
        -------
        list of dict

                vacancy_id,
                name_vacancy,
                short_description,
                description
            
            
        Возвращает актуальные вакансии.Если вакансии не найдены, возвращается строка "Not vacancies found".    
        """
        try:
            result = []
            cur = self.conn.cursor()
            urgent_vacancies_query = '''SELECT vacancyid, name_vacancy, short_description,description FROM subscriptions.urgent_vacancies
                        WHERE added_date >= (CURRENT_TIMESTAMP - iNTERVAL '1 hour')
                        '''
            cur.execute(urgent_vacancies_query)
            vacancies_rows = cur.fetchall()
            if not vacancies_rows:
                return "Not vacancies found"
            for row in vacancies_rows:
                vacancy_id = row[0]
                name_vacancy = row[1]
                short_description = row[2]
                description = row[3]

                result.append({
                    'vacancy_id' : vacancy_id,
                    'name_vacancy' : name_vacancy,
                    'short_description' : short_description,
                    'description' : description
                })
            return result
        except Exception as error:
            print(f'Ошибка в функции send_urgent_vacancies: ', error)

    def send_subs_vacancies_2(self):
        try:
            result = []
            cur = self.conn.cursor()
            subs_query = '''SELECT user_id,vacancy,subscription_date FROM subscriptions.user_subscriptions
                        ORDER BY user_id'''
            cur.execute(subs_query)
            subs_rows = cur.fetchall()
            if not subs_rows:
                return "Not subs found"
            for row in subs_rows:
                user_id = row[0]
                vacancy = ' & '.join(row[1].split())
                # vacancy = '%'+row[1]+'%'
                sub_date = row[2]
                vacancy_query = '''SELECT name_vacancy,short_description,vacancyid FROM subscriptions.vacancies
                        WHERE description_tsvector @@ to_tsquery('russian',%s)
                        AND added_date >= (CURRENT_TIMESTAMP - INTERVAL '6 hours')
                        AND timestamp %s <= added_date 
                        ORDER by added_date DESC;
                        '''
                cur.execute(vacancy_query,(vacancy,sub_date ))
                vacancies_rows = cur.fetchall()
                count_vac = len(vacancies_rows)
                if vacancies_rows:
                    for vac in vacancies_rows:
                        description_vac=vac[1]
                        vacancy_id = vac[2]
                        name_sub = row[1]
                        
                        result.append([user_id,description_vac,vacancy_id, name_sub, count_vac])
            return result

                # print(user_id,vacancy)
                # check_date_sub_query = '''  
                # '''

        except Exception as error:
            print(f'Ошибка в функции send_subs_vacancies: ', error)

    def delete_all_subs_user(self, user_id):
        try:
            cur = self.conn.cursor()
            check_numb_query = 'SELECT vacancy FROM subscriptions.user_subscriptions WHERE user_id = %s;'
            cur.execute(check_numb_query, (user_id,))  # Выполнение запроса с подстановкой параметров
            exists = cur.fetchone()
            if not exists:
                print('У данного пользователя нет подписок')
                return False
            delete_query = '''
            DELETE FROM subscriptions.user_subscriptions
            WHERE user_id = %s
            '''
            cur.execute(delete_query, (user_id,))  # Выполнение запроса с подстановкой параметров
        
            cur.close()
        except Exception as error:
            print('There are some problems in delete_user_sub function:', error )  


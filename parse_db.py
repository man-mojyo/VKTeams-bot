import re
from db_sql import Subs_db
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import asyncio
import json
#Пример как можно сделать


db = Subs_db() # Объявление объекта класса БД вакансий и подписок
    
async def your_pars_function()    -> None:

    db.delete_all() # Предварительная очистка всей таблицы вакансий
    url = f""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('load', timeout=60000)
        vacancy_count_element= await page.query_selector('.r-category_count')
        vacancy_count_text= await vacancy_count_element.inner_text()
        vacancy_count=int(vacancy_count_text)
        page_count=-(-vacancy_count//20)
        for i in range(1,page_count+1):
            print(i)
            await fetch_vacancies(i,page)
        await browser.close()

def shorten_text(text, max_length=300):
    if len(text) <= max_length:
        return text
    else:
        last_space = text.rfind(' ', 0, max_length)
        if last_space == -1:
            return text[:max_length - 3] + '...'
        else:
            return text[:last_space] + '...'

def html_to_text(html):
    text=re.sub(r'<br><br>', '<br>', html)
    text=re.sub(r'<br>', '\n', text)
    text=re.sub(r'<.*?>', '', text)
    text=text.rstrip()
    return text

def date_formatting(date_text):
    if "Сегодня" in date_text:
        date=datetime.today()
        time_str = date_text.split(", ")[1]
        return date.strftime("%d.%m.%Y")+" "+time_str
    elif "Вчера" in date_text:
        date= datetime.today()-timedelta(days=1)
        time_str = date_text.split(", ")[1]
        return date.strftime("%d.%m.%Y")+" "+time_str
    else:
        return date_text+" "+"00:00"

def salary_formatting(salary_text):
    f=filter(str.isdigit, salary_text)
    salary = "".join(f)
    return salary        

async def fetch_vacancies(page_num,page):
    try:
        url = f"https://rabota.ykt.ru/?page={page_num}"
        print(url)

        
        await page.goto(url)
        await page.wait_for_load_state('load', timeout=60000)
        # job_elements = await page.query_selector_all('.r-vacancy_wrap:not(.r-vacancy_list_urgent .r-vacancy_wrap)')
        job_elements = await page.query_selector_all('.r-vacancy_wrap')
        for job_element in job_elements:
            title_element=await job_element.query_selector('.r-vacancy_title')
            salary_element=await job_element.query_selector('.r-vacancy_salary')
            date_element_2=await job_element.query_selector('.r-vacancy_meta')
            date_element=await job_element.query_selector('.r-vacancy_createdate')
            vip_element =await job_element.query_selector('.r-vacancy_vip')
            vacancy_box_element=await job_element.query_selector('.r-vacancy_box')
            vacancy_full_body_element=await job_element.query_selector('.r-vacancy_body_full')
            vip_status = True if vip_element else False
            title_text=await title_element.inner_text() if title_element else "Не указано"
            salary_text=await salary_element.inner_text() if salary_element else "не указано"
            salary_text=salary_text.replace("руб.", "₽")
            date_text_2=await date_element_2.get_attribute('data-pubdate') if date_element_2 else datetime.now().strftime("%d.%m.%Y")
            date_text=await date_element.inner_text() if date_element else datetime.now().strftime("%d.%m.%Y")
            # print(f'Это date_text: {date_text}\nЭто date_text_2: {date_text_2}')
            date_formatted=date_formatting(date_text_2)
            vacancy_box_list=await job_element.eval_on_selector_all('dd', 'elements => elements.map(el => el.textContent)')
            vacancy_box_text=" ".join(vacancy_box_list)
            vacancy_box_dict = {'Education': vacancy_box_list[0] if len(vacancy_box_list) > 0 else 'Не указано', 
                                'Experience': vacancy_box_list[1] if len(vacancy_box_list) > 1 else 'Не указано',
                                'Schedule':vacancy_box_list[2]if len(vacancy_box_list) > 2 else 'Не указано'}
            # print(title_text)
            # print(vacancy_box_json)
            vacancy_full_body_text= await vacancy_full_body_element.inner_text()
            exclude_element = await job_element.query_selector('.r-vacancy_categories')
            exclude_text = await exclude_element.inner_text()
            # print(exclude_text + '\n ----------------------')
            category_elements = await job_element.query_selector_all('.r-vacancy_categories_item')

            
            vacancy_full_body_text = vacancy_full_body_text.replace(exclude_text,'')
            try:
                vacancy_box_dict['Categories'] = {}
                for element in category_elements:
                    category_element = await element.query_selector('.r-vacancy_categories_item_parent')
                    category_text = await category_element.inner_text()
                    subcategory_element = await element.query_selector('a')
                    subcategory_text = await subcategory_element.inner_text()
                    category_cleaned_text  = category_text.replace('(','').replace(')','').strip()
                    if category_cleaned_text in vacancy_box_dict['Categories']:
                        vacancy_box_dict['Categories'][category_cleaned_text].append(subcategory_text)
                    else:
                    
                        vacancy_box_dict['Categories'][category_cleaned_text] = [subcategory_text]
                    
                    #     categories_list.append(category_cleaned_text)
                    # if category_cleaned_text not in categories_list:
            except Exception as err:
                vacancy_box_dict['Categories'] = {}
                print(f'{err}')
            
            try:
                brief_element = await job_element.query_selector('noindex p') 
                brief_html = await brief_element.inner_html()
                brief_text = html_to_text(brief_html)
            except:
                brief_text=''
            try:
                company_element= await job_element.query_selector('.r-vacancy_company a')
                company_text= await company_element.inner_text()
            except:
                company_text="Не указано"

            try:
                address_element=await job_element.query_selector('.r-vacancy_work-address_address')
                address_text=await address_element.inner_text() if address_element else "Не указано"
            except:
                address_text="Не указано"

            try:
                requirement_selector='.r-vacancy_body_full div:nth-child(6)'
                requirement_element= await job_element.query_selector(requirement_selector)
                requirement_html=await requirement_element.inner_html()
                requirement_text=html_to_text(requirement_html)
                requirement_text=shorten_text(requirement_text, max_length=300)
            except:
                requirement_text="Не указано"

            try:
                condition_selector='.r-vacancy_body_full div:nth-child(8)'
                condition_element= await job_element.query_selector(condition_selector)
                condition_html=await condition_element.inner_html()
                condition_text=html_to_text(condition_html)
                condition_text=shorten_text(condition_text, max_length=300)
            except:
                condition_text="Не указано"
            
            vacancy_id=await title_element.get_attribute('data-id')
            try:      
                name = title_text
                if "-" in salary_text:
                    salary_min, salary_max=salary_text.split("-")
                    salary_min=salary_formatting(salary_min)
                    salary_max=salary_formatting(salary_max)
                elif "Договорная" in salary_text:
                    salary_min=salary_text.strip()
                    salary_max=salary_text.strip()
                else:
                    salary_min=salary_formatting(salary_text)
                    salary_max=salary_formatting(salary_text)
                vacancy_box_dict['Salary_min'] = salary_min
                vacancy_box_dict['Salary_max'] = salary_max
                
                vacancy_box_json = json.dumps(vacancy_box_dict)
                short_description=f'<b>{title_text}</b> — {salary_text}\n<i>{company_text}</i>\n\nПосмотреть на сайте: <a href="https://rabota.ykt.ru/jobs/view?id={vacancy_id}&utm_source=telegram&utm_medium=subscribe&utm_campaign=vacancy"> https://rabota.ykt.ru/jobs/view?id={vacancy_id}</a>'
                description = f'<b>{title_text}</b> — {salary_text}\n<i>{company_text}</i>\n\n<u>✅Требования:</u> {requirement_text}\n\n<u>✅Условия работы:</u> {condition_text}\n\n<u>📍Адрес места работы:</u> {address_text}\n\nПосмотреть на сайте: '
                full_description=f'{title_text}\n{company_text}\n{brief_text}'
                vacancy_id= vacancy_id
                
                
                # print(f'{vacancy_full_body_text} это vacancy_full_body_text')
                db.insert_vacation(name=name, salary_min=salary_min,salary_max=salary_max, description=description, short_description=short_description, 
                                    VacancyId=vacancy_id, date_added=date_formatted, full_description=full_description, vip_status=vip_status, filter = vacancy_box_json)
            except Exception as error:
                print(f'Произошла ошибка добавления вакансии id={vacancy_id} name={name}:', error)
            # obligation_selector='.r-vacancy_body_full div:nth-child(4)'
            # obligation_element=await job_element.query_selector(obligation_selector)
            # obligation_text=await obligation_element.inner_text()
                
        
        print(f"done{page}")
    except Exception as e:
        print(f"Error fetching vacancies: {e}")

def main():
    asyncio.run(your_pars_function())

if __name__ == '__main__':
    main()

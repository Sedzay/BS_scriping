import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure

quotes_list = []
authors_list = []

url = 'https://quotes.toscrape.com/'

# Функція для скрапінгу цитат з однієї сторінки
def scrape_quotes(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('div', class_='quote')

    for quote in quotes:
        quote_text = quote.find('span', class_='text').text
        author = quote.find('small', class_='author').text
        tags = [tag.text for tag in quote.find_all('a', class_='tag')]
        
        quote_info = {
            'quote': quote_text,
            'author': author,
            'tags': tags
        }
        quotes_list.append(quote_info)

# Функція для скрапінгу інформації про автора з його власної сторінки
def scrape_author_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    fullname = soup.find('h3', class_='author-title').text.strip()
    born_date = soup.find('span', class_='author-born-date').text.strip()
    born_location = soup.find('span', class_='author-born-location').text.strip()
    description = soup.find('div', class_='author-description').text.strip()
    
    author_info = {
        'fullname': fullname,
        'born_date': born_date,
        'born_location': born_location,
        'description': description
    }
    if author_info not in authors_list:
        authors_list.append(author_info)

# Функція для скрапінгу всіх сторінок
def scrape_all_pages():
    next_page = url
    while next_page:
        scrape_quotes(next_page)
        response = requests.get(next_page)
        soup = BeautifulSoup(response.text, 'lxml')
        next_button = soup.find('li', class_='next')
        next_page = url + next_button.find('a')['href'] if next_button else None

        # Отримую посилання на сторінку автора та скрапимо її
        authors = soup.find_all('div', class_='quote')
        for author in authors:
            author_link = url + author.find_next('a')['href']
            scrape_author_info(author_link)

# Викликаю функцію для скрапінгу всіх сторінок
scrape_all_pages()



# Зберігаю отримані дані у файли JSON
with open('quotes.json', 'w') as file:
    json.dump(quotes_list, file, indent=2)
   

with open('authors.json', 'w') as file:
    json.dump(authors_list, file, indent=2)
    

print('Дані збережено у файли quotes.json та authors.json.') 

#Підключаюся до MongoDB
try:
    client = MongoClient(
        "mongodb+srv://user:user1@cluster0.upgzm2n.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&appName=Cluster0",
        server_api=ServerApi('1')
    )
except ConnectionFailure as e:
    print("Помилка підключення до бази даних:", e)
    exit()
    
#так, я навмисно допустив помилку в слові autor)
db = client.quotes_autors

# Імпорт даних у колекцію autors
with open('authors.json', 'r') as file:
    authors_data = json.load(file)
    db['autors'].insert_many(authors_data)

# Імпорт даних у колекцію quotes
with open('quotes.json', 'r') as file:
    quotes_data = json.load(file)
    db['quotes'].insert_many(quotes_data)


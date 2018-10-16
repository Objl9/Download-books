import requests
import bs4
import sqlite3

def download_page(page):
    url = 'https://mybook.ru/catalog/fentezi/fentezi-pro-drakonov/books/?page=%d'  % (page)
    request = requests.get(url)
    if request.status_code == 404:
        return None
    return request.text

def download_book_info(href):
    url = 'https://mybook.ru/%s' % (href)
    request = requests.get(url)
    soup = bs4.BeautifulSoup(request.text, 'html.parser')
    author = soup.find('div', {'class': 'book-page-author'}).find('a').text.strip()
    book_name = soup.find('div', {'class': 'book-page-book-name'}).text.strip()
    description = soup.find('div', {'class':"definition-section"}).find('p').text
    return author, book_name, description


def main():
    mybook = sqlite3.connect('mybook.db')
    c = mybook.cursor()
    c.execute('''CREATE TABLE BOOKS
                (ID_book integer PRIMARY KEY autoincrement, author text, book_name text, description text)''')
    page = 1
    while True:
        response = download_page(page)
        if response == None: break
        soup = bs4.BeautifulSoup(response, 'html.parser')
        items_collections = soup.find('div', {"class":"items-collection"})
        item = items_collections.find_all('li', {"class":["item", "item -feature"]})
        for book in item:
            href = book.find('div', {"class": 'book-name'}).find('a').get('href')
            text = download_book_info(href)
            c.execute("INSERT INTO BOOKS(author, book_name, description) VALUES(?,?,?)", text)
        page+=1
    mybook.commit()
    mybook.close()


if __name__ == "__main__":
    main()

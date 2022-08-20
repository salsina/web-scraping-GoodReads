from bs4 import BeautifulSoup
import requests
import csv
from os.path import exists
from lxml import html

def login():
    URL = 'https://www.goodreads.com'
    LOGIN_ROUTE = '/user/sign_in'
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36', 'origin': URL, 'referer': URL + LOGIN_ROUTE}

    s = requests.session()
    result = s.get(URL + LOGIN_ROUTE)
    tree = html.fromstring(result.text)
    
    csrf_token = list(set(tree.xpath("/html/head/meta[3]/@content")))[0]
    n_token = list(set(tree.xpath("/html/body/div[1]/div[1]/div[2]/div/div/div/div[2]/form/fieldset/input/@value")))[0]

    login_payload  = {
        "user[email]": "sina99.sn@gmail.com", 
        "user[password]": "12345678", 
        "authenticity_token": csrf_token,
        "remember_me": "on",
        "next": "Sign in",
        "n": n_token
    }
    login_result = s.post("https://www.goodreads.com/user/sign_in", headers=HEADERS, data=login_payload)
    
    print("login status", login_result)
    return s

Genres = {
'Art':0,
'Biography':0,
'Business':0,
'Children\'s':0,
'Christian':0,
'Classics':0,
'Comics':0,
'Cookbooks':0,
'Ebooks':0,
'Fantasy':0,
'Fiction':0,
'Graphic-Novels':0,
'Historical-Fiction':0,
'History':0,
'Horror':0,
'Memoir':0,
'Music':0,
'Mystery':0,
'Nonfiction':0,
'Poetry':0,
'Psychology':0,
'Romance':0,
'Science':0,
'Science-Fiction':0,
'Self-Help':0,
'Sports':0,
'Thriller':0,
'Travel':0,
'Young-Adult':0}

def write_to_csv(list_input):

    if not exists("allBooks.csv"):
        with open("allBooks.csv", "a") as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(['BookId', 'Link', 'CoverImageLink', 'Genre', 'Description', 'Rate', 'AuthorName', 'PublishYear', 'NumberOfPages', 'Recommended_Genres'])
        fopen.close()
    
    if not exists("allComments.csv"):
        with open("allComments.csv", "a") as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(['BookId','Comment'])
        fopen.close()
    try:
        with open("allBooks.csv", "a") as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            csv_writer.writerow(list_input[:-1])
        fopen.close()
        
        with open("allComments.csv", "a", newline='') as fopen:  # Open the csv file.
            csv_writer = csv.writer(fopen)
            for cmnt in list_input[-1]:
                try:
                    csv_writer.writerow([list_input[0], cmnt])
                except:
                    continue
        fopen.close()

    except:
        return False
          
def get_last_bookId():
    Ids = []
    with open("allBooks.csv", "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped, delimiter=',')
        for row in reader:
            if row:
                Ids.append(row[0])
    return int(Ids[-1])

 
def get_coverImage(soup):
    try:
        return soup.find(id="coverImage")['src']
    except Exception as e:
        return None
def get_description(soup):
    try:
        return soup.find(id="description").find_all('span')[1].get_text()
    except Exception as e:
        try:
            return soup.find(id="description").find_all('span')[0].get_text()
        except Exception as e:
            return None

def get_rate(soup):
    return soup.find(id="bookMeta").find(itemprop='ratingValue').string

def get_authorName(soup):
    return soup.find("a", class_="authorName").find(itemprop='name').get_text()

def get_publishYear(soup):
    text = soup.find(id="details").find_all('div')[1].get_text().split()
    for word in text:
        if len(word) == 4:
            try:
                return int(word)
            except Exception as e:
                continue
            
    for word in text:
        if len(word) == 5:
            try:
                return int(word[:-1])
            except Exception as e:
                continue
    return None

def get_numOfPages(soup):
    return soup.find(id="details").find(itemprop='numberOfPages').string.split()[0]
    
def get_RecommendedGenres(soup):
    userGenres = ""
    recommended_genres = soup.find_all("a", class_="actionLinkLite bookPageGenreLink")
    recommended_genres_voteNumbers = soup.find_all("div", class_="greyText bookPageGenreLink")
    counter = 0
    try:
        for genre in recommended_genres:
            if len(genre.next_sibling) > 1:
                continue
            userGenres += "{" + genre.get_text() + "," + recommended_genres_voteNumbers[counter].get_text().strip() + "},"
            counter += 1
        return userGenres[:-1]
    
    except Exception as e:
        userGenres = ""
        for genre in recommended_genres:
            if len(genre.next_sibling) > 1:
                continue
            userGenres += "{" + genre.get_text() + ",0" + "},"
        return userGenres[:-1]

def get_comments(soup):
    reviewTexts = soup.find_all("div", class_="reviewText stacked")
    comments = []
    for reviewText in reviewTexts:
        try:
            comments.append(reviewText.find_all('span')[2].get_text())
        except Exception as e:
            try:
                comments.append(reviewText.find_all('span')[1].get_text())
            except Exception as e2:
                continue
    return comments

def add_book_info(bookId, book_url, genre):
    if book_url == "https://www.goodreads.com/book/show/4502877-midnight-sun-2008-draft.html":
        return
    print(bookId, genre, book_url)
    book_html = requests.get(book_url).text
    soup = BeautifulSoup(book_html, 'html.parser')
    book_info = {}
    book_info['Link'] = book_url
    book_info['RecommendedGenres'] = get_RecommendedGenres(soup)
    book_info['CoverImage'] = get_coverImage(soup)
    book_info['Genre'] = genre
    book_info['Description'] = get_description(soup)
    book_info['Rate'] = float(get_rate(soup))
    book_info['AuthorName'] = get_authorName(soup)
    try:
        book_info['PublishYear'] = int(get_publishYear(soup))
    except Exception as e:
        book_info['PublishYear'] = None
    try:
        book_info['NumberOfPages'] = int(get_numOfPages(soup))
    except Exception as e:
        book_info['NumberOfPages'] = None
    book_info['Comments'] = get_comments(soup)
    
    lnk = book_info['CoverImage']
    with open('images/'+str(bookId)+".jpg", "wb") as f:
        f.write(requests.get(lnk).content)
    write_to_csv([bookId, book_info['Link'], book_info['CoverImage'],book_info['Genre'], book_info['Description'], book_info['Rate'], book_info['AuthorName'], book_info['PublishYear'], book_info['NumberOfPages'], book_info['RecommendedGenres'], book_info['Comments']])

    return book_info

def get_genre_books(bookId, genre, last_bookId, page_counter, session):
    genre_url = "https://www.goodreads.com/shelf/show/{}?page=".format(genre)
    for i in range(1,8):
        if i < page_counter:
            bookId += 50
            continue
        genre_url += str(i)
        print(genre_url)
        result = session.get(genre_url)
        books = html.fromstring(result.text).find_class("leftAlignedImage")
        
        counter = 1
        # if genre_url == "https://www.goodreads.com/shelf/show/Music?page=4" or\
        #     genre_url == "https://www.goodreads.com/shelf/show/Science-Fiction?page=6" or\
        #         genre_url == "https://www.goodreads.com/shelf/show/Travel?page=6"or\
        #             genre:
        #     counter += 1
        
        for index, book in enumerate(books):
            print(bookId)
            if counter == 50:
                break
            book_url = "https://www.goodreads.com{}.html".format(book.get('href'))
            if bookId > last_bookId:
                add_book_info(bookId, book_url, genre)                    
            bookId += 1
            counter += 1
        genre_url = genre_url[:-1]
        
    return bookId
    
    
def get_data(session, bookId=0):
    try:
        last_bookId = get_last_bookId()
        page_counter = ((last_bookId+1) % 350) // 50 + 1 
        genre_number = (last_bookId + 1)// 350 
    except :
        last_bookId = -1
        page_counter = 1
        genre_number = 0
        
    genre_counter = 1
    for genre in Genres:
        if genre_counter > genre_number:
            try:
                if Genres[genre] == 0:
                    bookId = get_genre_books(bookId, genre, last_bookId, page_counter, session)
                    Genres[genre] = 1
                    print(Genres)
                    get_data(session)
            except:
                print("failed")
                get_data(session)
                
        genre_counter += 1
        bookId += 350
        
if __name__ == "__main__":
    session = login()
    get_data(session)

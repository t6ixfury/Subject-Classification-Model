import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime

import time


def GatherArticleData(URL: str):
    SiteResponse = requests.get(URL)

    SoupParser = bs(SiteResponse.text, 'html.parser')

    title = SoupParser.find('h1', class_= 'title mathjax')
    authors = SoupParser.find('div', class_= 'authors')
    abstract = SoupParser.find('blockquote', class_= 'abstract mathjax')
    subject = SoupParser.find('span', class_= 'primary-subject')
    date = SoupParser.find('div', class_= 'dateline')

    if title:
        #remove the Title: word from the text.
        title_text = title.text.replace('Title:', '').strip()

    if authors:
        #remove the Authors: word from the text.
        authors_text = authors.text.replace('Authors:', '').strip()

    if abstract:
        #remove the abstract: word from the text.
        abstract_text = abstract.text.replace('Abstract:', '').strip()

    if subject:
        #remove paranthesis from the subject text
        subject_text = re.sub(r"\s*\([^)]*\)", "", subject.text).strip()
    
    if date:
        #retrieve the date in the format "MM/DD/YYYY"
        date_pattern = re.search(r'\b(\d{1,2}) (\w{3}) (\d{4})\b', date.text)
        if date_pattern:
            day, month, year = date_pattern.groups()

            date_obj = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")

            date_text = date_obj.strftime("%m/%d/%Y")
    #Put all necessary text in a dictionary and return dictionary
    Article = {'Title': title_text, 'Authors': authors_text, 'Abstract': abstract_text, 'Subject': subject_text, 'Date': date_text}

    return Article

def GetAllArticleLinks(URL:str):
    response = requests.get(URL)

    SoupParser = bs(response.text, 'html.parser')

    url_list = [a.get('href') for a in SoupParser.find_all('a') if a.get('href')]

    pattern = r'https://arxiv\.org/abs/\d+\.\d+'

    filtered_article_urls = [url for url in url_list if re.match(pattern, url)]

    return filtered_article_urls

def GetMaxArticleNumber(URL:str):
    response = requests.get(URL)

    SoupParser = bs(response.text, 'html.parser')

    Articles = SoupParser.find('h1', class_="title is-clearfix")

    Articles_numbers = re.findall(r'\d{1,3}(?:,\d{3})*', Articles.text.strip())

    numbers = [int(num.replace(',', '')) for num in Articles_numbers]

    max_article_numbers = max(numbers) if numbers else None

    return max_article_numbers


def RetrieveData(increment:int):

    data = {'Title': [], 'Authors': [], 'Abstract': [], 'Subject': [], 'Date': []}

    index = 0

    URL=f'https://arxiv.org/search/advanced?advanced=1&terms-0-term=&terms-0-operator=AND&terms-0-field=title&classification-computer_science=y&classification-physics_archives=all&classification
    -include_cross_list=include&date-filter_by=date_range&date-year=&date-from_date=2014&date-to_date=2024&date-date_type=submitted_date&abstracts=show&size={increment}&order=-announced_date_first&start={index}'

    number_of_articles = GetMaxArticleNumber(URL)

    number_of_articles = 1000

    attempts = 10

    while number_of_articles > 49 or attempts < 5:
        links = GetAllArticleLinks(URL)
        time.sleep(0.1) 
        

        for link in links:
            new_data = GatherArticleData(link)
            data['Title'].append(new_data['Title'])
            data['Abstract'].append(new_data['Abstract'])
            data["Authors"].append(new_data['Authors'])
            data["Subject"].append(new_data['Subject'])
            data["Date"].append(new_data['Date'])
            time.sleep(0.1) 
        index = index + increment

        number_of_articles = number_of_articles - increment
        
        URL=f'https://arxiv.org/search/advanced?advanced=1&terms-0-term=&terms-0-operator=AND&terms-0-field=title&classification-computer_science=y&classification-
        physics_archives=all&classification-include_cross_list=include&date-filter_by=date_range&date-year=&date-from_date=2014&date-to_date=2024&date-
        date_type=submitted_date&abstracts=show&size={increment}&order=-announced_date_first&start={index}'
        attempts = attempts - 1
        print(attempts)
        time.sleep(1) 
    return data


AllData = RetrieveData(200)

df = pd.DataFrame(AllData)

df.to_csv("ComputerScienceArticle-Main.csv", index=False)
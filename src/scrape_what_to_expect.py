from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import time
from urllib import urlencode
import pandas as pd

browser = webdriver.Firefox()
search_term = "nutrition"

def search_whattoexpect(query, browser, page):
    base_url = "http://www.whattoexpect.com/info/v1us/{}?c=256652&z=srch&p={}"
    search_url = base_url.format(query,page)
    browser.get(search_url)
    return browser.page_source

def get_article_tags(query, browser):
    """Return the article tag associated with each article found in search.

    Arguments
    ---------
    query

    Returns
    -------
    article_tag : bs4.element.Tag
    """
    article_tags = []
    for i in xrange(10):
        html = search_whattoexpect(query, browser, page=i)
        soup = BeautifulSoup(html, 'html.parser')
        article_tags.extend(soup.select('a.actionlinks'))
    return article_tags

def get_article_title(article_tag):
    """Return the title of an article selected from What to Expect site.

    If no title element is found, return None.

    Arguments
    ---------
    article_tag : bs4.element.Tag
        article.post (from kellymom.com)

    Returns
    -------
    article_titles : list
    """

    title = article_tag.text
    if type(title) == unicode:
        title = title.encode('utf8')

    return title

def get_article_link(article_tag):
    """Return the link of an article from What to Expect site.

    If no link element is found, return None.

    Arguments
    ---------
    article_tag : bs4.element.Tag
        article.post (from kellymom.com)

    Returns
    -------
    article_links : list
    """
    link_str = str(article_tag)
    link = link_str.split()
    link = link[2][6:-1]
    if link.startswith('http://www.whattoexpect.com'):
        return link

def get_content(link, browser, delay=2):
    '''
    Return the content of a selected link from kellymom.com site.


    Arguments
    ---------
    link : string object

    Returns
    -------
    article_content : list
    '''
    if link is not None:
        if link.startswith('http://www.whattoexpect.com'):
            browser.get(link)
            time.sleep(delay)  # Wait a few seconds before getting the HTML source
            source = browser.page_source
            soup = BeautifulSoup(source, 'html.parser')
            content_list = soup.select('div.body-content')
            if len(content_list) == 0:
                return None
            content = content_list[0].text
            return content.encode('ascii', 'ignore').strip().replace('\n', '')

def build_corpus(queries, browser):
    '''
    Takes a search term and returns the title, link and content for all articles with that term

    Arguments
    ---------
    query : list of strings

    Returns
    -------
    corpus : list of rows, with each row containing the title, url and content of each article

    '''
    article_tags = []
    for query in queries:
        article_tag_prelim = get_article_tags(query, browser)
        for article_tag in article_tag_prelim:
            if article_tag not in article_tags:
                article_tags.append(article_tag)

    return [(get_article_title(t), get_article_link(t), get_content(get_article_link(t), browser)) for t in article_tags]

if __name__ == '__main__':
    search_terms = ['nutrition', 'food', 'eat', 'meal', 'formula', 'nutrients', 'vitamins', 'supplements', 'diet', 'wellness',]
    corpus = build_corpus(search_terms, browser)
    ! touch what_to_expect.csv
    with open('what_to_expect.csv', 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(corpus)

# reference: https://docs.python.org/3/library/time.html
import time

# reference: https://docs.python-requests.org/en/master/
import requests
from parsel import Selector
from tech_news.database import create_news


# Requisito 1
def fetch(url):
    try:
        r = requests.get(url, timeout=3)
        time.sleep(1)
        if r.status_code == 200:
            return r.text
        else:
            return None
    except requests.ReadTimeout:
        return None


# Requisito 2
def scrape_noticia(html_content):
    selector = Selector(text=html_content)

    url = selector.css("meta[property='og:url']::attr(content)").get()

    title = selector.css(".tec--article__header__title::text").get()

    timestamp = selector.css("#js-article-date::attr(datetime)").get()

    writer = selector.css(".tec--author__info__link::text").get()
    if writer:
        writer = writer.strip()
    else:
        writer = None

    shares_count = selector.css(".tec--toolbar__item::text").get()
    if shares_count:
        shares_count = int((shares_count.strip()).split(" ")[0])
    else:
        shares_count = 0

    comments_count = selector.css("#js-comments-btn::attr(data-count)").get()
    if comments_count:
        comments_count = int(comments_count)
    else:
        comments_count = 0

    summary = "".join(selector.css(
        ".tec--article__body > p:first-child *::text").getall())

    sources = [src.strip() for src in selector.css(
        ".z--mb-16 div a.tec--badge::text").getall()]

    categories = [cat.strip() for cat in selector.css(
        "#js-categories .tec--badge::text").getall()]

    return {
        "url": url,
        "title": title,
        "timestamp": timestamp,
        "writer": writer,
        "shares_count": shares_count,
        "comments_count": comments_count,
        "summary": summary,
        "sources": sources,
        "categories": categories,
    }


# Requisito 3
def scrape_novidades(html_content):
    selector = Selector(text=html_content)
    if selector:
        return selector.css(
            "h3.tec--card__title a.tec--card__title__link::attr(href)"
            ).getall()
    else:
        return []


# Requisito 4
def scrape_next_page_link(html_content):
    selector = Selector(text=html_content)
    link = selector.css("div.tec--list a.tec--btn::attr(href)").get()
    if link:
        return link
    else:
        return None


# Requisito 5
def get_tech_news(amount):
    url = "https://www.tecmundo.com.br/novidades"
    news = []
    while len(news) < amount:
        html_content = fetch(url)
        url_news = scrape_novidades(html_content)
        news.extend(url_news)
        url = scrape_next_page_link(html_content)
    news = news[0:amount]
    news_list = [
        scrape_noticia(fetch(new)) for new in news
    ]
    create_news(news_list)
    return news_list

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import schedule
import time

def crawl_dantri():
    base_url = 'https://dantri.com.vn/cong-nghe.htm'
    articles = []
    page = 1
    while True:
        url = f"{base_url}?page={page}"
        print(f"Crawling {url}...")
        response = requests.get(url)
        if response.status_code != 200:
            print("No more pages or error.")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('article')
        
        if not news_items:
            break
        
        for item in news_items:
            try:
                title_tag = item.find('h3')
                title = title_tag.text.strip() if title_tag else ''
                
                description_tag = item.find('div', class_='description')
                description = description_tag.text.strip() if description_tag else ''
                
                img_tag = item.find('img')
                img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ''
                
                link_tag = title_tag.find('a') if title_tag else None
                link = 'https://dantri.com.vn' + link_tag['href'] if link_tag else ''
                
                content = ''
                if link:
                    article_resp = requests.get(link)
                    article_soup = BeautifulSoup(article_resp.text, 'html.parser')
                    content_div = article_soup.find('div', class_='dt-news__content')
                    content = content_div.get_text(separator='\n').strip() if content_div else ''
                
                articles.append({
                    'Title': title,
                    'Description': description,
                    'Image URL': img_url,
                    'Content': content,
                    'Link': link,
                    'Crawl Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                print(f"Error parsing article: {e}")
        
        page += 1

    df = pd.DataFrame(articles)
    filename = f'dantri_articles_{datetime.now().strftime("%Y%m%d")}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Saved {len(articles)} articles to {filename}")

schedule.every().day.at("06:00").do(crawl_dantri)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(60)

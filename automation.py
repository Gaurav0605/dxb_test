from flask import Flask, render_template_string, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# HTML template with structured and styled display
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest News from Various Sources</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        h1 {
            color: #333;
        }
        .news-container {
            background-color: #fff;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .news-container ul {
            padding: 0;
            list-style: none;
        }
        .news-container ul li {
            padding: 10px 0;
            border-bottom: 1px solid #ddd;
        }
        .news-container ul li:last-child {
            border-bottom: none;
        }
        .news-item {
            margin-bottom: 20px;
        }
        .news-item img {
            max-width: 100px;
            display: block;
            margin-bottom: 10px;
        }
        .news-item a {
            color: #007bff;
            text-decoration: none;
        }
        .news-item a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Government of India</h1>
        <div class="news-container" id="output"></div>
        
        <h1>Abu Dhabi Latest News</h1>
        <div class="news-container" id="abu_dhabi_output"></div>
        
        <h1>Ajman Media Office</h1>
        <div class="news-container" id="ajman_output"></div>

        <h1>ARAB News</h1>
        <div class="news-container" id="arab_news_output"></div>
        
        <h1>The Peninsula</h1>
        <div class="news-container" id="peninsula_output"></div>
        
        <h1>Gulf News</h1>
        <div class="news-container" id="gulfnews_output"></div>
    </div>
    
    <script>
        async function fetchNews() {
            const endpoints = ['/scrape', '/scrape-abu-dhabi', '/scrape-ajman', '/scrape-arab-news', '/scrape-peninsula', '/scrape-gulfnews'];
            const results = await Promise.all(endpoints.map(endpoint => fetch(endpoint).then(res => res.json())));
            
            document.getElementById('output').innerHTML = results[0].result;
            document.getElementById('abu_dhabi_output').innerHTML = results[1].result;
            document.getElementById('ajman_output').innerHTML = results[2].result;
            document.getElementById('arab_news_output').innerHTML = results[3].result;
            document.getElementById('peninsula_output').innerHTML = results[4].result;
            document.getElementById('gulfnews_output').innerHTML = results[5].result;
        }
        
        fetchNews();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/scrape')
def scrape():
    url = 'https://pib.gov.in/Allrel.aspx'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    h3_elements = soup.find_all('h3', class_='font104')

    result = "<ul>"
    for h3 in h3_elements:
        result += f"<li><strong>{h3.get_text()}:</strong><ul>"
        ul = h3.find_next('ul', class_='num')
        if ul:
            links = ul.find_all('a')
            for link in links:
                result += f"<li><a href='{link['href']}' target='_blank'>{link['title']}</a></li>"
        result += "</ul></li>"
    result += "</ul>"
    
    return jsonify({'result': result})

@app.route('/scrape-abu-dhabi')
def scrape_abu_dhabi():
    url = 'https://www.mediaoffice.abudhabi/en/latest-news/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    articles = soup.find_all('div', class_='content')

    result = "<ul>"
    for article in articles:
        title = article.find('h3', class_='title')
        if title:
            title_text = title.get_text(strip=True)
            category = article.find('p', class_='metadata').get_text(strip=True)
            result += f"<li><strong>{title_text}:</strong> {category}</li>"
    result += "</ul>"
    
    return jsonify({'result': result})

@app.route('/scrape-ajman')
def scrape_ajman():
    url = 'https://amcfz.ae/en/category/news/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    articles = soup.find_all('article', class_='post')

    result = "<ul>"
    for article in articles:
        title = article.find('h2', class_='title-post entry-title').get_text(strip=True)
        link = article.find('a')['href']
        excerpt = article.find('div', class_='entry-post').get_text(strip=True)
        result += f"<li><strong>{title}:</strong> <a href='{link}' target='_blank'>{link}</a><br>{excerpt}</li>"
    result += "</ul>"
    
    return jsonify({'result': result})

@app.route('/scrape-arab-news')
def scrape_arab_news():
    url = 'https://www.arabtimesonline.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    articles = soup.find_all('div', class_='article')
    
    seen_urls = set()

    result = "<ul>"
    for article in articles:
        title_tag = article.find('div', class_='article-title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'
        
        subtitle_tag = article.find('div', class_='article-subtitle')
        subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else 'No subtitle'
        
        link_tag = title_tag.find('a') if title_tag else None
        article_url = link_tag['href'] if link_tag else 'No URL'
        
        img_tag = article.find('img')
        img_url = img_tag['src'] if img_tag else 'No image URL'
        
        pub_date_tag = article.find('span', class_='time')
        pub_date = pub_date_tag.get_text(strip=True) if pub_date_tag else 'No date'
        
        if article_url not in seen_urls:
            seen_urls.add(article_url)
            result += f"<li><strong>Title:</strong> {title}<br><strong>Subtitle:</strong> {subtitle}<br><strong>Article URL:</strong> <a href='{article_url}' target='_blank'>{article_url}</a><br><strong>Image URL:</strong> <img src='{img_url}' alt='Image' style='max-width:100px;'><br><strong>Published Date:</strong> {pub_date}</li>"
    result += "</ul>"
    
    return jsonify({'result': result})

@app.route('/scrape-peninsula')
def scrape_peninsula():
    url = 'https://thepeninsulaqatar.com/category/News'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    news_items = soup.find_all('div', class_='col-sm-6 item')

    # Create a dictionary to store categorized news
    news_by_category = {
        'General': [],
        'International': [],
        'Local': []
        # Add more categories as needed
    }

    result = "<ul>"
    for item in news_items:
        # Extract title
        title = item.find('a', class_='title').text.strip()
        
        # Extract date
        date = item.find('span').text.strip()
        
        # Extract description
        description = item.find('p', class_='search').text.strip()
        
        # Extract image URL
        img_tag = item.find('a', class_='photo').find('img')
        img_url = img_tag['src'] if img_tag else 'No Image Available'
        
        # Complete the URL if it is relative
        if img_url.startswith('/'):
            img_url = 'https://thepeninsulaqatar.com' + img_url
        
        # Assuming you have some logic to determine category; here it's set to 'General'
        category = 'General'  # Modify this based on your actual categorization logic
        
        # Create a news item dictionary
        news_item = {
            'title': title,
            'date': date,
            'description': description,
            'image_url': img_url
        }
        
        # Append the news item to the appropriate category
        if category in news_by_category:
            news_by_category[category].append(news_item)
        else:
            # Handle unknown categories if needed
            news_by_category['General'].append(news_item)

    for category, items in news_by_category.items():
        result += f"<li><strong>Category: {category}</strong><ul>"
        for item in items:
            result += f"<li><strong>Title:</strong> {item['title']}<br><strong>Date:</strong> {item['date']}<br><strong>Description:</strong> {item['description']}<br><strong>Image:</strong> <img src='{item['image_url']}' alt='Image' style='max-width:100px;'></li>"
        result += "</ul></li>"
    result += "</ul>"

    return jsonify({'result': result})

@app.route('/scrape-gulfnews')
def scrape_gulfnews():
    url = 'https://gulfnews.com/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    sections = soup.find_all('section', class_='sc-container')

    result = "<ul>"
    for section in sections:
        cards = section.find_all('div', class_='card')
        
        for card in cards:
            title_tag = card.find('h2', class_='card-title')
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            
            link_tag = title_tag.find('a') if title_tag else None
            link = link_tag['href'] if link_tag else "No link found"
            
            img_tag = card.find('img', class_='card-img')
            img_url = img_tag['data-src'] if img_tag and 'data-src' in img_tag.attrs else img_tag['src'] if img_tag else "No image found"
            
            category_tag = card.find('a', class_='card-category')
            category = category_tag.get_text(strip=True) if category_tag else "No category found"
            
            result += f"<li><strong>Category:</strong> {category}<br><strong>Title:</strong> {title}<br><strong>Link:</strong> <a href='{url.rstrip('/')}{link}' target='_blank'>{url.rstrip('/')}{link}</a><br><strong>Image URL:</strong> <img src='{img_url}' alt='Image' style='max-width:100px;'><br></li>"
            result += "<hr>"  # To separate each news item

    result += "</ul>"
    
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)

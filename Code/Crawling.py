import streamlit as st
import pandas as pd
import json
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import re
from collections import Counter
import sys
import importlib.util
from io import StringIO
import contextlib

# Import the IMDb scraper functionality
# The functions we need from the original script
import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import logging
import base64
from datetime import datetime

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import random
import logging
import os
import shutil # Import shutil for get_chromedriver_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@st.cache_resource
# def initialize_driver():
#     """Initialize WebDriver optimized for Streamlit Cloud"""
#     chrome_options = Options()
#     chrome_options.add_argument("--headless") # Wajib untuk lingkungan tanpa UI
#     chrome_options.add_argument("--no-sandbox") # Penting untuk lingkungan Linux/Docker
#     chrome_options.add_argument("--disable-dev-shm-usage") # Penting untuk lingkungan Linux/Docker
#     chrome_options.add_argument("--disable-gpu") # Penting untuk lingkungan headless
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument("--single-process") # Dapat membantu di beberapa lingkungan cloud
#     chrome_options.add_argument("--disable-extensions")
#     chrome_options.add_argument("--disable-plugins")
#     # chrome_options.add_argument("--disable-images") # Aktifkan jika Anda ingin menghemat bandwidth/memori
#     # chrome_options.add_argument("--disable-javascript") # Hapus jika Anda membutuhkan JS untuk halaman
#     chrome_options.add_argument("--remote-debugging-port=9222")
#     chrome_options.add_argument("--ignore-certificate-errors") # Dapat membantu jika ada masalah SSL

#     user_agents = [
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
#         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
#     ]
#     chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
#     chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#     chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     chrome_options.add_experimental_option("useAutomationExtension", False)

#     driver = None
#     try:
#         logger.info("Attempting to initialize Chrome WebDriver...")
#         # Prioritaskan chromedriver yang diinstal sistem (via packages.txt)
#         system_chromedriver_path = shutil.which('chromedriver') # Cari 'chromedriver' di PATH sistem
#         if system_chromedriver_path:
#             logger.info(f"Using system-installed chromedriver at: {system_chromedriver_path}")
#             service = Service(executable_path=system_chromedriver_path)
#             driver = webdriver.Chrome(service=service, options=chrome_options)
#             logger.info("Successfully initialized with system-installed chromedriver.")
#         else:
#             logger.warning("System-installed chromedriver not found. Falling back to webdriver-manager.")
#             # Fallback ke webdriver-manager jika chromedriver sistem tidak ditemukan
#             driver_path = ChromeDriverManager().install()
#             service = Service(driver_path)
#             driver = webdriver.Chrome(service=service, options=chrome_options)
#             logger.info(f"Successfully initialized with webdriver-manager.")

#         # Anti-detection scripts (tetap dipertahankan)
#         try:
#             driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
#                 "source": """
#                     Object.defineProperty(navigator, 'webdriver', {
#                         get: () => undefined
#                     });
#                     Object.defineProperty(navigator, 'plugins', {
#                         get: () => [1, 2, 3, 4, 5] // Simulasikan plugin
#                     });
#                     Object.defineProperty(navigator, 'languages', {
#                         get: () => ['en-US', 'en'] // Simulasikan bahasa
#                     });
#                     const originalQuery = window.navigator.permissions.query;
#                     window.navigator.permissions.query = (parameters) => (
#                         parameters.name === 'notifications' ?
#                             Promise.resolve({state: Notification.permission}) :
#                             originalQuery(parameters)
#                     );
#                 """
#             })
#         except Exception as e:
#             logger.warning(f"Could not execute anti-detection script: {e}")
#         return driver
#     except Exception as e:
#         logger.error(f"Failed to initialize WebDriver: {e}")
#         st.error(f"Gagal menginisialisasi WebDriver: {e}")
#         if driver:
#             driver.quit() # Pastikan driver ditutup jika terjadi kesalahan
#         raise

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920x1080")

    # Penting: Tentukan path ke binary Chromium yang terinstal di Streamlit Cloud
    # Browser yang terinstal adalah Chromium (versi 120.x) di /usr/bin/chromium
    service = ChromeService(ChromeDriverManager(
        chrome_type="chromium", # Tentukan tipe browser
        version=None, # Biarkan webdriver-manager mendeteksi versi dari binary
        path="/home/appuser/.wdm/drivers/chromedriver/" # Opsional: jika ingin mengontrol lokasi cache
    ).install())

    # Atau cara yang lebih sederhana dan sering berhasil:
    # Biarkan webdriver-manager mencoba menebak versi dari opsi browser
    # service = ChromeService(ChromeDriverManager().install())
    # chrome_options.binary_location = "/usr/bin/chromium" # Set lokasi binary Chromium

    # Alternatif yang lebih eksplisit jika cara di atas tidak berhasil:
    # Anda juga bisa mencoba secara langsung mendefinisikan versi chromedriver
    # jika Anda yakin dengan versi Chromium yang diinstal (misal 120.0.6099.224)
    # service = ChromeService(ChromeDriverManager(version="120.0.6099.109").install())
    # chrome_options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
    

def random_delay(min_seconds=2, max_seconds=5):
    """Add a random delay between requests to avoid detection"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def take_screenshot(driver, name="screenshot"):
    """Save a screenshot for debugging purposes"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    logger.info(f"Screenshot saved to {filename}")

def search_movie_by_title(movie_title, driver):
    """Search for a movie by title using Selenium WebDriver with improved year extraction"""
    search_url = f"https://www.imdb.com/find/?q={movie_title.replace(' ', '+')}&s=tt&exact=true"
    
    logger.info(f"Searching with URL: {search_url}")
    
    try:
        # Visit the IMDb homepage first to get cookies
        driver.get("https://www.imdb.com/")
        random_delay(2, 4)
        
        # Now navigate to the search URL
        driver.get(search_url)
        random_delay(3, 7)
        
        # Take a screenshot of search results
        take_screenshot(driver, "search_results")
        
        # Wait for search results to appear - updated selectors for 2025 IMDb
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".find-result-item, .ipc-metadata-list-summary-item"))
            )
        except TimeoutException:
            logger.warning("Timeout waiting for search results. Checking for any results format.")

        # Parse the page using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Save HTML for debugging
        with open(f"debug_search_{movie_title.replace(' ', '_')}.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        
        # Find movie results
        search_results = []
        
        # Try multiple possible selectors for results
        result_selectors = [
            '.find-result-item',                # Current IMDb (2025)
            '.ipc-metadata-list-summary-item',  # Alternative format
            '.findResult',                      # Legacy format
            'li.ipc-list__item'                 # Generic list items
        ]
        
        result_items = []
        for selector in result_selectors:
            result_items = soup.select(selector)
            if result_items:
                logger.info(f"Found {len(result_items)} results using selector: {selector}")
                break
        
        if not result_items:
            # Try alternative search format
            alternative_url = f"https://www.imdb.com/search/title/?title={movie_title.replace(' ', '+')}"
            logger.info(f"No results found. Trying alternative search: {alternative_url}")
            
            driver.get(alternative_url)
            random_delay(3, 5)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            result_items = soup.select('.lister-item')
        
        # Process search results with improved year extraction
        for item in result_items:
            try:
                # Find the title link - try multiple possible selectors
                link = (
                    item.select_one('a[href*="/title/tt"]') or 
                    item.select_one('.ipc-metadata-list-summary-item__t') or
                    item.select_one('.result_text a') or
                    item.select_one('a[data-testid="title"]')
                )
                
                if not link:
                    continue
                
                title = link.text.strip()
                href = link.get('href', '')
                
                # Extract IMDb ID
                imdb_id_match = re.search(r'/title/(tt\d+)/?', href)
                if not imdb_id_match:
                    continue
                
                imdb_id = imdb_id_match.group(1)
                
                # Enhanced year extraction - try multiple approaches
                year = "Unknown"
                
                # Method 1: Look for year in parentheses directly next to the title
                year_next_to_title = re.search(r'(.+?)(?:\s*\((\d{4})\))', title)
                if year_next_to_title:
                    title = year_next_to_title.group(1).strip()
                    year = year_next_to_title.group(2)
                else:
                    # Method 2: Look for specific year elements by class
                    year_element = item.select_one('.year-text, .lister-item-year, .image-year')
                    if year_element:
                        year_text = year_element.text.strip()
                        year_match = re.search(r'(\d{4})', year_text)
                        if year_match:
                            year = year_match.group(1)
                    else:
                        # Method 3: Look for spans containing typical year format
                        for span in item.select('span'):
                            span_text = span.text.strip()
                            if re.match(r'^\(\d{4}\)$', span_text) or re.match(r'^\d{4}$', span_text):
                                year_match = re.search(r'(\d{4})', span_text)
                                if year_match:
                                    year = year_match.group(1)
                                    break
                        
                        # Method 4: Look for year in any text nearby
                        if year == "Unknown":
                            # Search in surrounding text within this item
                            item_text = item.text
                            # Look for patterns like (2009) or (2009-2023)
                            surrounding_year = re.search(r'\((\d{4})(?:-\d{4})?\)', item_text)
                            if surrounding_year:
                                year = surrounding_year.group(1)
                
                # Method 5: If we have the IMDb ID, we can try to fetch the year via additional API or page load
                # This is a more expensive operation, so we use it as a last resort
                if year == "Unknown" and random.random() < 0.2:  # Only try for ~20% of unknown years to avoid overloading
                    try:
                        # Try getting year from title page meta info
                        title_url = f"https://www.imdb.com/title/{imdb_id}/"
                        # Use requests instead of Selenium for speed
                        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
                        title_response = requests.get(title_url, headers=headers, timeout=5)
                        if title_response.status_code == 200:
                            title_soup = BeautifulSoup(title_response.text, 'html.parser')
                            # Look for year in meta tags or JSON-LD
                            meta_year = None
                            # Try JSON-LD data
                            script_tags = title_soup.find_all("script", type="application/ld+json")
                            for script in script_tags:
                                try:
                                    json_data = json.loads(script.string)
                                    if isinstance(json_data, dict) and 'datePublished' in json_data:
                                        date_str = json_data['datePublished']
                                        meta_year = re.search(r'(\d{4})', date_str).group(1)
                                        break
                                except (json.JSONDecodeError, AttributeError):
                                    continue
                            
                            if meta_year:
                                year = meta_year
                    except Exception as e:
                        logger.debug(f"Failed to fetch additional year info for {imdb_id}: {e}")
                
                # Clean the title if it still contains year info
                title = re.sub(r'\s*\(\d{4}(?:-\d{4})?\)\s*', '', title)
                
                 # Extract image URL - look for movie poster image
                image_url = None
                
                # Try multiple methods to find the image
                # Method 1: Look for img tag within the search result item
                img_element = item.select_one('img.ipc-image, img.loadlate, img[src*="media-amazon"], img[data-src*="media-amazon"]')
                if img_element:
                    # Get the actual image URL, considering both src and data-src attributes
                    image_url = img_element.get('src') or img_element.get('data-src')
                    
                    # Check if we got a low-quality placeholder - look for higher quality version
                    # if image_url and ('_V1_UY74_' in image_url or '_V1_UX50_' in image_url):
                        # Transform URL to get higher resolution
                        # Example: https://m.media-amazon.com/images/M/MV5BMT...._V1_UY74_CR0,0,50,74_.jpg
                        # to: https://m.media-amazon.com/images/M/MV5BMT...._V1_SX300.jpg
                    base_url = re.sub(r'_V1_.*?.jpg', '', image_url)
                    if base_url:
                        image_url = f"{base_url}QL75_UY148_CR0,0,100,148_.jpg"
                
                # Method 2: If no image found and we have IMDb ID, try to get from metadata
                if not image_url and random.random() < 0.3:  # Only try for ~30% to avoid overloading
                    try:
                        # Only do this if we haven't already loaded the page for year info
                        if year != "Unknown" or random.random() < 0.15:
                            title_url = f"https://www.imdb.com/title/{imdb_id}/"
                            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
                            title_response = requests.get(title_url, headers=headers, timeout=5)
                            if title_response.status_code == 200:
                                title_soup = BeautifulSoup(title_response.text, 'html.parser')
                                
                                # Try to find image in JSON-LD
                                script_tags = title_soup.find_all("script", type="application/ld+json")
                                for script in script_tags:
                                    try:
                                        json_data = json.loads(script.string)
                                        if isinstance(json_data, dict) and 'image' in json_data:
                                            if isinstance(json_data['image'], str):
                                                image_url = json_data['image']
                                                break
                                            elif isinstance(json_data['image'], dict) and 'url' in json_data['image']:
                                                image_url = json_data['image']['url']
                                                break
                                    except (json.JSONDecodeError, AttributeError):
                                        continue
                                
                                # Try to find the poster image directly
                                if not image_url:
                                    poster_img = title_soup.select_one('img.ipc-image[srcset*="media-amazon"], img.poster[src*="media-amazon"]')
                                    if poster_img:
                                        image_url = poster_img.get('src')
                    except Exception as e:
                        logger.debug(f"Failed to fetch image for {imdb_id}: {e}")
                
                # Add to search results
                search_results.append({
                    'title': title,
                    'year': year,
                    'imdb_id': imdb_id,
                    'image_url': image_url  # Add the extracted image URL to the dictionary
                })
            except Exception as e:
                logger.error(f"Error parsing result: {e}")
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return []

def diagnose_review_page(page_source, imdb_id):
    """Output diagnostic information about the page structure"""
    soup = BeautifulSoup(page_source, 'html.parser')
    
    logger.info("------- DIAGNOSTIC INFO -------")
    
    # Save full HTML for inspection
    debug_file = f"debug_fullpage_{imdb_id}.html"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    logger.info(f"Saved full HTML to {debug_file}")
    
    # Check for specific 2025 IMDb review section structure
    review_section = soup.select_one("section.ipc-page-section--sp-pageMargin")
    if review_section:
        logger.info("Found main review section container")
        
        # Look for article elements which should contain reviews
        articles = review_section.select("article")
        logger.info(f"Found {len(articles)} article elements in review section")
        
        # Examine first few articles
        for i, article in enumerate(articles[:3]):
            logger.info(f"Article {i+1} classes: {article.get('class', 'none')}")
            logger.info(f"Article {i+1} contains {len(article.select('div'))} div elements")
            
            # Check for review card structure
            review_card = article.select_one(".ipc-list-card")
            if review_card:
                logger.info(f"Article {i+1} contains review card structure")
                
                # Check for review content
                review_content = article.select_one(".review-content")
                if review_content:
                    logger.info(f"Found review content: {review_content.text[:50]}...")
                else:
                    logger.info("No specific review content class found")
                    
                # Check for HTML content
                html_content = article.select_one(".ipc-html-content")
                if html_content:
                    logger.info(f"Found HTML content section: {html_content.text[:50]}...")
    else:
        logger.warning("Could not find main review section container")
    
    # Check for common review indicators
    potential_patterns = [
        'user review', 'out of 10', 'rated this', 'review title', 
        'spoiler alert', 'was this review helpful'
    ]
    
    for pattern in potential_patterns:
        matches = soup.find_all(string=re.compile(pattern, re.IGNORECASE))
        if matches:
            logger.info(f"Found {len(matches)} elements containing '{pattern}'")
    
    # Check for pagination or load more elements
    load_more = soup.select('button.ipc-see-more__button, [data-testid="load-more"], .load-more')
    if load_more:
        logger.info(f"Found {len(load_more)} potential 'load more' elements")
        for elem in load_more[:2]:
            logger.info(f"Load more element: {elem.get('class', 'none')}, text: {elem.text.strip()}")
    
    logger.info("------- END DIAGNOSTIC INFO -------")

def extract_review_from_article(article):
    """Extract review details from a 2025 IMDb article element"""
    review_data = {}
    
    try:
        # Extract reviewer name and URL from the user info section
        user_info = article.select_one("ul li a")
        if user_info:
            review_data['reviewer_name'] = user_info.text.strip()
            review_data['reviewer_url'] = user_info.get('href', '')
        
        # Extract review date
        date_element = article.select_one("ul li:nth-child(2)")
        if date_element:
            review_data['review_date'] = date_element.text.strip()
        
        # Extract rating if available
        rating_element = article.select_one("span.ipc-rating-star")
        if rating_element:
            rating_text = rating_element.text.strip()
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                review_data['rating_value'] = rating_match.group(1)
        
        # Extract short review (title)
        title_element = article.select_one("div.edCLQz > div")
        if title_element:
            review_data['short_review'] = title_element.text.strip()
        
        # Try multiple selectors for full review content
        content_element = None
        
        # First try the precise selector provided
        content_element = article.select_one("div.ipc-list-card--border-speech div.ipc-list-card__content div:nth-child(3) div.ipc-html-content.ipc-html-content--base.review-content div")
        
        # If that fails, try the original selector
        if not content_element:
            content_element = article.select_one(".ipc-html-content.review-content")
            
        # Additional fallback selector
        if not content_element:
            content_element = article.select_one("div.ipc-html-content--base")
        
        if content_element:
            review_data['full_review'] = content_element.text.strip()
        
        # Extract review ID
        review_data['data-review-id'] = article.get('id', '')
        
        # Check if we got meaningful data
        if not (review_data.get('short_review') or review_data.get('full_review')):
            logger.debug("Could not extract essential review text")
            return None
            
        return review_data
    
    except Exception as e:
        logger.error(f"Error extracting review from article: {e}")
        return None
    
def scrape_reviews_page_2025(page_source, imdb_id):
    """Extract reviews from the 2025 IMDb page structure"""
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Debug: Save the HTML to examine the structure
    with open(f"debug_imdb_{imdb_id}.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    
    logger.info(f"Saved debug HTML to debug_imdb_{imdb_id}.html")
    
    # First try to find the main review section
    review_section = soup.select_one("section.ipc-page-section--sp-pageMargin")
    
    reviews_data = {
        'ImdbId': imdb_id,
        'reviews': []
    }
    
    if review_section:
        logger.info("Found main review section container")
        
        # Find all article elements which contain individual reviews
        articles = review_section.select("article")
        logger.info(f"Found {len(articles)} article elements that might contain reviews")
        
        for article in articles:
            review_data = extract_review_from_article(article)
            if review_data:
                reviews_data['reviews'].append(review_data)
    
    if not reviews_data['reviews']:
        logger.warning("Could not find reviews using 2025 structure. Running diagnostics...")
        diagnose_review_page(page_source, imdb_id)
        
        # Fallback to generic scraping approach
        return scrape_reviews_page_generic(page_source, imdb_id)
    
    return reviews_data

def scrape_reviews_page_generic(page_source, imdb_id):
    """Generic fallback method to find review-like content"""
    soup = BeautifulSoup(page_source, 'html.parser')
    
    reviews_data = {
        'ImdbId': imdb_id,
        'reviews': []
    }
    
    # Look for elements that might contain reviews based on content
    potential_reviews = []
    
    # Look for divs with substantial text content
    for div in soup.find_all(['div', 'article', 'section']):
        text = div.text.strip()
        if len(text) > 200:  # Minimum length for review content
            # Check if it has review-like content
            lower_text = text.lower()
            if any(marker in lower_text for marker in ['review', 'rating', 'stars', 'out of 10', 'recommended']):
                potential_reviews.append(div)
    
    logger.info(f"Found {len(potential_reviews)} potential review-like elements")
    
    # Process these potential reviews
    for i, element in enumerate(potential_reviews):
        try:
            review_data = {}
            
            # Try to extract review title
            title_candidates = element.find_all(['h3', 'h4', 'strong', 'b'])
            if title_candidates:
                review_data['short_review'] = title_candidates[0].text.strip()
            
            # Extract main text content
            paragraphs = element.find_all('p')
            if paragraphs:
                review_data['full_review'] = ' '.join([p.text.strip() for p in paragraphs])
            else:
                # If no paragraphs, use the element's text
                review_data['full_review'] = element.text.strip()
            
            # Look for rating patterns
            rating_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:/\s*10|stars?)', element.text)
            if rating_match:
                review_data['rating_value'] = rating_match.group(1)
            
            # Look for date patterns
            date_match = re.search(r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}', element.text)
            if date_match:
                review_data['review_date'] = date_match.group(0)
            
            # Only add if we have meaningful content
            if review_data.get('full_review') and len(review_data['full_review']) > 50:
                # Create a unique ID
                review_data['data-review-id'] = f"generic_{i}"
                reviews_data['reviews'].append(review_data)
        
        except Exception as e:
            logger.error(f"Error processing potential review: {e}")
    
    return reviews_data

def scroll_page(driver, amount=None):
    """Scroll the page down to load lazy content"""
    if amount:
        driver.execute_script(f"window.scrollBy(0, {amount});")
    else:
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Give time for content to load

def click_load_more(driver):
    """Try to click the 'Load More' button using various approaches"""
    load_more_selectors = [
        "button.ipc-see-more__button",
        "button.load-more",
        "[data-testid='load-more']",
        ".ipc-pagination__next-button",
        ".see-more button",
        ".ipl-load-more__button"
    ]
    
    for selector in load_more_selectors:
        try:
            # Try to find the button
            load_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            
            # Scroll to make button visible
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", load_more)
            time.sleep(1)
            
            # Try to click
            try:
                load_more.click()
                logger.info(f"Clicked 'Load More' button using selector: {selector}")
                return True
            except Exception as e:
                # If normal click fails, try JavaScript click
                logger.info(f"Normal click failed: {e}. Trying JavaScript click.")
                driver.execute_script("arguments[0].click();", load_more)
                logger.info(f"Used JavaScript to click 'Load More' button")
                return True
                
        except TimeoutException:
            continue
    
    # If all selectors failed, try using JavaScript to find and click any button that looks like "Load More"
    try:
        clicked = driver.execute_script("""
            // Find buttons with "load more" or "next" text
            var buttons = Array.from(document.querySelectorAll('button, [role="button"], a.ipc-button'));
            
            for (var i = 0; i < buttons.length; i++) {
                var btn = buttons[i];
                var text = btn.textContent.toLowerCase();
                
                if (text.includes('load more') || text.includes('show more') || text.includes('next')) {
                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                    setTimeout(() => {}, 500);
                    btn.click();
                    return true;
                }
            }
            
            return false;
        """)
        
        if clicked:
            logger.info("Found and clicked 'Load More' button using JavaScript")
            return True
    except Exception as e:
        logger.error(f"JavaScript click attempt failed: {e}")
    
    logger.info("No 'Load More' button found or clickable")
    return False

def scrape_all_reviews(imdb_id, driver, max_pages=None):
    """Scrape all review pages for a movie using Selenium with improved 2025 support"""
    reviews_url = f"https://www.imdb.com/title/{imdb_id}/reviews"
    all_reviews = []
    
    logger.info(f"Opening reviews page: {reviews_url}")
    driver.get(reviews_url)
    random_delay(3, 7)
    
    # Accept cookies if the dialog appears
    try:
        cookie_selectors = [
            "button[id*='accept']",
            "button[data-testid='accept']",
            ".ipc-button--accept-cookies",
            ".accept-cookies"
        ]
        
        for selector in cookie_selectors:
            try:
                accept_button = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                accept_button.click()
                logger.info(f"Accepted cookies using selector: {selector}")
                random_delay(1, 2)
                break
            except TimeoutException:
                continue
    except Exception:
        logger.info("No cookie prompt found or already accepted")

    # Take screenshot of initial review page
    take_screenshot(driver, f"reviews_initial_{imdb_id}")
    
    # Initial scroll to trigger lazy loading
    scroll_page(driver)
    
    # Get initial reviews
    data = scrape_reviews_page_2025(driver.page_source, imdb_id)
    if data['reviews']:
        all_reviews.extend(data['reviews'])
        logger.info(f"Found {len(data['reviews'])} reviews on initial page")
    else:
        logger.warning("No reviews found on initial page. Trying alternative approach...")
        
        # Try refreshing the page and waiting longer
        driver.refresh()
        random_delay(5, 10)
        scroll_page(driver)
        
        # Try again
        data = scrape_reviews_page_2025(driver.page_source, imdb_id)
        if data['reviews']:
            all_reviews.extend(data['reviews'])
            logger.info(f"Found {len(data['reviews'])} reviews after refresh")
        else:
            logger.warning("Still no reviews found. Is the movie very new or has no reviews?")
    
    # Keep track of page count and continue loading more reviews if available
    page_count = 1
    attempt_count = 0
    max_attempts = 5  # Maximum attempts to load more content if no new reviews appear
    
    # Continue loading more reviews until we reach the limit or no more are available
    while (max_pages is None or page_count < max_pages) and attempt_count < max_attempts:
        # Remember current review count
        current_review_count = len(all_reviews)
        
        # Try to click "Load More" button
        if click_load_more(driver):
            # Wait for new content to load
            random_delay(3, 6)
            
            # Scroll to ensure new content is rendered
            scroll_page(driver)
            
            # Take screenshot after loading more
            take_screenshot(driver, f"reviews_more_{imdb_id}_page{page_count}")
            
            # Extract new reviews
            data = scrape_reviews_page_2025(driver.page_source, imdb_id)
            
            # Check if we got new reviews
            if data['reviews'] and len(data['reviews']) > current_review_count:
                # If we have new reviews, reset attempt counter
                new_reviews = data['reviews'][current_review_count:]
                all_reviews.extend(new_reviews)
                page_count += 1
                attempt_count = 0
                logger.info(f"Loaded page {page_count}: Found {len(new_reviews)} new reviews (Total: {len(all_reviews)})")
            else:
                # No new reviews, increment attempt counter
                attempt_count += 1
                logger.info(f"No new reviews loaded (attempt {attempt_count}/{max_attempts})")
                
                # Try scrolling more and waiting
                scroll_page(driver)
                random_delay(2, 4)
        else:
            # No more "Load More" button found
            logger.info("No more 'Load More' button found, reached end of reviews")
            break
    
    # Remove potential duplicates
    unique_reviews = []
    seen_reviews = set()
    
    for review in all_reviews:
        # Create a hash of review content to identify duplicates
        review_hash = hash((review.get('full_review', '') or '') + 
                           (review.get('short_review', '') or '') + 
                           (review.get('reviewer_name', '') or ''))
        
        if review_hash not in seen_reviews:
            seen_reviews.add(review_hash)
            unique_reviews.append(review)
    
    if len(unique_reviews) < len(all_reviews):
        logger.info(f"Removed {len(all_reviews) - len(unique_reviews)} duplicate reviews")
    
    result = {
        'ImdbId': imdb_id,
        'total_reviews': len(unique_reviews),
        'reviews': unique_reviews
    }
    
    return result

def get_movie_reviews_by_title(movie_title, max_pages=None):
    """Main function to get reviews by movie title using Selenium"""
    logger.info(f"\nSearching for movie: {movie_title}")
    
    driver = initialize_driver()
    
    try:
        # Search for the movie
        search_results = search_movie_by_title(movie_title, driver)
        
        if not search_results:
            logger.warning("No movies found matching that title.")
            return None
        
        # Display search results
        print("\nFound the following movies:")
        for i, movie in enumerate(search_results, 1):
            print(f"{i}. {movie['title']} ({movie['year']}) - {movie['imdb_id']}")
        
        # Let user choose a movie or use first result in automated mode
        selected_movie = None
        if len(search_results) == 1:
            selected_movie = search_results[0]
            print(f"Auto-selecting the only result: {selected_movie['title']}")
        else:
            try:
                choice = int(input(f"\nSelect a movie (1-{len(search_results)}): "))
                if 1 <= choice <= len(search_results):
                    selected_movie = search_results[choice-1]
                else:
                    logger.error("Invalid selection")
                    return None
            except ValueError:
                logger.error("Please enter a valid number")
                return None
        
        imdb_id = selected_movie['imdb_id']
        movie_title = selected_movie['title']
        
        logger.info(f"\nScraping reviews for: {movie_title} ({imdb_id})")
        
        # Scrape reviews for the selected movie
        data = scrape_all_reviews(imdb_id, driver, max_pages)
        
        # Count total reviews
        total_reviews = len(data['reviews'])
        
        logger.info(f"\nFound {total_reviews} reviews for {movie_title}")
        
        # Create directory if it doesn't exist
        os.makedirs("reviews", exist_ok=True)
        
        # Save to JSON file
        sanitized_title = re.sub(r'[\\/*?:"<>|]', "", movie_title.replace(' ', '_'))
        filename = f"reviews/reviews_{imdb_id}_{sanitized_title}.json"
        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        
        logger.info(f"\nReviews saved to {filename}")
        return data
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
    finally:
        # Always close the driver when done
        driver.quit()

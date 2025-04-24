import requests
from bs4 import BeautifulSoup
import csv
import time
import random

class MyAnimeListScraper:
    def __init__(self):
        self.base_url = "https://myanimelist.net/anime"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_top_anime(self, page=1, limit=50):
        """Scrape the top anime list page by page"""
        anime_list = []
        url = f"{self.base_url}/top/all/{page}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            anime_entries = soup.select('tr.ranking-list')
            
            count = 0
            for entry in anime_entries:
                if count >= limit:
                    break
                    
                rank = entry.select_one('td.rank span').text.strip()
                title_element = entry.select_one('td.title div.di-ib h3 a')
                title = title_element.text
                anime_url = title_element['href']
                anime_id = anime_url.split('/')[-2]
                
                # Extract score and other basic info
                score = entry.select_one('td.score span').text.strip()
                info_div = entry.select_one('div.information')
                info_text = info_div.text.strip().split('\n')
                
                # Process the information text
                anime_type = ""
                episodes = ""
                airing_dates = ""
                members = ""
                
                for line in info_text:
                    line = line.strip()
                    if line:
                        if anime_type == "":
                            anime_type = line
                        elif episodes == "":
                            episodes = line
                        elif airing_dates == "":
                            airing_dates = line
                        elif members == "":
                            members = line
                
                # Get image URL
                image_element = entry.select_one('td.title div.picSurround img')
                image_url = image_element['data-src'] if image_element.get('data-src') else image_element.get('src', '')
                
                anime_info = {
                    'rank': rank,
                    'title': title,
                    'anime_id': anime_id,
                    'url': anime_url,
                    'score': score,
                    'type': anime_type,
                    'episodes': episodes,
                    'airing_dates': airing_dates,
                    'members': members,
                    'image_url': image_url
                }
                
                anime_list.append(anime_info)
                count += 1
                
            return anime_list
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            return []

    def get_anime_details(self, anime_id):
        """Scrape detailed information about a specific anime"""
        url = f"{self.base_url}/{anime_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Basic information
            title = soup.select_one('h1.title-name').text.strip() if soup.select_one('h1.title-name') else "N/A"
            
            # Get alternative titles
            alt_titles = {}
            alt_titles_section = soup.select_one('div.alternative-titles')
            if alt_titles_section:
                for row in alt_titles_section.select('div.spaceit_pad'):
                    key = row.text.split(':')[0].strip()
                    value = row.text.split(':', 1)[1].strip() if ':' in row.text else "N/A"
                    alt_titles[key] = value
            
            # Information section
            info = {}
            info_section = soup.select('div.spaceit_pad')
            for item in info_section:
                if ':' in item.text:
                    key = item.text.split(':')[0].strip()
                    value = item.text.split(':', 1)[1].strip()
                    info[key] = value
            
            # Synopsis
            synopsis = ""
            synopsis_element = soup.select_one('p[itemprop="description"]')
            if synopsis_element:
                synopsis = synopsis_element.text.strip()
            
            # Related anime
            related_anime = []
            related_section = soup.select_one('table.anime_detail_related_anime')
            if related_section:
                for row in related_section.select('tr'):
                    relation = row.select_one('td:first-child').text.strip().replace(':', '')
                    related_titles = [a.text.strip() for a in row.select('td:last-child a')]
                    for title in related_titles:
                        related_anime.append({
                            'relation': relation,
                            'title': title
                        })
            
            # Characters & Staff
            characters = []
            characters_section = soup.select('div.detail-characters-list')
            for char_row in characters_section:
                character_elements = char_row.select('table')
                for element in character_elements:
                    character_name = element.select_one('td:nth-child(2) a')
                    if character_name:
                        character_name = character_name.text.strip()
                        character_role = element.select_one('td:nth-child(2) div small').text.strip() if element.select_one('td:nth-child(2) div small') else "N/A"
                        
                        # Voice actor info
                        va_element = element.select_one('td:nth-child(3) a')
                        va_name = va_element.text.strip() if va_element else "N/A"
                        
                        characters.append({
                            'name': character_name,
                            'role': character_role,
                            'voice_actor': va_name
                        })
            
            # Collect detailed anime information
            anime_details = {
                'id': anime_id,
                'title': title,
                'alternative_titles': alt_titles,
                'information': info,
                'synopsis': synopsis,
                'related_anime': related_anime,
                'characters': characters
            }
            
            return anime_details
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching anime details for ID {anime_id}: {e}")
            return {}

    def search_anime(self, query, page=1):
        """Search for anime based on a query"""
        search_url = f"{self.base_url}/search"
        params = {
            'q': query,
            'page': page
        }
        
        try:
            response = requests.get(search_url, params=params, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            search_results = soup.select('div.js-categories-seasonal div[id^="sinfo"]')
            
            results = []
            for result in search_results:
                # Extract anime info
                title_element = result.select_one('div.title a')
                if not title_element:
                    continue
                    
                title = title_element.text.strip()
                url = title_element['href']
                anime_id = url.split('/')[-2]
                
                # Extract image
                image_element = result.select_one('div.picSurround img')
                image_url = image_element['data-src'] if image_element.get('data-src') else image_element.get('src', '')
                
                # Extract synopsis
                synopsis = ""
                synopsis_element = result.select_one('div.pt4')
                if synopsis_element:
                    synopsis = synopsis_element.text.strip()
                
                # Extract additional info
                info_element = result.select_one('div.info')
                info_text = info_element.text.strip() if info_element else ""
                
                results.append({
                    'title': title,
                    'id': anime_id,
                    'url': url,
                    'image': image_url,
                    'synopsis': synopsis,
                    'info': info_text
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching for '{query}' on page {page}: {e}")
            return []

    def save_to_csv(self, data, filename):
        """Save scraped data to a CSV file"""
        if not data:
            print("No data to save")
            return
            
        # Get headers from first item
        headers = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
            
        print(f"Data saved to {filename}")

def main():
    scraper = MyAnimeListScraper()
    
    # Example 1: Get top anime
    print("Scraping top anime...")
    top_anime = scraper.get_top_anime(page=1, limit=10)
    scraper.save_to_csv(top_anime, 'top_anime.csv')
    
    # Wait to avoid overloading the server
    time.sleep(2)
    
    # Example 2: Get detailed info for a specific anime (Attack on Titan)
    print("Scraping detailed info for Attack on Titan...")
    attack_on_titan_id = "16498"  # ID for Attack on Titan
    anime_details = scraper.get_anime_details(attack_on_titan_id)
    print(f"Title: {anime_details.get('title')}")
    print(f"Synopsis: {anime_details.get('synopsis')[:100]}...")
    
    # Wait to avoid overloading the server
    time.sleep(2)
    
    # Example 3: Search for anime
    print("Searching for 'Naruto'...")
    search_results = scraper.search_anime("Naruto", page=1)
    scraper.save_to_csv(search_results, 'naruto_search.csv')

if __name__ == "__main__":
    main()
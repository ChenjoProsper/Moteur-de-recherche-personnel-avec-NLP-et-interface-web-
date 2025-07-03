import pytest
from indexation import scrape_and_save
import os

def test_scraper():
    test_url = "https://fr.wikipedia.org/wiki/Test_(informatique)"
    output_path = "data/test_scraped.txt"
    
    scrape_and_save(test_url, output_path)
    assert os.path.exists(output_path), "Le fichier scrapé n'existe pas !"
    assert os.path.getsize(output_path) > 0, "Le fichier scrapé est vide !"
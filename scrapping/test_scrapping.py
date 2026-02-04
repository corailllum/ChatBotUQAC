"""
Script de test pour vérifier le scraper avant le lancement complet
"""

from scrapper import HTMLScraper, PDFScraper, Config

def test_html_scraping():
    """Test du scraping d'une page HTML"""
    print("\n TEST 1: Scraping d'une page HTML")
    print("-" * 50)
    
    scraper = HTMLScraper(Config.BASE_URL)
    data = scraper.get_page_content(Config.BASE_URL)
    
    if data:
        print(f" Titre: {data['title'][:50]}...")
        print(f" Contenu récupéré: {len(data['content'])} caractères")
        print(f" URL: {data['url']}")
        print(f" Aperçu: {data['content'][:200]}...")
    else:
        print(" Échec du scraping")

def test_find_links():
    """Test de la recherche de liens"""
    print("\n TEST 2: Recherche de liens")
    print("-" * 50)
    
    scraper = HTMLScraper(Config.BASE_URL)
    links = scraper.find_links(Config.BASE_URL)
    
    print(f" {len(links)} liens trouvés")
    print(" Premiers liens:")
    for i, link in enumerate(links[:5]):
        print(f"  {i+1}. {link}")

def test_embeddings():
    """Test du chargement des embeddings"""
    print("\n TEST 3: Chargement des embeddings")
    print("-" * 50)
    
    try:
        from langchain_community.embeddings import GPT4AllEmbeddings
        embeddings = GPT4AllEmbeddings()
        
        # Test avec un texte simple
        test_text = "Ceci est un test pour vérifier que les embeddings fonctionnent."
        result = embeddings.embed_query(test_text)
        
        print(f" Embeddings chargés avec succès!")
        print(f" Dimension du vecteur: {len(result)}")
    except Exception as e:
        print(f" Erreur: {str(e)}")

if __name__ == "__main__":
    print("""
           TESTS DU SCRAPER
   """)
    
    test_html_scraping()
    test_find_links()
    test_embeddings()
    
    print("\n" + "=" * 50)
    print(" Tests terminés!")
    print("=" * 50)
"""
Scraper pour le Manuel de Gestion UQAC
Ce script récupère le contenu des pages HTML et PDF du site de l'UQAC
et les stocke dans une base de données vectorielle pour le RAG
"""
import sys
from pathlib import Path

# ajouter la racine du projet au PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import RAG.config as config
import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import tempfile
import time
from typing import List, Dict
from pypdf import PdfReader
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma
import RAG.config as config
import re



# ==========================================
# PARTIE 2 : SCRAPING DES PAGES HTML
# ==========================================

class HTMLScraper:
    """Classe pour scraper les pages HTML du manuel UQAC"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.visited_urls = set()  # Pour éviter les doublons
        self.session = requests.Session()  # Réutilise la connexion HTTP
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Bot)'
        })
    
    def get_page_content(self, url: str) -> Dict[str, str]:
        """
        Récupère le contenu d'une page HTML
        
        Args:
            url: L'URL de la page à scraper
            
        Returns:
            Dictionnaire avec le titre, le contenu et l'URL
        """
        try:
            print(f" Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # Lève une erreur si le statut n'est pas 200
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Récupère le titre de la page
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Sans titre"
            
            # Cherche le contenu dans les divs spécifiées
            content_parts = []
            
            # Cherche dans entry-header
            header = soup.find('div', class_='entry-header')
            if header:
                content_parts.append(header.get_text(strip=True, separator=' '))
            
            # Cherche dans entry-content
            content = soup.find('div', class_='entry-content')
            if content:
                content_parts.append(content.get_text(strip=True, separator=' '))
            
            # Combine tout le contenu
            full_content = ' '.join(content_parts)
            
            return {
                'title': title_text,
                'content': full_content,
                'url': url,
                'type': 'html'
            }
            
        except Exception as e:
            print(f" Erreur lors du scraping de {url}: {str(e)}")
            return None
    
    def find_links(self, url: str) -> List[str]:
        """
        Trouve tous les liens dans une page
        
        Args:
            url: L'URL de la page
            
        Returns:
            Liste des URLs trouvées
        """
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                
                # Garde seulement les liens du même domaine
                if self.base_url in absolute_url:
                    links.append(absolute_url)
            
            return list(set(links))  # Enlève les doublons
            
        except Exception as e:
            print(f" Erreur lors de la recherche de liens: {str(e)}")
            return []


# ==========================================
# PARTIE 3 : SCRAPING DES PDF
# ==========================================

class PDFScraper:
    """Classe pour télécharger et extraire le texte des PDF"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Bot)'
        })
    
    def extract_pdf_content(self, url: str) -> Dict[str, str]:
        """
        Télécharge un PDF temporairement et extrait son contenu
        
        Args:
            url: L'URL du PDF
            
        Returns:
            Dictionnaire avec le contenu et l'URL
        """
        try:
            print(f" Téléchargement PDF: {url}")
            
            # Télécharge le PDF
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Crée un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            # Lit le PDF
            reader = PdfReader(tmp_path)
            text_parts = []
            
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            # Supprime le fichier temporaire
            os.unlink(tmp_path)
            
            full_text = '\n'.join(text_parts)
            
            return {
                'title': os.path.basename(urlparse(url).path),
                'content': full_text,
                'url': url,
                'type': 'pdf'
            }
            
        except Exception as e:
            print(f" Erreur lors de l'extraction du PDF {url}: {str(e)}")
            return None



# ==========================================
# PARTIE 5 : ORCHESTRATION PRINCIPALE
# ==========================================

class ManuelScraperPipeline:
    """Pipeline complet de scraping et stockage"""
    
    def __init__(self):
        self.html_scraper = HTMLScraper(config.BASE_URL)
        self.pdf_scraper = PDFScraper()
        self.embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
        self.vector_store = Chroma(embedding_function=self.embeddings, persist_directory=config.PERSIST_DIRECTORY)
        self.scraped_data = []
        self.chunks = []
    
    def scrape_all(self, start_url: str, max_pages: int = config.MAX_PAGES):
        """
        Lance le scraping complet
        
        Args:
            start_url: URL de départ
            max_pages: Nombre maximum de pages à scraper
        """
        urls_to_visit = [start_url]
        visited = set()
        
        print(f" Début du scraping depuis {start_url}")
        print(f" Maximum {max_pages} pages")
        print("-" * 50)
        
        while urls_to_visit and len(visited) < max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in visited:
                continue
            
            visited.add(current_url)
            
            # Détermine si c'est un PDF ou HTML
            if current_url.lower().endswith('.pdf'):
                # Traite les PDF
                data = self.pdf_scraper.extract_pdf_content(current_url)
                if data:
                    self.scraped_data.append(data)
            else:
                # Traite les HTML
                data = self.html_scraper.get_page_content(current_url)
                if data:
                    self.scraped_data.append(data)
                
                # Trouve de nouveaux liens
                new_links = self.html_scraper.find_links(current_url)
                for link in new_links:
                    if link not in visited and link not in urls_to_visit:
                        urls_to_visit.append(link)
            
            # Pause pour ne pas surcharger le serveur
            time.sleep(0.5)
            
            # Affiche la progression
            if len(visited) % 10 == 0:
                print(f" Progression: {len(visited)} pages visitées, {len(self.scraped_data)} documents collectés")
        
        print("-" * 50)
        print(f" Scraping terminé! {len(self.scraped_data)} documents collectés")
        
    def convert_data(self):
        print("\nConversion des données en documents")
        documents = []
        for item in self.scraped_data:
            print(f" Converti : {item}")
            if item and item.get('content'):
                doc = Document(
                    page_content=item['content'],
                    metadata={
                        'title': item['title'],
                        'url': item['url'],
                        'type': item['type']
                    }
                )
                documents.append(doc)
        print(f"{len(documents)} documents convertis")
        return documents
    
    def split_by_sections(self):
        print("\n Découpage des documents en sections")

        documents = self.convert_data()

        # Utilise le text splitter de LangChain pour garantir la taille
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        all_chunks = []
        for doc in documents:
            # Découpe d'abord par sections si possible
            text = doc.page_content
            sections = re.split(
                r"\n(?=\d+\.\s|\n\d+\.\d+\.\s)",  # Regex du titre
                text
            )
            for section in sections:
                section = section.strip()
                if len(section) > 100:  # évite les titres seuls
                    if len(section) > config.CHUNK_SIZE:
                        # Subdivise avec le text splitter
                        sub_chunks = text_splitter.create_documents(
                            [section],
                            metadatas=[doc.metadata]
                        )
                        all_chunks.extend(sub_chunks)
                    else:
                        all_chunks.append(
                            Document(
                                page_content=section,
                                metadata=doc.metadata
                            )
                        )
        self.chunks = all_chunks
        print(f"\n {len(self.chunks)} sections créées")

        max_length = max(len(chunk.page_content) for chunk in self.chunks)
        print(f"Taille maximale des chunks: {max_length} caractères")

    def store_data(self):
        """Stocke les données dans la base vectorielle"""
        print("\n Stockage des données dans ChromaDB...")

        if not self.chunks:
            print("\n Aucun chunk à stocker !")
            return

        # Filtre les chunks vides ou trop petits
        valid_chunks = [
            chunk for chunk in self.chunks
            if chunk.page_content and len(chunk.page_content.strip()) > 50
        ]
        print(f"{len(valid_chunks)} chunks valides sur {len(self.chunks)}")

        self.vector_store.add_documents(valid_chunks)
        print(" Stockage terminé!")
    
    def run(self):
        """Lance le pipeline complet"""
        self.scrape_all(config.BASE_URL)
        self.split_by_sections()
        self.store_data()
        
        print("\n" + "=" * 50)
        print(" PIPELINE TERMINÉ!")
        print(f" Base de données sauvegardée dans: {config.PERSIST_DIRECTORY}")
        print("=" * 50)


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    print("""
          SCRAPER MANUEL DE GESTION UQAC
          Projet Chatbot RAG - IA                    
    """)
    
    # Lance le pipeline
    pipeline = ManuelScraperPipeline()
    pipeline.run()



"""
Script de diagnostic pour tester les liens PDF du site UQAC
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import config as config

def test_pdf_links():
    """Teste si des liens PDF existent sur le site UQAC"""
    
    print("🔍 Recherche de liens PDF sur le site UQAC...")
    print(f"URL de base : {config.BASE_URL}")
    print("-" * 60)
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Educational Bot)'})
    
    try:
        # Récupère la page d'accueil
        response = session.get(config.BASE_URL, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trouve TOUS les liens
        all_links = soup.find_all('a', href=True)
        print(f"✅ Total de liens trouvés : {len(all_links)}\n")
        
        # Filtre les liens PDF
        pdf_links = []
        for link in all_links:
            href = link['href']
            absolute_url = urljoin(config.BASE_URL, href)
            
            # Vérifie si c'est un PDF
            if '.pdf' in absolute_url.lower():
                pdf_links.append({
                    'url': absolute_url,
                    'text': link.get_text().strip()
                })
        
        print(f"📄 Liens PDF trouvés : {len(pdf_links)}\n")
        
        if pdf_links:
            print("Liste des PDFs trouvés :")
            print("-" * 60)
            for i, pdf in enumerate(pdf_links[:10], 1):  # Affiche les 10 premiers
                print(f"{i}. {pdf['text'][:50]}")
                print(f"   URL: {pdf['url']}")
                print()
            
            if len(pdf_links) > 10:
                print(f"... et {len(pdf_links) - 10} autres PDFs")
            
            # Teste l'accessibilité du premier PDF
            print("\n" + "=" * 60)
            print("🧪 Test d'accessibilité du premier PDF...")
            print("=" * 60)
            
            test_url = pdf_links[0]['url']
            print(f"URL testée : {test_url}")
            
            try:
                pdf_response = session.head(test_url, timeout=10)
                print(f"Status Code : {pdf_response.status_code}")
                print(f"Content-Type : {pdf_response.headers.get('Content-Type', 'N/A')}")
                
                if pdf_response.status_code == 200:
                    print("✅ Le PDF est accessible !")
                elif pdf_response.status_code == 404:
                    print("❌ Le PDF n'existe plus (404 Not Found)")
                elif pdf_response.status_code == 403:
                    print("❌ Accès refusé au PDF (403 Forbidden)")
                else:
                    print(f"⚠️  Status inattendu : {pdf_response.status_code}")
                
            except Exception as e:
                print(f"❌ Erreur lors du test : {str(e)}")
        
        else:
            print("❌ Aucun lien PDF trouvé sur la page d'accueil !")
            print("\n💡 Possibilités :")
            print("   1. Les PDFs ne sont plus sur le site")
            print("   2. Les PDFs sont dans des sous-pages")
            print("   3. Les PDFs sont chargés dynamiquement (JavaScript)")
            
            # Affiche quelques liens pour diagnostic
            print("\n📋 Exemples de liens trouvés :")
            for i, link in enumerate(all_links[:5], 1):
                print(f"{i}. {link.get_text().strip()[:50]}")
                print(f"   URL: {urljoin(config.BASE_URL, link['href'])}")
                print()
    
    except Exception as e:
        print(f"❌ Erreur lors de la connexion : {str(e)}")
        print("\n💡 Vérifiez que :")
        print("   1. Vous avez une connexion Internet")
        print("   2. L'URL dans config.py est correcte")
        print("   3. Le site UQAC est accessible")


def test_specific_pdf(pdf_url: str):
    """Teste un PDF spécifique"""
    
    print("\n" + "=" * 60)
    print("🧪 Test d'un PDF spécifique")
    print("=" * 60)
    print(f"URL : {pdf_url}\n")
    
    session = requests.Session()
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Educational Bot)'})
    
    try:
        # Test HEAD (rapide, ne télécharge pas le contenu)
        response = session.head(pdf_url, timeout=10)
        print(f"Status Code : {response.status_code}")
        print(f"Content-Type : {response.headers.get('Content-Type', 'N/A')}")
        print(f"Content-Length : {response.headers.get('Content-Length', 'N/A')} bytes")
        
        if response.status_code == 200:
            print("\n✅ Le PDF existe et est accessible !")
            
            # Test de téléchargement
            print("\n📥 Test de téléchargement...")
            download_response = session.get(pdf_url, timeout=30)
            
            if download_response.status_code == 200:
                size_kb = len(download_response.content) / 1024
                print(f"✅ PDF téléchargé avec succès ! ({size_kb:.2f} KB)")
                
                # Test d'extraction
                print("\n📖 Test d'extraction du texte...")
                try:
                    import tempfile
                    from pypdf import PdfReader
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(download_response.content)
                        tmp_path = tmp.name
                    
                    reader = PdfReader(tmp_path)
                    num_pages = len(reader.pages)
                    
                    # Extrait le texte de la première page
                    first_page_text = reader.pages[0].extract_text()
                    
                    print(f"✅ PDF lu avec succès !")
                    print(f"   Nombre de pages : {num_pages}")
                    print(f"   Texte première page (100 premiers caractères) :")
                    print(f"   {first_page_text[:100]}")
                    
                    import os
                    os.unlink(tmp_path)
                    
                except Exception as e:
                    print(f"❌ Erreur lors de l'extraction : {str(e)}")
            
            else:
                print(f"❌ Échec du téléchargement : {download_response.status_code}")
        
        elif response.status_code == 404:
            print("\n❌ Le PDF n'existe pas (404 Not Found)")
            print("💡 Le lien est peut-être obsolète")
        
        elif response.status_code == 403:
            print("\n❌ Accès refusé (403 Forbidden)")
            print("💡 Le serveur bloque peut-être les bots")
        
        else:
            print(f"\n⚠️  Status inattendu : {response.status_code}")
    
    except Exception as e:
        print(f"\n❌ Erreur : {str(e)}")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   DIAGNOSTIC SCRAPING PDF - UQAC             ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Test 1 : Recherche de PDFs sur le site
    test_pdf_links()
    
    # Test 2 : Si vous avez un lien PDF spécifique à tester
    # Décommentez et mettez votre URL :
    # test_specific_pdf("https://www.uqac.ca/mgestion/exemple.pdf")
    
    print("\n" + "=" * 60)
    print("🏁 Diagnostic terminé")
    print("=" * 60)
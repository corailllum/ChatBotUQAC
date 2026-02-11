# ChatBotUQAC 
## Groupe :

**Charlotte Chanudet**

**Mahaut Galice**

**Marie Howet**

## But du projet :
Le but de ce projet est de mettre en place un chatbot fonctionnel afin répondre à des questions d'usagers portant sur le manuel de l'UQAC. Ce README à pour but d'expliquer les différents choix de conception ainsi que l'architecture choisie. Il detaillera également les differentes étapes du projet et la façon de lancer le chatbot. D'autre ReadMe sont présents dans les différents dossiers afin d'expliquer le fonctionnement de chaque partie.

## Technologie utilisées :
- **Librairies :** LangChain, tempfile, Streamlit 
- **Techniques :** RAG, webscrapping 
- **Modèles :** Ollama

## Organisation du Git : 
Ce GitHub est séparé en plusieurs dossiers dont nous allons expliquer le rôle ici :
- **Data** : le dossier data sert à contenir toute la base de donnée mise en place avec chroma. 
- **RAG** : le dossier RAG contient les fichiers servant pour l'interface du CHATBOT ainsi que le model LLM
- **scrapping** : Le dossier scraping contient tous les fichiers relatifs à la collecte et à la sauvegarde des données relatives au manuel de l'UQAC

### Lancement du chat bot : 
Pour lancer le Chatbot veuillez suivre les instructions suivantes :

#### Prérequis
Avoir pip d'installer (permet de suivre plus aisément les commande bash) ainsi que ollama.

#### Pour installer Ollama si ce n'est pas fait

Sous Linux
```
curl -fsSL https://ollama.ai/install.sh | sh
```

Sous MacOS
```
brew install ollama
```

Sous Windows
- Télécharger directement via le site https://ollama.com/download

Ensuite

Dans un premier temps, lancer la commande suivante : 
```
 pip install -r requirements.txt  

```
Ensuite, démarrer le serveur Ollama avec cette commande 
```
ollama serve
```
Installer les modèles Ollama nécéssaire :
```
ollama pull llama3.2
ollama pull nomic-embed-text
```
Dans un autre terminal, lancer la commande suivante puis suivre le lien donné en console
```
streamlit run RAG/rag_chatbot.py
```


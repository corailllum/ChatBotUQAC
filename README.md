# ChatBotUQAC 
## Groupe :

**Charlotte Chanudet**

**Mahaut Galice**

**Marie Howet**

## But du projet :
Le but est de mettre en place un chatbot fonctionnel pour répondre aux questions portant sur le manuel de l'UQAC. Ce README a pour but d'expliquée les différents choix de conception ainsi que l'architecture choisi. Il detaillera aussi different étapes du projet. d'autre readme seront présent dans les dossiers afin d'expliquée l'utilisation de chaque partie

## Technologie utilisées :
- **Librairies :** LangGraph, LangChain, Python LangGraph, tempfile, Streamlit 
- **Techniques :** RAG, webscrapping 
- **Modèles :** GPT4ALL (https://www.nomic.ai/gpt4all), Ollama

## Organisation du Git : 
Le git est séparé en plusieurs dossier dont nous allons expliquées le rôle ici :
- **Data** : le dossier data est la pour contenir toute la base de donnée mis en place avec chroma. 
- **RAG** : le dossier RAG contient les les fichier pour l'interface du CHATBOT ainsi que le model LLM
- **scrapping** : Le dossier scraping contient tous les fichier relative a la collecte et a la sauvegarde des données relative au manuel de l'uqac

### Lancement du chat bot : 
Pour lancée le Chatbot veuillez suivre les commande suivante :

#### prérequis
Avoir pip d'installée (permet de suivre plus aisément les commande bash) ainsi que ollama

dans un premier temps lancée la commende suivante : 
```
 pip install -r requirements.txt  

```
ensuite, démarrer le serveure ollama avec cette commande 
```
ollama serve
```
installer les modèles ollama nécéssaire :
```
ollama pull llama3.2
ollama pull nomic-embed-text
```
Dans un autre terminal lancée la commande suivante puis suiver le lien donné en console
```
streamlit run rag_chatbot.py
```


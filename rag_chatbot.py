"""
Chatbot RAG - Version corrigée
Posez vos questions sur le Manuel de Gestion UQAC
"""

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM, OllamaEmbeddings
import streamlit as st
import config

# ========================
# 1. INTERFACE
# ========================
st.set_page_config(page_title="Chatbot RAG UQAC", page_icon="💬", layout="wide")
st.title("💬 Chatbot RAG - Manuel de Gestion UQAC")
st.caption("Posez vos questions sur les politiques et règlements de l'UQAC")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres")
    k_sources = st.slider(
        "Nombre de sources à consulter",
        min_value=1,
        max_value=10,
        value=4,
        help="Plus de sources = plus de contexte mais temps de réponse plus long"
    )

    if st.button("🗑️ Effacer l'historique"):
        st.session_state.messages = []
        st.session_state.conversation_context = []
        st.rerun()

# ========================
# 2. INITIALISATION
# ========================
@st.cache_resource
def init_components():
    """Initialise les composants (embeddings, vectorstore, LLM)"""
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory=config.PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    llm = OllamaLLM(model=config.LLM_MODEL, temperature=0.2)
    return embeddings, vectorstore, llm


embeddings, vectorstore, llm = init_components()

# ========================
# 3. FONCTION RAG AVEC MÉMOIRE
# ========================
def get_rag_response(question: str, k: int = 4):
    """
    Génère une réponse en utilisant RAG avec mémoire contextuelle optionnelle

    Args:
        question: La question de l'utilisateur
        k: Nombre de documents sources à récupérer

    Returns:
       Dictionnaire avec le contexte et les sources
    """

    # Récupérer les documents pertinents
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    source_docs = retriever.invoke(question)

    # Construire le contexte depuis les sources
    context = "\n\n".join([
        f"[Source {i + 1}]\n{doc.page_content}"
        for i, doc in enumerate(source_docs)
    ])

    # Construire l'historique de conversation
    conversation_history = ""
    if "conversation_context" in st.session_state:
        recent_exchanges = st.session_state.conversation_context[-3:]  # 3 derniers échanges
        if recent_exchanges:
            conversation_history = "\n\nHistorique récent de la conversation:\n"
            for exchange in recent_exchanges:
                conversation_history += f"Q: {exchange['question']}\n"
                conversation_history += f"R: {exchange['answer']}\n\n"

    # Créer le prompt avec ou sans mémoire
    if conversation_history:
        template = """Tu es un assistant spécialisé dans les politiques et procédures de l'UQAC.
                    Réponds en te basant sur le contexte fourni et l'historique de la conversation.
                    Si l'information n'est pas dans le contexte, dis-le clairement.
                    
                    {conversation_history}
                    
                    Contexte actuel:
                    {context}
                    
                    Question actuelle: {question}
                    
                    Réponse:
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain_input = {
            "context": context,
            "question": question,
            "conversation_history": conversation_history
        }
    else:
        template = """Tu es un assistant spécialisé dans les politiques de l'UQAC.
                    Réponds en te basant uniquement sur le contexte fourni.
                    Si l'information n'est pas dans le contexte, dis-le clairement.
                    
                    Contexte:
                    {context}
                    
                    Question: {question}
                    
                    Réponse:
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain_input = {
            "context": context,
            "question": question
        }

    # Générer la réponse
    formatted_prompt = prompt.format(**chain_input)
    answer = llm.invoke(formatted_prompt)

    return {
        "answer": answer,
        "sources": source_docs
    }

# ========================
# 4. INITIALISATION DE LA SESSION
# ========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_context" not in st.session_state:
    st.session_state.conversation_context = []

# ========================
# 5. AFFICHAGE DE L'HISTORIQUE
# ========================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Afficher les sources si disponibles
        if message["role"] == "assistant" and "sources" in message:
            with st.expander(f"📚 {len(message['sources'])} sources consultées"):
                for i, doc in enumerate(message["sources"], 1):
                    url = doc.metadata.get('url', 'N/A')

                    st.markdown(f"{i}. {url}")

                    # Afficher un extrait du contenu
                    preview = doc.page_content[:200].replace('\n', ' ')
                    st.text(f"   {preview}...")
                    st.divider()

# ========================
# 6. ENTRÉE UTILISATEUR
# ========================
if prompt := st.chat_input("Votre question sur le manuel de gestion..."):

    # Afficher la question de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Générer et afficher la réponse
    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche dans le manuel de gestion..."):
            result = get_rag_response(prompt, k=k_sources)
            answer = result["answer"]
            sources = result["sources"]

            # Afficher la réponse
            st.markdown(answer)

            # Afficher les sources de manière persistante
            with st.expander(f"📚 {len(sources)} sources consultées"):
                for i, doc in enumerate(sources, 1):
                    url = doc.metadata.get('url', 'N/A')

                    st.markdown(f"{i}. {url}")

                    # Afficher un extrait du contenu
                    preview = doc.page_content[:200].replace('\n', ' ')
                    st.text(f"   {preview}...")
                    st.divider()

    # Sauvegarder la réponse avec les sources dans l'historique
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

    # Mettre à jour le contexte de conversation pour la mémoire
    st.session_state.conversation_context.append({
        "question": prompt,
        "answer": answer
    })

    # Limiter l'historique contextuel à 5 échanges pour éviter des prompts trop longs
    if len(st.session_state.conversation_context) > 5:
        st.session_state.conversation_context = st.session_state.conversation_context[-5:]

# ========================
# 7. FOOTER AVEC INFOS
# ========================
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🤖 Modèle LLM", config.LLM_MODEL)
with col2:
    st.metric("🧠 Modèle Embeddings", config.EMBEDDING_MODEL)
with col3:
    st.metric("💬 Messages", len(st.session_state.messages))
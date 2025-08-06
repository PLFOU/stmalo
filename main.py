import streamlit as st
import json
from streamlit_js_eval import streamlit_js_eval

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Liste de Courses", page_icon="🛒", layout="centered")
st.title("🛒 Liste de Courses Partagée")

# --- FONCTIONS POUR GÉRER LES DONNÉES ---

def charger_donnees():
    """Charge la liste de courses depuis le fichier JSON."""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si le fichier n'existe pas ou est vide, retourne une liste vide
        return []

def sauvegarder_donnees(data):
    """Sauvegarde la liste de courses dans le fichier JSON."""
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- INITIALISATION ---
# On charge les données au début de l'exécution
liste_courses = charger_donnees()

# --- INTERFACE UTILISATEUR ---

# Crée des colonnes pour organiser les boutons d'action en haut
col1, col2, col3 = st.columns([0.5, 0.25, 0.25])

# Section pour ajouter un article
with col1:
    with st.form(key='form_ajout'):
        nouvel_article = st.text_input(
            "Ajouter un article",
            placeholder="Ex: Bananes, Lait, Pain...",
            label_visibility="collapsed",
            key="input_article"
        )
        bouton_ajouter = st.form_submit_button(label="➕ Ajouter")

# Logique pour ajouter un article
if bouton_ajouter and nouvel_article:
    # Ajoute le nouvel article à la liste (non coché par défaut)
    liste_courses.append({"nom": nouvel_article.capitalize(), "coche": False})
    sauvegarder_donnees(liste_courses)
    # Met le focus sur le champ de saisie après l'ajout
    streamlit_js_eval(js_expressions="parent.document.getElementById('input_article').focus()")
    # Force le rechargement pour afficher la mise à jour
    st.rerun()

# Bouton pour supprimer les articles sélectionnés
with col2:
    if st.button("🗑️ Supprimer la sélection"):
        # Garde uniquement les articles qui ne sont pas cochés
        liste_courses_filtree = [item for item in liste_courses if not item['coche']]
        sauvegarder_donnees(liste_courses_filtree)
        st.rerun()

# Bouton pour tout réinitialiser
with col3:
    if st.button("🔄 Tout effacer"):
        sauvegarder_donnees([]) # Sauvegarde une liste vide
        st.rerun()

st.markdown("---") # Ligne de séparation

# --- AFFICHAGE DE LA LISTE DE COURSES ---
if not liste_courses:
    st.info("Votre liste de courses est vide. Ajoutez des articles ci-dessus !")
else:
    # Parcourt chaque article et l'affiche avec une case à cocher
    for i, article in enumerate(liste_courses):
        # `st.checkbox` retourne True si la case est cochée, False sinon
        # La clé unique est importante pour que Streamlit identifie chaque case
        est_coche = st.checkbox(
            article['nom'],
            value=article['coche'],
            key=f"article_{i}"
        )
        # Met à jour le statut de l'article si la case a été (dé)cochée
        if est_coche != article['coche']:
            liste_courses[i]['coche'] = est_coche
            sauvegarder_donnees(liste_courses)
            st.rerun()

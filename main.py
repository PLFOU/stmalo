import streamlit as st
import json
from streamlit_js_eval import streamlit_js_eval

# --- CONFIGURATION DE LA PAGE ---
# Définit le titre de l'onglet du navigateur et l'icône
st.set_page_config(page_title="Liste de Courses", page_icon="🛒", layout="centered")

# --- FONCTIONS POUR GÉRER LE FICHIER JSON ---

def charger_donnees():
    """Charge la liste de courses depuis le fichier data.json."""
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Si le fichier n'est pas trouvé ou est corrompu/vide, on repart d'une liste vide.
        return []

def sauvegarder_donnees(data):
    """Sauvegarde la liste actuelle dans le fichier data.json."""
    with open('data.json', 'w', encoding='utf-8') as f:
        # indent=4 pour une lecture facile du fichier, ensure_ascii=False pour les accents
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- INTERFACE DE L'APPLICATION ---

st.title("🛒 Ma Liste de Courses")

# Charge les données au lancement de l'application
liste_courses = charger_donnees()

# --- BLOC D'ACTIONS EN HAUT ---
# On utilise des colonnes pour aligner les boutons
col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

# Colonne 1 : Formulaire pour ajouter un article
with col1:
    # Utiliser un formulaire est une bonne pratique dans Streamlit
    with st.form(key='form_ajout', clear_on_submit=True):
        nouvel_article = st.text_input(
            "Ajouter un article", 
            placeholder="Que faut-il acheter ?",
            label_visibility="collapsed" # Masque le label "Ajouter un article"
        )
        bouton_ajouter = st.form_submit_button(label="➕ Ajouter")

# Colonne 2 : Bouton pour supprimer la sélection
with col2:
    if st.button("🗑️ Supprimer"):
        # On ne garde que les articles qui ne sont PAS cochés
        liste_courses_maj = [item for item in liste_courses if not item['coche']]
        sauvegarder_donnees(liste_courses_maj)
        st.rerun() # Rafraîchit la page pour afficher le résultat

# Colonne 3 : Bouton pour tout remettre à zéro
with col3:
    if st.button("🔄 Vider"):
        sauvegarder_donnees([]) # Sauvegarde une liste vide
        st.rerun()

# --- LOGIQUE D'AJOUT D'ARTICLE (après la déclaration du formulaire) ---
# Ce code s'exécute si le bouton "Ajouter" a été cliqué et que le champ n'est pas vide
if bouton_ajouter and nouvel_article:
    liste_courses.append({'nom': nouvel_article.strip().capitalize(), 'coche': False})
    sauvegarder_donnees(liste_courses)
    
    # POINT CRUCIAL : C'est ici qu'on remet le focus sur le champ de saisie
    # On exécute un petit code Javascript pour que l'utilisateur puisse continuer à taper
    streamlit_js_eval(js_expressions="parent.document.querySelector('input[aria-label=\"Ajouter un article\"]').focus()")
    
    # On rafraîchit la page pour voir le nouvel article dans la liste
    st.rerun()


st.markdown("---") # Ligne de séparation visuelle

# --- AFFICHAGE DE LA LISTE DE COURSES ---
if not liste_courses:
    st.info("La liste est vide. Ajoutez des articles ci-dessus !")
else:
    # On parcourt la liste et on affiche chaque article avec sa case à cocher
    for i, article in enumerate(liste_courses):
        # On utilise l'index `i` pour donner une clé unique à chaque case à cocher
        est_coche = st.checkbox(
            label=article['nom'], 
            value=article['coche'], 
            key=f"article_{i}"
        )
        
        # Si l'état de la case a changé (l'utilisateur a cliqué dessus)
        if est_coche != article['coche']:
            liste_courses[i]['coche'] = est_coche
            sauvegarder_donnees(liste_courses)
            st.rerun() # Rafraîchit pour enregistrer l'état coché/décoché

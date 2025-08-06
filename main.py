import streamlit as st
import gspread
from streamlit_autorefresh import st_autorefresh

# --- INITIALISATION DE LA SESSION ---
# On vérifie si la date du jour n'est pas déjà en mémoire pour la créer une seule fois.
if 'today' not in st.session_state: # <--- 2. AJOUTER CE BLOC
    st.session_state.today = datetime.now()

# --- CONFIGURATION DE LA PAGE ---
# Le reste de votre code est bon, il commence ici...
st.set_page_config(
    page_title="Courses à Saint-Malo",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"


# --- CONNEXION SÉCURISÉE À GOOGLE SHEETS (inchangée) ---
@st.cache_resource
def connect_to_sheet():
    """Initialise la connexion à Google Sheets en utilisant les secrets de Streamlit."""
    sa = gspread.service_account_from_dict(st.secrets["gcp_credentials"])
    sh = sa.open("Liste de Courses App")
    worksheet = sh.sheet1
    return worksheet

worksheet = connect_to_sheet()

# --- FONCTIONS DE GESTION DES DONNÉES (inchangées) ---
def charger_donnees():
    """Charge tous les articles depuis la feuille de calcul."""
    records = worksheet.get_all_records()
    for record in records:
        record['coche'] = (str(record['coche']).upper() == 'TRUE')
    return sorted(records, key=lambda x: x['nom'])

def maj_article(nom_article, est_coche):
    """Met à jour le statut 'coche' d'un article."""
    try:
        cell = worksheet.find(nom_article)
        worksheet.update_cell(cell.row, 2, str(est_coche).upper())
    except gspread.exceptions.CellNotFound:
        pass

def supprimer_selection():
    """Supprime toutes les lignes dont la case est cochée."""
    all_items = charger_donnees()
    items_to_keep = [item for item in all_items if not item['coche']]
    worksheet.clear()
    worksheet.append_row(["nom", "coche"])
    for item in items_to_keep:
        worksheet.append_row([item['nom'], str(item['coche']).upper()])

def tout_effacer():
    """Supprime tous les articles, ne laissant que l'en-tête."""
    worksheet.clear()
    worksheet.append_row(["nom", "coche"])

# --- INTERFACE UTILISATEUR AMÉLIORÉE ---

# Titre principal
st.title("🛒 Liste de Courses")
st.caption(f"Nous sommes le {st.session_state.today.strftime('%A %d %B %Y')}")

# Rafraîchissement automatique pour la synchronisation
st_autorefresh(interval=15000, key="data_refresh") # 15 secondes

# --- BLOC D'ACTIONS ---
with st.form(key='form_ajout', clear_on_submit=True):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        nouvel_article = st.text_input(
            "Ajouter un article",
            placeholder="Ex: Galettes, cidre, beurre salé...",
            label_visibility="collapsed"
        )
    with col2:
        bouton_ajouter = st.form_submit_button(label="Ajouter", use_container_width=True)

# Logique d'ajout avec notification "toast"
if bouton_ajouter and nouvel_article:
    worksheet.append_row([nouvel_article.strip().capitalize(), "FALSE"])
    st.toast(f"✅ '{nouvel_article}' ajouté !")
    st.rerun()

# Chargement et séparation des données
liste_courses = charger_donnees()
articles_a_acheter = [item for item in liste_courses if not item['coche']]
articles_dans_caddie = [item for item in liste_courses if item['coche']]

# --- AFFICHAGE DE LA LISTE ---
col_g, col_d = st.columns(2)

# Colonne de gauche : Compteur et articles à acheter
with col_g:
    st.metric(label="Articles à prendre", value=len(articles_a_acheter))
    
    if not articles_a_acheter and not articles_dans_caddie:
         st.info("Votre liste de courses est vide. Ajoutez un article pour commencer !", icon="📝")
    else:
        with st.container(border=True):
            for article in articles_a_acheter:
                # Si l'utilisateur coche la case
                if st.checkbox(article['nom'], value=False, key=f"add_{article['nom']}"):
                    maj_article(article['nom'], True)
                    st.rerun()

# Colonne de droite : Caddie et actions de suppression
with col_d:
    st.metric(label="Dans le caddie", value=len(articles_dans_caddie))
    with st.container(border=True):
        for article in articles_dans_caddie:
            # Affiche l'article barré et une case cochée
            # Si l'utilisateur décoche la case
            if not st.checkbox(f"~{article['nom']}~", value=True, key=f"remove_{article['nom']}"):
                maj_article(article['nom'], False)
                st.rerun()

# Boutons de suppression en bas pour un look plus propre
if articles_dans_caddie or articles_a_acheter:
    st.markdown("---")
    col_suppr1, col_suppr2 = st.columns(2)
    with col_suppr1:
        if st.button("🗑️ Vider le caddie", use_container_width=True, help="Supprime uniquement les articles cochés"):
            supprimer_selection()
            st.toast("🛒 Caddie vidé !")
            st.rerun()
    with col_suppr2:
        if st.button("🔄 Recommencer la liste", use_container_width=True, type="primary", help="Attention, supprime tout !"):
            tout_effacer()
            st.toast("💥 Liste remise à zéro !")
            st.rerun()

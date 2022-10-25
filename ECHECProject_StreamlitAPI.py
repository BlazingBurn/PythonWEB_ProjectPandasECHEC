import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

st.title("CHESS / ECHECS")
st.header("**PROBLEMATIQUE : Est-ce qu'un opening particulier influt sur la victoire ?**")

st.markdown("* **Opening** ou **Ouverture** correspond a la première phase d'une partie d'échecs. Elle s'arrête lorsque les forces des deux adversaires sont mobilisées et que les rois sont en sécurité.")

from PIL import Image
image = Image.open('chess.jpg')
st.image(image, caption='chess game')

# Read chess data
dataChess=pd.read_csv('games.csv')


# "Unix" to "dateTime"
st.header("Transformation \"Unix\" du dataSet à des valeurs \"dateTime\" :")
dataChessTimes = dataChess[['created_at','last_move_at']].copy()

dataChessTimes['created_at_dt'] = pd.to_datetime(dataChessTimes['created_at']/1000, 
                                           unit='s', 
                                           origin='unix')

dataChessTimes['last_move_at_dt'] = pd.to_datetime(dataChessTimes['last_move_at']/1000, 
                                             unit='s', 
                                             origin='unix')

dataChess['created_at'] = dataChessTimes['created_at_dt']
dataChess['last_move_at'] = dataChessTimes['last_move_at_dt']


# Add game format
st.header("Ajout du format de la partie jouer : ")
def GameType(inc):
    splitted = inc.split('+')
    if int(splitted[0])+int(splitted[1]) <= 9:
        return 'blitz'
    elif int(splitted[0])+int(splitted[1]) <= 16:
        return 'rapid'
    else:
        return 'tournament'

dataChess['format'] = np.vectorize(GameType)(dataChess['increment_code'])

# display data
dataChess

st.header("I. Est-ce que commencer en premier donne un avantage ?")

st.subheader("Seulement les parties classées :")

# Only ranked games
dataChessUtils = dataChess[(dataChess['rated'] == True)]

st.write("Nouveau nombre de parties :",dataChessUtils.shape[0])

st.dataframe(dataChessUtils.head(5))

# Remove non necessary column
st.subheader("Supression des colonnes inutile :")
dataChessUtils = dataChessUtils.drop(columns=['id', 'created_at', 'last_move_at', 'black_id', 'white_id', 'rated', 'opening_ply'])

st.dataframe(dataChessUtils)

# Check outlier in game result
st.subheader("Vérification si il n'y a pas de valeur absurde dans les résultats des matchs (trop grosse différence entre le classement des deux joueurs)")

boxplotGraph = st.radio(
    "Quel graphique boxplot afficher montrant la différence de niveau dans les parties classées ?",
    ('blanc', 'noir'))

if boxplotGraph == 'blanc':
    f, ax = plt.subplots(figsize=(20,5))
    sns.boxplot(data=dataChessUtils,x="white_rating", y="winner", ax=ax).set(title="Graphique montrant la différence de niveau dans les parties classées")
    st.pyplot(f)
else:
    f, ax = plt.subplots(figsize=(20,5))
    sns.boxplot(data=dataChessUtils,x="black_rating", y="winner", ax=ax).set(title="Graphique montrant la différence de niveau dans les parties classées")
    st.pyplot(f)


dataChessUtilsAberrante = dataChessUtils

# Isolation des valeurs aberrantes | WHITE
Q1 = dataChessUtils['white_rating'].quantile(0.25)
Q3 = dataChessUtils['white_rating'].quantile(0.75)

IQR = Q3 - Q1    #IQR is interquartile range. 

filter = (dataChessUtils['white_rating'] >= Q1 - (1.5 * IQR)) & (dataChessUtils['white_rating'] <= Q3 + (1.5 * IQR))
dataChessUtils = dataChessUtils.loc[filter]


# Isolation des valeurs aberrantes | BLACK
Q1 = dataChessUtils['black_rating'].quantile(0.25)
Q3 = dataChessUtils['black_rating'].quantile(0.75)

IQR = Q3 - Q1    #IQR is interquartile range. 

filter = (dataChessUtils['black_rating'] >= Q1 - (1.5 * IQR)) & (dataChessUtils['black_rating'] <= Q3 + (1.5 * IQR))
dataChessUtils = dataChessUtils.loc[filter]

dataChessUtilsNonAberrante = dataChessUtils


if st.button('Issolation des valeurs aberrantes'):
    st.write("Apres isolation des valeurs aberrantes : ")
    st.write(dataChessUtilsNonAberrante.describe())
else:
    st.write("Sans isolation des valeurs aberrantes : ")
    st.write(dataChessUtilsAberrante.describe())


st.header("Les blancs avantagés ?")
st.subheader("Histogrammes par rapport au chance de gagner en étant noir ou blanc :")


subplotGraph = st.radio(
    "Quel graphique histogramme afficher montrant la victoire suivant le classement ?",
    ('blanc', 'noir'))

if subplotGraph == 'blanc':
    # Creation visuel pour la victoire des blancs en fonction de leur rang
    f, ax = plt.subplots(figsize=(20,5))
    sns.histplot(data=dataChessUtils, x='white_rating', hue='winner', ax=ax).set(title='Histogramme de victoire des joueurs blanc par rapport au classement')
    st.pyplot(f)
else:
    # Creation visuel pour la victoire des noirs en fonction de leur rang
    f, ax = plt.subplots(figsize=(20,5))
    sns.histplot(data=dataChessUtils, x='black_rating', hue='winner', ax=ax).set(title='Histogramme de victoire des joueurs noir par rapport au classement')
    st.pyplot(f)


# Check victory type
st.subheader("Vérification du type de victoire")
# exploding pie
explode = [0.1, 0, 0]
# Seaborn color
colors = sns.color_palette('pastel')[0:5]

data = dataChessUtils['winner'].value_counts()
keys = dataChessUtils['winner'].value_counts().index.tolist()

# chart
plt.pie(data, labels=keys, colors=colors, 
        explode=explode, autopct='%.0f%%',
        shadow = 'True', textprops = {'color': 'Black','fontsize':14}, 
        wedgeprops = {'linewidth': 2}, startangle = 90)
  
# displaying chart
fig = plt.gcf()
fig.set_size_inches(18.5, 10.5)
plt.show()
st.pyplot(fig)


# A specific opening is stronger than another ?
st.header("II. Existe-t-il un opening plus fort que les autres ?")

st.subheader("Meilleurs opening :")

dataChessWhiteWin = dataChessUtils[(dataChessUtils['victory_status'] != 'draw')]
temp_dict = dict(dataChessWhiteWin['opening_name'].value_counts()[0:5])
top_opening_white = list(temp_dict.keys())
temp_df = dataChessUtils[dataChessUtils['opening_name'].isin(top_opening_white)]

f, ax = plt.subplots(figsize=(20,5))
sns.countplot(data=temp_df, x='opening_name', hue='victory_status', ax=ax).set(title='Cinq meilleurs opening')
st.pyplot(f)


dataChessOpeningCompare = dataChessUtils[(dataChessUtils['opening_name'].isin(top_opening_white))]
f, ax = plt.subplots(figsize=(20,5))
sns.countplot(data=dataChessOpeningCompare, y='opening_name', hue='winner', ax=ax).set(title='Comparaison des cinqs meilleurs opening en fonction du vainqueur du match')
st.pyplot(f)


# Opening depending on game type
st.subheader("Opening en fonction du type de partie (blitz, rapide, tournoi)")
f, ax = plt.subplots(figsize=(20,5))
sns.countplot(data=dataChessOpeningCompare, x='format', hue='opening_name', ax=ax).set(title="Choix de l'opening en fonction du format de la partie")
st.pyplot(f)


st.header("Conclusion")
st.write("Il existe bien des openings pour augmenter ces chances de gagner mais on rappel que les echecs ce base aussi sur l'adaptabilité et que généralement l'opening influt seulement sur le début et milieu de partie et que pour la fin cela nécessite de prédire les mouvements de son adversaire pour retourner la situation ou maintenir la présion mentale mise sur l'adversaire.")
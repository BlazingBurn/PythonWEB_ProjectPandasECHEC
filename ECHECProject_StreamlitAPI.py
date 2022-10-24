import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Read chess data
st.write("Start get data from csv .....")
dataChess=pd.read_csv('games.csv')
st.write("End get data from csv .....")


# "Unix" to "dateTime"
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

# Only ranked games
dataChessUtils = dataChess[(dataChess['rated'] == True)]

st.write("Nouveau nombre de parties :",dataChessUtils.shape[0])

st.dataframe(dataChessUtils.head(5))

# Remove non necessary column
dataChessUtils = dataChessUtils.drop(columns=['id', 'created_at', 'last_move_at', 'black_id', 'white_id', 'rated', 'opening_ply'])

st.dataframe(dataChessUtils)

# Check outlier in game result
f, ax = plt.subplots(figsize=(20,5))
sns.boxplot(data=dataChessUtils,x="white_rating", y="winner", ax=ax).set(title="Graphique montrant la différence de niveau dans les parties classées")
st.pyplot(f)

f, ax = plt.subplots(figsize=(20,5))
sns.boxplot(data=dataChessUtils,x="black_rating", y="winner", ax=ax).set(title="Graphique montrant la différence de niveau dans les parties classées")
st.pyplot(f)

st.write(dataChessUtils.describe())

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


st.write(dataChessUtils.describe())


# Creation visuel pour la victoire des blancs en fonction de leur rang
f, ax = plt.subplots(figsize=(20,5))
sns.histplot(data=dataChessUtils, x='white_rating', hue='winner', ax=ax).set(title='Histogramme de victoire des joueurs blanc par rapport au classement')
st.pyplot(f)


# Creation visuel pour la victoire des noirs en fonction de leur rang
f, ax = plt.subplots(figsize=(20,5))
sns.histplot(data=dataChessUtils, x='black_rating', hue='winner', ax=ax).set(title='Histogramme de victoire des joueurs noir par rapport au classement')
st.pyplot(f)


# Check victory type
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
f, ax = plt.subplots(figsize=(20,5))
sns.countplot(data=dataChessOpeningCompare, x='format', hue='opening_name', ax=ax).set(title="Choix de l'opening en fonction du format de la partie")
st.pyplot(f)
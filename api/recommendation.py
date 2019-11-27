import pandas as pd
import numpy as np
import pickle
from flask import Blueprint, request, jsonify
from sklearn.neighbors import NearestNeighbors

bp = Blueprint('note', __name__)

rating = pd.read_csv('./instance/rating.csv').query('rating >= 0').drop_duplicates(['user_id', 'anime_id'])
anime = pd.read_csv('./instance/anime.csv').query('members > 10000').dropna()

rating_m = rating.merge(anime, how = 'inner', left_on = 'anime_id', right_on = 'anime_id', suffixes= ['', '_anime']).\
    drop(['name', 'genre', 'type', 'episodes', 'rating_anime', 'members'], axis = 1)
anime_m = anime.merge(pd.DataFrame(rating_m['anime_id'].unique()), how = 'inner', left_on = 'anime_id', right_on = 0).\
    drop([0], axis = 1).sort_values('anime_id').reset_index().drop(['index'], axis = 1)

with open('./instance/knn.pickle', mode = 'rb') as fp:
    model_knn = pickle.load(fp)


@bp.route('/recommendations', methods=['GET'])
def index():
    name :string = request.args.get('name')
    ret = []

    try:
        anime_id = anime_m[anime_m.name == name]['anime_id'].values[0]
    except:
        return jsonify(ret), 200

    self = rating_m.drop_duplicates(subset = 'user_id').loc[:, ['user_id']].\
        merge(rating_m[rating_m.anime_id == anime_id].loc[:, ['user_id', 'rating']], on = 'user_id', how = 'left').\
        fillna(0).sort_values('user_id')['rating'].values.reshape(1,-1)

    distance, indice = model_knn.kneighbors(self, n_neighbors = 11)

    for i in range(0, len(indice.flatten())):
        ret += {
                   "name":anime_m.iloc[indice.flatten()[i]]['name'],
                   "genre":anime_m.iloc[indice.flatten()[i]]['genre'],
                   "type":anime_m.iloc[indice.flatten()[i]]['type'],
                   "episodes":anime_m.iloc[indice.flatten()[i]]['episodes'],
               },

    return jsonify(ret), 200

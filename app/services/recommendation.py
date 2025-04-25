from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from app.db.db import get_connection
import numpy as np

# Function to get user-product interaction data
def get_user_product_data():
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT u.UserName, u.ProductId, COUNT(*) as Interaction
        FROM UserCartTbl u
        GROUP BY u.UserName, u.ProductId;
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=['UserName', 'ProductId', 'Interaction'])
    connection.close()
    return df


# Function to generate recommendations for users
def generate_recommendations():
    df = get_user_product_data()

    if df.empty:
        return {}

    user_item_matrix = df.pivot(index='UserName', columns='ProductId', values='Interaction').fillna(0)
    interaction_matrix = user_item_matrix.values
    cosine_sim = cosine_similarity(interaction_matrix)

    recommendations = {}
    for user_idx, user in enumerate(user_item_matrix.index):
        user_similarities = cosine_sim[user_idx]
        similar_users = user_similarities.argsort()[-2::-1]

        recommended_products = set()
        for similar_user in similar_users:
            interacted_products = np.nonzero(user_item_matrix.iloc[similar_user].values)[0]
            recommended_products.update(interacted_products)

        user_interacted_products = np.nonzero(user_item_matrix.iloc[user_idx].values)[0]
        recommended_products = [prod for prod in recommended_products if prod not in user_interacted_products]

        # Convert column indices to actual product IDs (and cast to str or int)
        recommended_product_ids = user_item_matrix.columns[recommended_products].values
        recommended_product_ids = [int(pid) if isinstance(pid, (np.integer, np.int64)) else str(pid) for pid in recommended_product_ids]

        recommendations[user] = recommended_product_ids[:5]

    return recommendations

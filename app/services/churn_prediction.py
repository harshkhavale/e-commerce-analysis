from sklearn.ensemble import RandomForestClassifier
from app.db.db import get_connection
import pandas as pd
from datetime import datetime

def predict_churn(user_data):
    try:
        # Connect to the database
        connection = get_connection()

        # Fetch user activity data
        query = """
            SELECT UserId, ActivityType, ActivityDate
            FROM UserActivityTbl
        """
        data = pd.read_sql(query, connection)
        connection.close()

        # Convert ActivityDate to datetime
        data['ActivityDate'] = pd.to_datetime(data['ActivityDate'])

        # Feature engineering
        today = pd.Timestamp(datetime.now())

        user_features = (
            data.groupby('UserId')
            .agg(
                LastPurchase=('ActivityDate', lambda x: (today - x.max()).days),
                TotalPurchases=('ActivityType', lambda x: (x == 'purchase').sum()),
                TotalSessions=('ActivityDate', 'count')
            )
            .reset_index()
        )

        # Fake churn labels for demo purposes (real use: historical churn labels)
        user_features['Churned'] = user_features['LastPurchase'].apply(lambda x: 1 if x > 30 else 0)

        # Define input/output
        X = user_features[['LastPurchase', 'TotalPurchases', 'TotalSessions']]
        y = user_features['Churned']

        # Train the model
        model = RandomForestClassifier()
        model.fit(X, y)

        # Predict for incoming user data
        prediction = model.predict([user_data])
        return int(prediction[0])  # Make sure it's serializable

    except Exception as e:
        return {'error': str(e)}

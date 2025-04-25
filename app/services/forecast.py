import pandas as pd
from prophet import Prophet
from app.db.db import get_connection

def generate_forecast():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT DATE(DateTime) as order_date, COUNT(*) as sales
        FROM ProductDeliveryTbl
        WHERE DateTime IS NOT NULL
        GROUP BY order_date
        ORDER BY order_date;
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    df = pd.DataFrame(data, columns=["ds", "y"])

    if df.shape[0] < 2:
        return {'error': 'Not enough data to forecast.'}

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    return forecast[['ds', 'yhat']].tail(30).to_dict(orient='records')

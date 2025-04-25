import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import seaborn as sns
from app.db.db import get_connection
import os

def segment_customers(n_clusters=3, visualize=False):
    try:
        # Get database connection
        conn = get_connection()

        # Fetch delivery data
        df = pd.read_sql("SELECT UserName, ProductId, DateTime FROM ProductDeliveryTbl", conn)
        if df.empty:
            return {"error": "No delivery data found."}

        df['DateTime'] = pd.to_datetime(df['DateTime'])

        # Aggregate by customer
        summary = df.groupby('UserName').agg(
            total_orders=pd.NamedAgg(column="ProductId", aggfunc="count"),
            last_order=pd.NamedAgg(column="DateTime", aggfunc="max")
        ).reset_index()

        summary['recency_days'] = (pd.Timestamp.now() - summary['last_order']).dt.days

        # Get price data
        price_df = pd.read_sql("SELECT ProductId, ProductSellingPrice FROM ProductDataTbl", conn)
        df = df.merge(price_df, on="ProductId", how="left")

        avg_value = df.groupby('UserName').agg(
            avg_order_value=pd.NamedAgg(column="ProductSellingPrice", aggfunc="mean")
        ).reset_index()

        summary = summary.merge(avg_value, on="UserName")
        summary.fillna(0, inplace=True)

        # Prepare data for clustering
        features = summary[['total_orders', 'recency_days', 'avg_order_value']]
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        summary['cluster'] = kmeans.fit_predict(features)

        # Optional visualization
        image_path = None
        if visualize:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(
                x="total_orders",
                y="avg_order_value",
                hue="cluster",
                data=summary,
                palette="viridis"
            )
            plt.title("Customer Segments")
            plt.xlabel("Total Orders")
            plt.ylabel("Average Order Value")
            image_path = "static/cluster_plot.png"
            plt.savefig(image_path)
            plt.close()

        # Prepare response
        segment_counts = summary['cluster'].value_counts().to_dict()

        return {
            "segments": segment_counts,
            "visualization": image_path
        }

    except Exception as e:
        return {"error": str(e)}

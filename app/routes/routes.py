from flask import Blueprint, jsonify, request
from app.services.forecast import generate_forecast
from app.services.segmentation import segment_customers
from app.services.recommendation import generate_recommendations
from app.services.churn_prediction import predict_churn
routes = Blueprint('routes', __name__)

# Sales Forecast Route
@routes.route('/api/sales-forecast', methods=['GET'])
def sales_forecast():
    result = generate_forecast()
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result)

# Customer Segmentation Route
@routes.route('/api/segment-customers', methods=['GET'])
def customer_segmentation():
    try:
        clusters = int(request.args.get('clusters', 3))
        visualize = request.args.get('visualize', 'false').lower() == 'true'

        result = segment_customers(n_clusters=clusters, visualize=visualize)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify({
            'status': 'success',
            'segments': result['segments'],
            'visualization_path': result.get('visualization')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# Recommendation Route
@routes.route('/api/recommendations', methods=['GET'])
def recommendations():
    try:
        username = request.args.get('username')
        if not username:
            return jsonify({'error': 'Username is required'}), 400

        # Generate recommendations
        recommendations = generate_recommendations()

        # Get recommendations for the requested username
        if username in recommendations:
            return jsonify({'recommended_products': recommendations[username]})
        else:
            return jsonify({'error': f'No recommendations found for username: {username}'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Churn Prediction Route
@routes.route('/api/predict-churn', methods=['GET'])
def churn_prediction():
    try:
        # Get user_data from query param (e.g., "15,5,20")
        raw_data = request.args.get("user_data")
        if not raw_data:
            return jsonify({'error': 'user_data is required'}), 400

        # Convert comma-separated string to list of ints/floats
        user_data = [float(x) for x in raw_data.split(",")]

        # Call the prediction function
        prediction = predict_churn(user_data)
        return jsonify({'churn_prediction': prediction})

    except Exception as e:
        return jsonify({'churn_prediction': {'error': str(e)}}), 500
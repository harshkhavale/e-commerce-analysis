
## 🚀 Project Setup Guide

### 1. 📦 Create Virtual Environment
```bash
python -m venv venv

source venv/bin/activate        # On Linux/macOS
# or
venv\Scripts\activate           # On Windows
```

### 2. 📥 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. ⚙️ Set Environment Variables
- Use `example.env` as a reference.
- Create a `.env` file and fill in your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=ShoeStore
```

### 4. 🌱 Seed the Database with Fake Data
```bash
python seed.py
```

### 5. 🏁 Start the API Server
```bash
python run.py
```

---

## 🔥 Bonus: What You Can Add to Your PHP E-commerce

| Feature                  | Tech Stack          | Integration Idea                                |
|--------------------------|---------------------|--------------------------------------------------|
| 📈 Sales Forecast        | Python (Prophet/LSTM)| Show graphs on PHP dashboard via API            |
| 🧠 Customer Segmentation | Python (KMeans)      | Store cluster IDs in DB, use in PHP logic       |
| 💬 Product Recommendation| Python (SVD/NMF)     | Show related products dynamically               |
| 💰 Churn Prediction      | Python (LogReg/XGB)  | Highlight risky users in admin panel            |
| 📊 Data Dashboard        | Chart.js / Streamlit | Embed Streamlit via iframe or call via API      |

---

## 🔗 API Endpoints

### ✅ 1. **Sales Forecast**
```bash
curl -X GET http://localhost:5000/api/sales-forecast
```

---

### ✅ 2. **Customer Segmentation**

#### ➤ Default (3 clusters, no plot)
```bash
curl -X GET http://localhost:5000/api/segment-customers
```

#### ➤ Custom Clusters + Visualize
```bash
curl -G http://localhost:5000/api/segment-customers \
     --data-urlencode "clusters=5" \
     --data-urlencode "visualize=true"
```

---

### ✅ 3. **Product Recommendation**

#### ➤ For a specific user:
```bash
curl -G http://localhost:5000/api/recommendations \
     --data-urlencode "user_id=user123"
```

---

### ✅ 4. **Churn Prediction**

#### ➤ Provide user data:
```bash
curl -G http://localhost:5000/api/predict-churn \
     --data-urlencode "user_data=45" \
     --data-urlencode "user_data=20000" \
     --data-urlencode "user_data=3"
```
> Replace values as per model input: e.g., age, income, orders, etc.

---
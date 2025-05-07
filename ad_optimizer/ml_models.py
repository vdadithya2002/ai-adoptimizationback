import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

from ad_optimizer.models import AdPlatformData


def train_reach_prediction_model():
    # Get all records from DB
    data = list(AdPlatformData.objects.all().values())
    df = pd.DataFrame(data)

    if df.empty:
        return "No data available for training"

    # One-hot encode platform column
    ohe = OneHotEncoder()
    platform_encoded = ohe.fit_transform(df[['platform']]).toarray()
    encoded_df = pd.DataFrame(platform_encoded, columns=ohe.get_feature_names_out(['platform']))

    df = pd.concat([df, encoded_df], axis=1)
    df.drop(['platform', 'id'], axis=1, inplace=True)

    X = df.drop(['reach'], axis=1)
    y = df['reach']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Save the model and encoder
    joblib.dump(model, 'ml_models/reach_predictor.pkl')
    joblib.dump(ohe, 'ml_models/platform_encoder.pkl')

    return "Model trained and saved."


def predict_reach(platform, budget, impressions, clicks, cost_per_click):
    model = joblib.load('ml_models/reach_predictor.pkl')
    encoder = joblib.load('ml_models/platform_encoder.pkl')
    
    input_data = pd.DataFrame([{
        'platform': platform,
        'budget': budget,
        'impressions': impressions,
        'clicks': clicks,
        'cost_per_click': cost_per_click
    }])
    predicted_reach = model.predict(input_data)[0]
    return predicted_reach

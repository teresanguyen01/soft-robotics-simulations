import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# 1. Define the upper-body joint names (your prediction targets)
upper_body = [
    'x','y','z','qw','qx','qy','qz',
    'abdomen_z_0','abdomen_z_1',
    'shoulder1_right_0','shoulder1_right_1',
    'shoulder1_left_0','shoulder1_left_1',
    'abdomen_x','elbow_right','elbow_left'
]

# 2. Load the preprocessed dataset
df = pd.read_csv('sensor_angles_features_imputed.csv')

print(df.columns.tolist())


# 3. Separate inputs (X) and outputs (y)
feature_cols = [c for c in df.columns if c not in ['time_ms'] + upper_body]
X = df[feature_cols].values
y = df[upper_body].values

# 4. Split into train/validation/test sets (70/15/15)
X_train, X_tmp, y_train, y_tmp = train_test_split(
    X, y, test_size=0.30, random_state=42
)
X_val, X_test, y_val, y_test = train_test_split(
    X_tmp, y_tmp, test_size=0.50, random_state=42
)

# 5. Configure the MLP regressor
model = MLPRegressor(
    hidden_layer_sizes=(128, 64),
    activation='relu',
    solver='adam',
    alpha=1e-4,            # L2 regularization
    learning_rate_init=1e-3,
    max_iter=200,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=10,
    random_state=42,
    verbose=True
)

# 6. Train the model
print("Training MLPRegressor...")
model.fit(X_train, y_train)

# 7. Evaluate on validation set
y_val_pred = model.predict(X_val)
rmse_val = mean_squared_error(y_val, y_val_pred) ** 0.5
r2_val   = r2_score(y_val, y_val_pred)
print(f"Validation RMSE: {rmse_val:.4f}, R²: {r2_val:.4f}")

# 8. Final evaluation on test set
y_test_pred = model.predict(X_test)
rmse_test = mean_squared_error(y_test, y_test_pred) ** 0.5
r2_test   = r2_score(y_test, y_test_pred)
print(f"Test RMSE: {rmse_test:.4f}, R²: {r2_test:.4f}")


# 9. Per-joint RMSE
per_joint_rmse = np.sqrt(np.mean((y_test - y_test_pred)**2, axis=0))
for name, err in zip(upper_body, per_joint_rmse):
    print(f"{name:20s} RMSE = {err:.4f}")

# 10. Save the trained model to disk
joblib.dump(model, 'upper_body_angle_model.pkl')
print("Model saved to 'upper_body_angle_model.pkl'")

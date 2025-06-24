import pandas as pd
from sklearn.impute import SimpleImputer

# 1. Load the raw features CSV (may contain NaNs)
df = pd.read_csv('sensor_angles_features.csv')

# 2. Declare your timestamp and true upper-body joint columns exactly as they appear
time_col = 'time_ms'

upper_body = [
    'x', 'y', 'z',
    'qw', 'qx', 'qy', 'qz',
    'abdomen_z_0', 'abdomen_z_1',
    'shoulder1_right_0', 'shoulder1_right_1',
    'shoulder1_left_0', 'shoulder1_left_1',
    'abdomen_x', 'elbow_right', 'elbow_left'
]

# 3. Build list of feature columns by excluding time + targets
non_feature_cols = [time_col] + upper_body
feature_cols     = [c for c in df.columns if c not in non_feature_cols]

# 4. Identify & drop columns that are entirely NaN
all_nan = df[feature_cols].isna().all()
dropped_cols = all_nan[all_nan].index.tolist()
if dropped_cols:
    print(f"Dropping {len(dropped_cols)} all‐NaN columns: {dropped_cols}")
    feature_cols = [c for c in feature_cols if c not in dropped_cols]

# 5. Extract features and sanity‐check its shape
X_features = df[feature_cols]
print(f"Feature matrix shape before impute: {X_features.shape}")

# 6. Impute missing feature values (mean strategy)
imputer = SimpleImputer(strategy='mean')
X_imputed_np = imputer.fit_transform(X_features)

# 7. Sanity‐check imputed array’s shape
print(f"Imputed array shape: {X_imputed_np.shape}")
assert X_imputed_np.shape[1] == len(feature_cols), (
    "Mismatch between imputed width and feature_cols length"
)

# 8. Rebuild a DataFrame for the imputed features
df_imputed = pd.DataFrame(X_imputed_np, columns=feature_cols)

# 9. Concatenate timestamp, targets, and imputed features
df_out = pd.concat([df[[time_col] + upper_body], df_imputed], axis=1)

# 10. Save the fully imputed DataFrame
output_path = 'sensor_angles_features_imputed.csv'
df_out.to_csv(output_path, index=False)
print(f"Saved imputed features to '{output_path}'")
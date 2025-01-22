import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GRU, BatchNormalization, GaussianDropout, GaussianNoise
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

train_df = pd.read_excel("C:/Users/evan0/Downloads/full map.xlsx", header=0)
test_df = pd.read_excel("C:/Users/evan0/Downloads/sin.xlsx", header=0)

train_df['RSSI1_lag1'] = train_df['RSSI1'].shift(1).fillna(0)
train_df['RSSI2_lag1'] = train_df['RSSI2'].shift(1).fillna(0)
train_df['RSSI3_lag1'] = train_df['RSSI3'].shift(1).fillna(0)
train_df['RSSI4_lag1'] = train_df['RSSI4'].shift(1).fillna(0)

test_df['RSSI1_lag1'] = test_df['RSSI1'].shift(1).fillna(0)
test_df['RSSI2_lag1'] = test_df['RSSI2'].shift(1).fillna(0)
test_df['RSSI3_lag1'] = test_df['RSSI3'].shift(1).fillna(0)
test_df['RSSI4_lag1'] = test_df['RSSI4'].shift(1).fillna(0)

X_train = train_df[['RSSI1', 'RSSI2', 'RSSI3', 'RSSI4', 'RSSI1_lag1', 'RSSI2_lag1', 'RSSI3_lag1', 'RSSI4_lag1']].values
y_train = train_df[['X', 'Y']].values

X_test = test_df[['RSSI1', 'RSSI2', 'RSSI3', 'RSSI4', 'RSSI1_lag1', 'RSSI2_lag1', 'RSSI3_lag1', 'RSSI4_lag1']].values
y_test = test_df[['X', 'Y']].values

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = Sequential([
    Dense(512, activation='relu', input_shape=(8,)),
    #GaussianDropout(0.2),
    Dense(256, activation='relu'),
    Dense(256, activation='relu'),
    Dense(256, activation='relu'),
    Dense(256, activation='relu'),
    Dense(256, activation='relu'),
    #GaussianDropout(0.2),
    #BatchNormalization(),
    Dense(128, activation='relu'),
    #GaussianDropout(0.2),
    Dense(64, activation='relu'),
    Dense(2)
])

model.compile(optimizer='Adam', loss='mse', metrics=['mae'])

history = model.fit(X_train, y_train, epochs=200, batch_size=3, verbose=1)

loss, mae = model.evaluate(X_test, y_test)
print(f'Mean Absolute Error: {mae}')

y_pred = model.predict(X_test)

r2_x = r2_score(y_test[:, 0], y_pred[:, 0])
r2_y = r2_score(y_test[:, 1], y_pred[:, 1])
print(f"R² score for X: {r2_x}")
print(f"R² score for Y: {r2_y}")

mae_x = mean_absolute_error(y_test[:, 0], y_pred[:, 0])
mae_y = mean_absolute_error(y_test[:, 1], y_pred[:, 1])
print(f"MAE for X: {mae_x}")
print(f"MAE for Y: {mae_y}")

mse_x = mean_squared_error(y_test[:, 0], y_pred[:, 0])
mse_y = mean_squared_error(y_test[:, 1], y_pred[:, 1])
print(f"MSE for X: {mse_x}")
print(f"MSE for Y: {mse_y}")

rmse_x = np.sqrt(mse_x)
rmse_y = np.sqrt(mse_y)
print(f"RMSE for X: {rmse_x}")
print(f"RMSE for Y: {rmse_y}")

average_r2 = (r2_x + r2_y) / 2
average_mae = (mae_x + mae_y) / 2
average_mse = (mse_x + mse_y) / 2
average_rmse = (rmse_x + rmse_y) / 2

print("\nAverages:")
print(f"Average R² score: {average_r2}")
print(f"Average MAE: {average_mae}")
print(f"Average MSE: {average_mse}")
print(f"Average RMSE: {average_rmse}")

plt.figure(figsize=(14, 6))

plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['mae'], label='Training MAE')
plt.plot(history.history['val_mae'], label='Validation MAE')
plt.xlabel('Epochs')
plt.ylabel('MAE')
plt.title('Training and Validation MAE')
plt.legend()

plt.tight_layout()
plt.show()

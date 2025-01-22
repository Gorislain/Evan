#CNN+GRU:
import numpy as np
import pandas as pd
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, GRU, Dense, Concatenate, TimeDistributed, GlobalAveragePooling1D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import StandardScaler, LabelEncoder

train_data_path = "C:/Users/evan0/Desktop/west/data.xlsx"
test_data_path = "C:/Users/evan0/Desktop/west/data.xlsx"
train_data = pd.read_excel(train_data_path, usecols=[1, 3, 2])
test_data = pd.read_excel(test_data_path, usecols=[1, 3, 2])

scaler = StandardScaler()
label_encoder = LabelEncoder()
train_data[['Pulse', 'Extracted Value 35.0']] = scaler.fit_transform(train_data[['Pulse', 'Extracted Value 35.0']])
train_data['Validation'] = label_encoder.fit_transform(train_data['Validation'])
test_data[['Pulse', 'Extracted Value 35.0']] = scaler.transform(test_data[['Pulse', 'Extracted Value 35.0']])
test_data['Validation'] = label_encoder.transform(test_data['Validation'])

def unified_generator(image_dir, numeric_data, labels, batch_size):
    image_generator = ImageDataGenerator(rescale=1./255).flow_from_directory(
        image_dir,
        target_size=(48, 48),
        class_mode=None,
        batch_size=batch_size,
        shuffle=False
    )

    num_samples = len(numeric_data)
    while True:
        for start in range(0, num_samples, batch_size):
            end = min(start + batch_size, num_samples)
            batch_indices = range(start, end)

            try:
                image_batch = next(image_generator)
            except StopIteration:
                image_generator = ImageDataGenerator(rescale=1./255).flow_from_directory(
                    image_dir,
                    target_size=(48, 48),
                    class_mode=None,
                    batch_size=batch_size,
                    shuffle=False
                )
                image_batch = next(image_generator)

            numeric_batch = numeric_data.iloc[batch_indices].to_numpy()
            labels_batch = labels.iloc[batch_indices].to_numpy()
            labels_batch = to_categorical(labels_batch, num_classes=6) 

            image_batch = np.expand_dims(image_batch, axis=1)
            numeric_batch = np.expand_dims(numeric_batch, axis=1)

            yield [image_batch, numeric_batch], labels_batch


image_input = Input(shape=(None, 48, 48, 3))
numeric_input = Input(shape=(None, 2))

cnn = TimeDistributed(Conv2D(48, (3, 3), activation='relu', padding='same'))(image_input)
cnn = TimeDistributed(MaxPooling2D((2, 2), padding='same'))(cnn)
cnn = TimeDistributed(Conv2D(24, (3, 3), activation='relu', padding='same'))(cnn)
cnn = TimeDistributed(MaxPooling2D((2, 2), padding='same'))(cnn)
cnn = TimeDistributed(Flatten())(cnn)
cnn = GlobalAveragePooling1D()(cnn)

gru = GRU(24, return_sequences=True)(numeric_input)
gru = GlobalAveragePooling1D()(gru)

combined = Concatenate()([cnn, gru])

fc = Dense(24, activation='relu')(combined)
fc = Dense(12, activation='relu')(fc)
output = Dense(6, activation='softmax')(fc)

model = Model(inputs=[image_input, numeric_input], outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

train_generator = unified_generator("C:/Users/evan0/Desktop/train30f", train_data[['Pulse', 'Extracted Value 35.0']], train_data['Validation'], 16)
test_generator = unified_generator("C:/Users/evan0/Desktop/train30f", test_data[['Pulse', 'Extracted Value 35.0']], test_data['Validation'], 16)

history = model.fit(
    train_generator,
    steps_per_epoch=len(train_data) // 11,
    validation_data=test_generator,
    validation_steps=len(test_data) // 11,
    epochs=300
)

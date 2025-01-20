import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
import matplotlib.pyplot as plt

# Задаем размеры изображений и количество классов
img_width, img_height = 48, 48
num_classes = 6

# Задаем количество эпох и размер мини-пакета
epochs = 2000
batch_size = 9
# Создаем генераторы для загрузки и аугментации изображений
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

train_generator = train_datagen.flow_from_directory(
    "C:/Users/evan0/Desktop/trainf001",
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical')
# Создаем генератор для валидации данных
validation_datagen = ImageDataGenerator(rescale=1./255)
validation_generator = validation_datagen.flow_from_directory(
    "C:/Users/evan0/Desktop/testf001",
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode='categorical')
# Создаем модель CNN
model = Sequential()
model.add(Conv2D(4, (3, 3), activation='silu', input_shape=(img_width, img_height, 3), padding='same'))
model.add(MaxPooling2D((2, 2), padding='same'))
model.add(BatchNormalization())

model.add(Conv2D(8, (3, 3), activation='silu', padding='same'))
model.add(MaxPooling2D((2, 2), padding='same'))
model.add(BatchNormalization())

model.add(Conv2D(16, (3, 3), activation='silu', padding='same'))
model.add(MaxPooling2D((2, 2), padding='same'))
model.add(Dropout(0.05))

model.add(Conv2D(32, (3, 3), activation='silu', padding='same'))
model.add(MaxPooling2D((2, 2), padding='same'))
model.add(Dropout(0.05))

model.add(Conv2D(64, (3, 3), activation='silu', padding='same'))
model.add(MaxPooling2D((2, 2), padding='same'))
model.add(BatchNormalization())

model.add(Flatten())
model.add(Dense(64, activation='silu'))
model.add(Dense(num_classes, activation='softplus'))
model.add(Dense(32, activation='silu'))
model.add(Dense(num_classes, activation='softplus'))
model.add(Dense(16, activation='silu'))
model.add(Dense(num_classes, activation='softplus'))
model.add(Dense(8, activation='silu'))
model.add(Dropout(0.05))
model.add(Dense(num_classes, activation='softplus'))
model.add(Dense(4, activation='silu'))
model.add(Dropout(0.05))
model.add(Dense(num_classes, activation='softplus'))

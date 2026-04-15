import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# =========================
# CONFIGURACIÓN
# =========================
DATASET_DIR = "database"   # carpeta con subcarpetas: organico / inorganico
IMG_SIZE = (224, 224)
BATCH_SIZE = 16
EPOCHS = 10
FINE_TUNE_EPOCHS = 3
MODEL_PATH = "modelo_residuos.keras"

# =========================
# CARGA DEL DATASET
# =========================
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    DATASET_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE
)

class_names = train_ds.class_names
print("Clases detectadas:", class_names)

# Optimización
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

# =========================
# AUMENTO DE DATOS
# =========================
data_augmentation = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.15),
    layers.RandomZoom(0.15),
    layers.RandomTranslation(0.1, 0.1),
    layers.RandomContrast(0.1),
])

# =========================
# MODELO BASE
# =========================
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet"
)

# primera etapa: congelado
base_model.trainable = False

inputs = keras.Input(shape=(224, 224, 3))
x = data_augmentation(inputs)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.2)(x)
outputs = layers.Dense(1, activation="sigmoid")(x)

model = keras.Model(inputs, outputs)

model.compile(
    optimizer=keras.optimizers.Adam(),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

# =========================
# ENTRENAMIENTO INICIAL
# =========================
print("\nEntrenamiento inicial...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS
)

# =========================
# FINE-TUNING CORTO
# =========================
print("\nIniciando fine-tuning corto...")

base_model.trainable = True

# congelar casi todas las capas y dejar libres solo las últimas
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(1e-5),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=FINE_TUNE_EPOCHS
)

# =========================
# GUARDAR MODELO
# =========================
model.save(MODEL_PATH)
print(f"\nModelo guardado en: {MODEL_PATH}")
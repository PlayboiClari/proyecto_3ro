import cv2
import numpy as np
import tensorflow as tf

# =========================
# CONFIGURACIÓN
# =========================
MODEL_PATH = "modelo_residuos.keras"
IMG_SIZE = (224, 224)
CAMERA_INDEX = 1   # cambia a 0 si tu cámara principal no abre
PRED_EVERY_N_FRAMES = 8   # predecir cada 8 frames
UMBRAL_ORGANICO = 0.75
UMBRAL_INORGANICO = 0.25

# =========================
# CARGAR MODELO
# =========================
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# Ajusta si el orden real de tu dataset fue otro
class_names = ["inorganico", "organico"]

# =========================
# FUNCIÓN DE PREDICCIÓN
# =========================
def predecir_objeto(frame):
    img = cv2.resize(frame, IMG_SIZE)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)

    # mismo preprocess que MobileNetV2
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    pred = model.predict(img_array, verbose=0)[0][0]

    # pred cerca de 0 -> inorganico
    # pred cerca de 1 -> organico
    if pred >= UMBRAL_ORGANICO:
        etiqueta = class_names[1]
        confianza = pred
    elif pred <= UMBRAL_INORGANICO:
        etiqueta = class_names[0]
        confianza = 1 - pred
    else:
        etiqueta = "incierto"
        confianza = max(pred, 1 - pred)

    return etiqueta, float(confianza), float(pred)

# =========================
# ABRIR WEBCAM
# =========================
webcam = cv2.VideoCapture(CAMERA_INDEX)

if not webcam.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

# bajar resolución para que no caliente tanto
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

frame_count = 0
ultima_etiqueta = "incierto"
ultima_confianza = 0.0
ultimo_pred = 0.5

while True:
    ret, frame = webcam.read()
    if not ret:
        print("No se pudo leer el frame.")
        break

    frame_count += 1

    # Definir una región central para analizar
    h, w, _ = frame.shape
    x1, y1 = int(w * 0.3), int(h * 0.2)
    x2, y2 = int(w * 0.7), int(h * 0.8)

    roi = frame[y1:y2, x1:x2]

    # Solo predecir cada N frames
    if frame_count % PRED_EVERY_N_FRAMES == 0:
        ultima_etiqueta, ultima_confianza, ultimo_pred = predecir_objeto(roi)

    # Color según la clase
    if ultima_etiqueta == "organico":
        color = (0, 255, 0)
        texto = f"Organico ({ultima_confianza*100:.1f}%)"
    elif ultima_etiqueta == "inorganico":
        color = (0, 0, 255)
        texto = f"Inorganico ({ultima_confianza*100:.1f}%)"
    else:
        color = (0, 255, 255)
        texto = f"No claro ({ultimo_pred:.2f})"

    # Dibujar rectángulo y texto
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(
        frame,
        texto,
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2
    )

    cv2.imshow("Deteccion de Residuos", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()
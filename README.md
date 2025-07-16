# WebRTC Camera Stream 📹

Proyecto simple de transmisión de cámara web usando WebRTC con Python (aiortc) y OpenCV.

## Características

- ✅ Captura de video en tiempo real con OpenCV
- ✅ Transmisión WebRTC peer-to-peer
- ✅ Interface web simple y responsive
- ✅ Servidor HTTP integrado
- ✅ Configuración Firebase para señalización

## Requisitos

- Python 3.8+
- Cámara web
- Navegador web moderno

## Instalación

1. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

2. **Configurar Firebase (opcional):**
   - El proyecto incluye configuración de Firebase pero funciona sin ella
   - Asegúrate de que `serviceAccountKey.json` esté en el directorio raíz

## Uso

1. **Iniciar el servidor:**

```bash
python app.py
```

2. **Abrir en el navegador:**
   - Ve a `http://localhost:8080`
   - Haz clic en "Iniciar Stream"
   - Acepta los permisos de cámara si se solicitan

## Estructura del Proyecto

```
├── app.py                 # Servidor WebRTC principal
├── index.html            # Cliente web
├── requirements.txt      # Dependencias Python
├── serviceAccountKey.json # Configuración Firebase
└── README.md            # Este archivo
```

## Cómo Funciona

1. **Captura de Video**: OpenCV captura frames de la cámara web
2. **Procesamiento**: Los frames se convierten al formato correcto para WebRTC
3. **Transmisión**: aiortc maneja la conexión WebRTC peer-to-peer
4. **Visualización**: El navegador web muestra el video en tiempo real

## Tecnologías Utilizadas

- **Backend**: Python, aiortc, aiohttp, OpenCV
- **Frontend**: HTML5, JavaScript, WebRTC API
- **Base de datos**: Firebase Firestore (opcional)

## Solución de Problemas

### Error de cámara

- Verifica que la cámara no esté siendo usada por otra aplicación
- Prueba cambiar el `camera_id` en `OpenCVVideoTrack(camera_id=0)`

### Problemas de conexión

- Asegúrate de que no haya firewall bloqueando el puerto 8080
- Verifica que el navegador soporte WebRTC

### Errores de dependencias

```bash
# En macOS/Linux
pip3 install -r requirements.txt

# Si hay problemas con OpenCV
pip install opencv-python-headless
```

## Notas

- El proyecto está configurado para ser simple y educativo
- Para producción, considera usar HTTPS y servidores TURN
- La configuración actual funciona mejor en redes locales

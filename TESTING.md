# 🧪 Guía de Pruebas - Feature Raspberry Pi

Esta guía te ayuda a probar todas las nuevas características implementadas en la rama `feature/raspberry`.

## 🚀 Pruebas Rápidas

### 1. Información del Sistema
```bash
# Ver qué cámaras detecta el sistema
python app.py --info
```

**Resultado esperado:**
- Detecta la plataforma (computer/raspberry_pi)
- Lista cámaras disponibles
- Muestra configuración recomendada

### 2. Servidor con Auto-detección
```bash
# Iniciar con detección automática
python app.py
```

**Qué hace:**
- Auto-detecta el mejor tipo de cámara
- Configura resolución por defecto (640x480@30fps)
- Muestra información completa al iniciar

### 3. Configuración Personalizada
```bash
# Resolución personalizada
python app.py --width 1280 --height 720 --fps 30

# Puerto personalizado
python app.py --port 8081

# Servidor público (accesible desde red)
python app.py --host 0.0.0.0
```

### 4. Forzar Tipo de Cámara
```bash
# Forzar OpenCV (webcam)
python app.py --camera-type opencv --camera-id 0

# Forzar PiCamera2 (solo en Raspberry Pi)
python app.py --camera-type picamera2
```

## 🔍 Endpoints de Prueba

### `/camera-info` - Información del Sistema
```bash
curl http://localhost:8080/camera-info
```

**Respuesta esperada:**
```json
{
  "platform": "computer",
  "picamera_available": false,
  "recommended_camera": "opencv",
  "available_cameras": ["OpenCV Camera 0", "OpenCV Camera 1"],
  "current_config": {
    "type": "opencv",
    "camera_id": 0,
    "width": 640,
    "height": 480,
    "fps": 30
  }
}
```

### Interface Web Mejorada
- Abre `http://localhost:8080`
- Verifica que muestra información del sistema
- Debajo de las instrucciones debe aparecer:
  - Plataforma detectada
  - Cámara recomendada
  - Resolución actual
  - Cámaras disponibles

## 🍓 Pruebas Específicas de Raspberry Pi

### Setup Automático
```bash
# En Raspberry Pi
python setup_raspberry.py
```

**Qué verifica:**
- Instalación de PiCamera2
- Estado del hardware de cámara
- Permisos del usuario
- Configuración del sistema

### Comandos Raspberry Pi
```bash
# Máxima calidad con PiCamera2
python app.py --camera-type picamera2 --width 1920 --height 1080

# Baja latencia
python app.py --camera-type picamera2 --fps 60 --width 480 --height 360

# Servidor público para acceso remoto
python app.py --camera-type picamera2 --host 0.0.0.0
```

## 🧩 Pruebas del Módulo camera_module.py

### Prueba Independiente
```bash
# Ejecutar solo el módulo
python camera_module.py
```

**Resultado esperado:**
- Información del sistema
- Lista de cámaras detectadas
- Sin errores de importación

### Prueba en Python Interactive
```python
from camera_module import CameraFactory, CameraType, CameraDetector

# Ver información
CameraDetector.detect_platform()
CameraDetector.list_available_cameras()
CameraDetector.get_best_camera_type()

# Crear VideoTrack
track = CameraFactory.create_video_track(
    camera_type=CameraType.AUTO,
    width=640,
    height=480,
    fps=30
)
```

## 📊 Casos de Prueba por Plataforma

### 💻 En Computadora (macOS/Linux/Windows)
- ✅ Auto-detección → OpenCV
- ✅ Lista webcams USB disponibles
- ✅ Fallback si cámara está ocupada
- ✅ Configuración de resolución/FPS

### 🍓 En Raspberry Pi (simulado)
- ✅ Auto-detección → PiCamera2 (si disponible)
- ✅ Fallback a OpenCV si PiCamera2 falla
- ✅ Configuración optimizada para hardware
- ✅ Soporte para cámaras USB adicionales

## 🐛 Escenarios de Error Comunes

### 1. Sin Cámaras Disponibles
```bash
# Simular: desconectar todas las cámaras
python app.py
```
**Resultado:** Debe mostrar mensaje de error elegante

### 2. Puerto Ocupado
```bash
# Dos instancias en mismo puerto
python app.py &
python app.py
```
**Resultado:** Segunda instancia debe fallar con mensaje claro

### 3. Cámara Ocupada
```bash
# Abrir cámara en otra app, luego:
python app.py --camera-id 0
```
**Resultado:** Debe crear frame negro con mensaje de error

### 4. PiCamera2 No Disponible
```bash
# En sistema sin PiCamera2
python app.py --camera-type picamera2
```
**Resultado:** Debe hacer fallback a OpenCV automáticamente

## 📈 Pruebas de Rendimiento

### Diferentes Resoluciones
```bash
# Baja resolución (debería ser fluido)
python app.py --width 320 --height 240 --fps 60

# Resolución media
python app.py --width 640 --height 480 --fps 30

# Alta resolución (puede ser lento)
python app.py --width 1920 --height 1080 --fps 15
```

### Monitoreo de Recursos
```bash
# En otra terminal, mientras el servidor corre
htop  # o top en macOS
```

## ✅ Checklist de Pruebas

- [ ] `python app.py --info` muestra información correcta
- [ ] `python app.py` inicia servidor exitosamente
- [ ] Interface web carga y muestra información del sistema
- [ ] Endpoint `/camera-info` responde JSON válido
- [ ] `python camera_module.py` ejecuta sin errores
- [ ] Argumentos CLI funcionan (`--width`, `--height`, `--fps`, etc.)
- [ ] Fallback funciona si cámara principal falla
- [ ] Servidor se puede detener limpiamente con Ctrl+C
- [ ] Múltiples resoluciones funcionan
- [ ] Cambio de puertos funciona

## 🎯 Siguientes Pasos

Una vez que todas las pruebas pasen:

1. **Merge a main**: Crear PR desde `feature/raspberry`
2. **Documentación**: Actualizar README principal
3. **Release**: Crear tag de versión
4. **Deploy**: Probar en Raspberry Pi real

## 📝 Reporte de Bugs

Si encuentras problemas:

```bash
# Generar log completo
python app.py --info > system_info.txt
python app.py 2>&1 | tee server_log.txt
```

Incluir en el reporte:
- `system_info.txt`
- `server_log.txt`
- Plataforma (OS, versión Python)
- Pasos para reproducir
- Comportamiento esperado vs actual

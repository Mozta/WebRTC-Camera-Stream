"""
Módulo para manejar diferentes tipos de cámaras
Soporta OpenCV (webcam) y PiCamera2 (Raspberry Pi)
"""

import asyncio
import cv2
import numpy as np
import av
from aiortc import VideoStreamTrack
import platform
import sys

# Intentar importar PiCamera2 (solo disponible en Raspberry Pi)
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False

class CameraType:
    """Enum para tipos de cámara"""
    OPENCV = "opencv"
    PICAMERA2 = "picamera2"
    AUTO = "auto"

class CameraDetector:
    """Detecta automáticamente el tipo de cámara disponible"""
    
    @staticmethod
    def detect_platform():
        """Detecta si estamos en Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
                if 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo:
                    return "raspberry_pi"
        except FileNotFoundError:
            pass
        
        # Detectar por arquitectura
        machine = platform.machine().lower()
        if 'arm' in machine or 'aarch64' in machine:
            return "raspberry_pi"
        
        return "computer"
    
    @staticmethod
    def get_best_camera_type():
        """Determina el mejor tipo de cámara para la plataforma actual"""
        platform_type = CameraDetector.detect_platform()
        
        if platform_type == "raspberry_pi" and PICAMERA_AVAILABLE:
            return CameraType.PICAMERA2
        else:
            return CameraType.OPENCV
    
    @staticmethod
    def list_available_cameras():
        """Lista las cámaras disponibles"""
        cameras = []
        
        # Verificar OpenCV
        for i in range(5):  # Probar los primeros 5 índices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(f"OpenCV Camera {i}")
                cap.release()
        
        # Verificar PiCamera2
        if PICAMERA_AVAILABLE:
            try:
                picam = Picamera2()
                cameras.append("PiCamera2")
                picam.close()
            except Exception:
                pass
        
        return cameras

class OpenCVVideoTrack(VideoStreamTrack):
    """VideoStreamTrack que usa OpenCV para capturar video"""
    
    def __init__(self, camera_id=0, width=640, height=480, fps=30):
        super().__init__()
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.fps = fps
        
        # Configurar cámara OpenCV
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        
        print(f"📹 OpenCV Camera {camera_id} inicializada: {width}x{height}@{fps}fps")
        
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        ret, frame = self.cap.read()
        if not ret:
            # Si no hay frame, crear uno negro con texto
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(frame, "No Camera Signal", (50, self.height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Convertir BGR a RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.asarray(frame, dtype=np.uint8)
        
        # Crear frame de PyAV
        av_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        av_frame.pts = pts
        av_frame.time_base = time_base
        
        return av_frame
    
    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

class PiCamera2VideoTrack(VideoStreamTrack):
    """VideoStreamTrack que usa PiCamera2 para Raspberry Pi"""
    
    def __init__(self, width=640, height=480, fps=30):
        super().__init__()
        
        if not PICAMERA_AVAILABLE:
            raise ImportError("PiCamera2 no está disponible. Instala con: pip install picamera2")
        
        self.width = width
        self.height = height
        self.fps = fps
        
        # Configurar PiCamera2
        self.picam = Picamera2()
        
        # Configuración de video
        video_config = self.picam.create_video_configuration(
            main={"size": (width, height), "format": "RGB888"},
            controls={"FrameRate": fps}
        )
        
        self.picam.configure(video_config)
        self.picam.start()
        
        print(f"📹 PiCamera2 inicializada: {width}x{height}@{fps}fps")
    
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        try:
            # Capturar frame de PiCamera2
            frame = self.picam.capture_array()
            
            # Asegurar que el frame sea RGB y del tipo correcto
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame = np.asarray(frame, dtype=np.uint8)
            else:
                # Crear frame negro si hay problemas
                frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                cv2.putText(frame, "PiCamera Error", (50, self.height//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
        except Exception as e:
            print(f"❌ Error capturando de PiCamera2: {e}")
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(frame, "Camera Error", (50, self.height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # Crear frame de PyAV
        av_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        av_frame.pts = pts
        av_frame.time_base = time_base
        
        return av_frame
    
    def __del__(self):
        if hasattr(self, 'picam'):
            try:
                self.picam.stop()
                self.picam.close()
            except Exception:
                pass

class CameraFactory:
    """Factory para crear VideoTracks según el tipo de cámara"""
    
    @staticmethod
    def create_video_track(camera_type=CameraType.AUTO, camera_id=0, width=640, height=480, fps=30):
        """
        Crea un VideoTrack según el tipo especificado
        
        Args:
            camera_type: Tipo de cámara (AUTO, OPENCV, PICAMERA2)
            camera_id: ID de la cámara (solo para OpenCV)
            width: Ancho del video
            height: Alto del video
            fps: Frames por segundo
        
        Returns:
            VideoStreamTrack configurado
        """
        
        # Auto-detectar si es necesario
        if camera_type == CameraType.AUTO:
            camera_type = CameraDetector.get_best_camera_type()
            print(f"🔍 Auto-detectado: {camera_type}")
        
        # Crear el track apropiado
        if camera_type == CameraType.PICAMERA2:
            if not PICAMERA_AVAILABLE:
                print("⚠️  PiCamera2 no disponible, usando OpenCV")
                return OpenCVVideoTrack(camera_id, width, height, fps)
            return PiCamera2VideoTrack(width, height, fps)
        
        elif camera_type == CameraType.OPENCV:
            return OpenCVVideoTrack(camera_id, width, height, fps)
        
        else:
            raise ValueError(f"Tipo de cámara no soportado: {camera_type}")

def print_camera_info():
    """Imprime información sobre las cámaras disponibles"""
    print("🔍 Información del sistema:")
    print(f"  - Plataforma: {CameraDetector.detect_platform()}")
    print(f"  - PiCamera2 disponible: {PICAMERA_AVAILABLE}")
    print(f"  - Cámara recomendada: {CameraDetector.get_best_camera_type()}")
    
    print("\n📹 Cámaras disponibles:")
    cameras = CameraDetector.list_available_cameras()
    if cameras:
        for camera in cameras:
            print(f"  - {camera}")
    else:
        print("  - No se detectaron cámaras")

if __name__ == "__main__":
    # Prueba del módulo
    print_camera_info()

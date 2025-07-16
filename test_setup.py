#!/usr/bin/env python3
"""
Script de prueba para verificar que las dependencias funcionan correctamente
"""

def test_imports():
    """Prueba que todas las importaciones funcionen"""
    try:
        import cv2
        print("✅ OpenCV importado correctamente")
        
        import aiortc
        print("✅ aiortc importado correctamente")
        
        import av
        print("✅ PyAV importado correctamente")
        
        import aiohttp
        print("✅ aiohttp importado correctamente")
        
        import firebase_admin
        print("✅ firebase-admin importado correctamente")
        
        import numpy as np
        print("✅ numpy importado correctamente")
        
        return True
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_opencv_camera():
    """Prueba que OpenCV pueda acceder a la cámara"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("⚠️  No se pudo abrir la cámara (esto es normal si no hay cámara conectada)")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            print(f"✅ Cámara funciona correctamente - Frame: {frame.shape}")
            return True
        else:
            print("⚠️  No se pudo capturar frame de la cámara")
            return False
            
    except Exception as e:
        print(f"❌ Error con la cámara: {e}")
        return False

def test_webrtc_classes():
    """Prueba que las clases de WebRTC se puedan instanciar"""
    try:
        from aiortc import RTCPeerConnection
        pc = RTCPeerConnection()
        print("✅ RTCPeerConnection creado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando RTCPeerConnection: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Ejecutando pruebas del proyecto WebRTC...\n")
    
    print("1. Probando importaciones:")
    imports_ok = test_imports()
    
    print("\n2. Probando acceso a cámara:")
    camera_ok = test_opencv_camera()
    
    print("\n3. Probando clases WebRTC:")
    webrtc_ok = test_webrtc_classes()
    
    print("\n" + "="*50)
    if imports_ok and webrtc_ok:
        print("🎉 ¡Todas las pruebas básicas pasaron!")
        print("✅ El proyecto está listo para funcionar")
        if camera_ok:
            print("📹 Cámara detectada y funcionando")
        else:
            print("⚠️  Cámara no detectada (pero el proyecto debería funcionar)")
    else:
        print("❌ Algunas pruebas fallaron. Revisa las dependencias.")

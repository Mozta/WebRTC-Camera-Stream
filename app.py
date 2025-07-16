import asyncio
import json
import cv2
import firebase_admin
from firebase_admin import credentials, firestore
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
    VideoStreamTrack,
)
from aiortc.contrib.media import MediaPlayer
from aiohttp import web, web_ws
import aiohttp_cors
import av
import numpy as np
import threading
import time

# Configuración de Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Clase para capturar video de la cámara usando OpenCV
class OpenCVVideoTrack(VideoStreamTrack):
    """
    VideoStreamTrack que captura video de la cámara usando OpenCV
    """
    
    def __init__(self, camera_id=0):
        super().__init__()
        self.cap = cv2.VideoCapture(camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
    async def recv(self):
        pts, time_base = await self.next_timestamp()
        
        ret, frame = self.cap.read()
        if not ret:
            # Si no hay frame, crear uno negro
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Convertir BGR a RGB (OpenCV usa BGR por defecto)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Asegurar que el frame sea del tipo correcto
        frame = np.asarray(frame, dtype=np.uint8)
        
        # Crear frame de PyAV
        av_frame = av.VideoFrame.from_ndarray(frame, format="rgb24")
        av_frame.pts = pts
        av_frame.time_base = time_base
        
        return av_frame
    
    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

# Almacenar conexiones WebRTC activas
pcs = set()

async def index(request):
    """Página principal con el cliente WebRTC"""
    content = open('index.html', 'r').read()
    return web.Response(content_type='text/html', text=content)

async def offer(request):
    """Endpoint para manejar ofertas WebRTC"""
    params = await request.json()
    offer_data = params["offer"]
    
    # Crear nueva conexión peer
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    # Añadir track de video de la cámara
    video_track = OpenCVVideoTrack()
    pc.addTrack(video_track)
    
    # Manejar cierre de conexión
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
    
    # Configurar la oferta recibida
    await pc.setRemoteDescription(RTCSessionDescription(
        sdp=offer_data["sdp"], 
        type=offer_data["type"]
    ))
    
    # Crear respuesta
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "answer": {
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            }
        })
    )

async def cleanup_connections():
    """Limpiar conexiones al cerrar"""
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

async def init_app():
    """Inicializar la aplicación web"""
    app = web.Application()
    
    # Configurar CORS
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*"
        )
    })
    
    # Rutas
    app.router.add_get("/", index)
    app.router.add_post("/offer", offer)
    app.router.add_static('/', path='.', name='static')
    
    # Añadir CORS a todas las rutas
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

async def main():
    """Función principal"""
    app = await init_app()
    runner = None
    
    # Manejar cierre limpio
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8080)
        print("🚀 Servidor iniciado en http://localhost:8080")
        print("📹 Presiona Ctrl+C para detener")
        await site.start()
        
        # Mantener el servidor corriendo
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Cerrando servidor...")
        await cleanup_connections()
        if runner:
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

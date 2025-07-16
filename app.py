import asyncio
import json
import argparse
import firebase_admin
from firebase_admin import credentials, firestore
from aiortc import (
    RTCPeerConnection,
    RTCSessionDescription,
    RTCIceCandidate,
)
from aiohttp import web
import aiohttp_cors

# Importar nuestro módulo de cámaras
from camera_module import CameraFactory, CameraType, print_camera_info

# Configuración de Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Almacenar conexiones WebRTC activas
pcs = set()

# Configuración global de cámara
camera_config = {
    "type": CameraType.AUTO,
    "camera_id": 0,
    "width": 640,
    "height": 480,
    "fps": 30
}

async def index(request):
    """Página principal con el cliente WebRTC"""
    content = open('index.html', 'r').read()
    return web.Response(content_type='text/html', text=content)

async def camera_info(request):
    """Endpoint para obtener información de las cámaras"""
    from camera_module import CameraDetector, PICAMERA_AVAILABLE
    
    info = {
        "platform": CameraDetector.detect_platform(),
        "picamera_available": PICAMERA_AVAILABLE,
        "recommended_camera": CameraDetector.get_best_camera_type(),
        "available_cameras": CameraDetector.list_available_cameras(),
        "current_config": camera_config
    }
    
    return web.Response(
        content_type="application/json",
        text=json.dumps(info, indent=2)
    )

async def offer(request):
    """Endpoint para manejar ofertas WebRTC"""
    params = await request.json()
    offer_data = params["offer"]
    
    # Crear nueva conexión peer
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    # Crear track de video usando el factory
    try:
        video_track = CameraFactory.create_video_track(
            camera_type=camera_config["type"],
            camera_id=camera_config["camera_id"],
            width=camera_config["width"],
            height=camera_config["height"],
            fps=camera_config["fps"]
        )
        pc.addTrack(video_track)
        print(f"✅ Video track añadido: {camera_config['type']}")
    except Exception as e:
        print(f"❌ Error creando video track: {e}")
        # Intentar con OpenCV como fallback
        try:
            video_track = CameraFactory.create_video_track(
                camera_type=CameraType.OPENCV,
                camera_id=0,
                width=640,
                height=480,
                fps=30
            )
            pc.addTrack(video_track)
            print("⚠️  Usando OpenCV como fallback")
        except Exception as e2:
            print(f"❌ Error con fallback: {e2}")
            return web.Response(
                content_type="application/json",
                text=json.dumps({"error": "No se pudo inicializar la cámara"}),
                status=500
            )
    
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
    app.router.add_get("/camera-info", camera_info)
    app.router.add_static('/', path='.', name='static')
    
    # Añadir CORS a todas las rutas
    for route in list(app.router.routes()):
        cors.add(route)
    
    return app

def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='Servidor WebRTC con soporte para múltiples cámaras')
    
    parser.add_argument('--camera-type', 
                       choices=['auto', 'opencv', 'picamera2'], 
                       default='auto',
                       help='Tipo de cámara a usar (default: auto)')
    
    parser.add_argument('--camera-id', 
                       type=int, 
                       default=0,
                       help='ID de la cámara OpenCV (default: 0)')
    
    parser.add_argument('--width', 
                       type=int, 
                       default=640,
                       help='Ancho del video (default: 640)')
    
    parser.add_argument('--height', 
                       type=int, 
                       default=480,
                       help='Alto del video (default: 480)')
    
    parser.add_argument('--fps', 
                       type=int, 
                       default=30,
                       help='Frames por segundo (default: 30)')
    
    parser.add_argument('--port', 
                       type=int, 
                       default=8080,
                       help='Puerto del servidor (default: 8080)')
    
    parser.add_argument('--host', 
                       default='localhost',
                       help='Host del servidor (default: localhost)')
    
    parser.add_argument('--info', 
                       action='store_true',
                       help='Mostrar información de cámaras y salir')
    
    return parser.parse_args()

async def main():
    """Función principal"""
    global camera_config
    
    args = parse_arguments()
    
    # Mostrar información si se solicita
    if args.info:
        print_camera_info()
        return
    
    # Configurar cámara según argumentos
    camera_config.update({
        "type": getattr(CameraType, args.camera_type.upper()),
        "camera_id": args.camera_id,
        "width": args.width,
        "height": args.height,
        "fps": args.fps
    })
    
    print("🚀 Iniciando servidor WebRTC...")
    print_camera_info()
    print(f"\n⚙️  Configuración:")
    print(f"  - Tipo de cámara: {args.camera_type}")
    print(f"  - Resolución: {args.width}x{args.height}")
    print(f"  - FPS: {args.fps}")
    print(f"  - Servidor: http://{args.host}:{args.port}")
    
    app = await init_app()
    runner = None
    
    # Manejar cierre limpio
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, args.host, args.port)
        print(f"\n✅ Servidor iniciado en http://{args.host}:{args.port}")
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

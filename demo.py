#!/usr/bin/env python3
"""
🎬 Demo Script - WebRTC Camera Stream (Raspberry Pi Edition)

Script de demostración que muestra todas las características implementadas
en la rama feature/raspberry.
"""

import asyncio
import subprocess
import sys
import time
import json
from pathlib import Path

def print_header(title):
    """Imprimir encabezado con estilo"""
    print("\n" + "="*60)
    print(f"🎬 {title}")
    print("="*60)

def print_step(step, description):
    """Imprimir paso de la demostración"""
    print(f"\n📋 Paso {step}: {description}")
    print("-" * 40)

def run_command(cmd, description=""):
    """Ejecutar comando y mostrar resultado"""
    if description:
        print(f"💻 {description}")
    print(f"$ {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"⚠️  {result.stderr}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Comando tomó demasiado tiempo (timeout)")
        return False
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def demo_system_info():
    """Demostración de información del sistema"""
    print_header("INFORMACIÓN DEL SISTEMA")
    
    print_step(1, "Detectar plataforma y cámaras disponibles")
    run_command("python camera_module.py", "Ejecutando módulo de cámaras independiente")
    
    print_step(2, "Información completa del servidor")
    run_command("python app.py --info", "Información desde el servidor principal")

def demo_module_features():
    """Demostración de características del módulo"""
    print_header("CARACTERÍSTICAS DEL MÓDULO")
    
    print_step(1, "Importar y probar clases principales")
    
    test_script = '''
from camera_module import CameraDetector, CameraFactory, CameraType

print("🔍 Detección de plataforma:")
print(f"  Plataforma: {CameraDetector.detect_platform()}")
print(f"  Cámara recomendada: {CameraDetector.get_best_camera_type()}")

print("\\n📹 Cámaras disponibles:")
cameras = CameraDetector.list_available_cameras()
for i, camera in enumerate(cameras, 1):
    print(f"  {i}. {camera}")

print("\\n🏭 Factory de VideoTracks:")
try:
    track = CameraFactory.create_video_track(CameraType.AUTO, width=320, height=240)
    print(f"  ✅ VideoTrack creado: {type(track).__name__}")
except Exception as e:
    print(f"  ❌ Error: {e}")
    '''
    
    with open("temp_test.py", "w") as f:
        f.write(test_script)
    
    run_command("python temp_test.py", "Probando clases del módulo")
    
    # Limpiar archivo temporal
    Path("temp_test.py").unlink(missing_ok=True)

def demo_cli_arguments():
    """Demostración de argumentos CLI"""
    print_header("ARGUMENTOS DE LÍNEA DE COMANDOS")
    
    # Lista de demostraciones de argumentos
    cli_demos = [
        ("--help", "Mostrar ayuda completa"),
        ("--info", "Información del sistema"),
        ("--camera-type opencv --width 320 --height 240 --fps 15", "Configuración personalizada"),
    ]
    
    for i, (args, desc) in enumerate(cli_demos, 1):
        print_step(i, desc)
        run_command(f"python app.py {args}", f"Probando: {args}")

def demo_api_endpoints():
    """Demostración de endpoints de API"""
    print_header("ENDPOINTS DE API")
    
    print("🚀 Para esta demo, necesitamos iniciar el servidor...")
    print("💡 En otra terminal, ejecuta: python app.py --port 8082")
    print("⏳ Esperando 5 segundos para que inicies el servidor...")
    
    for i in range(5, 0, -1):
        print(f"⏰ {i}...", end=" ", flush=True)
        time.sleep(1)
    print("\n")
    
    print_step(1, "Probar endpoint de información")
    
    # Verificar si el servidor está corriendo
    import urllib.request
    import urllib.error
    
    try:
        with urllib.request.urlopen("http://localhost:8082/camera-info", timeout=5) as response:
            data = json.loads(response.read().decode())
            print("✅ Endpoint /camera-info responde:")
            print(json.dumps(data, indent=2))
    except urllib.error.URLError:
        print("❌ Servidor no está corriendo en puerto 8082")
        print("💡 Inicia con: python app.py --port 8082")
    except Exception as e:
        print(f"❌ Error conectando: {e}")

def demo_file_structure():
    """Mostrar estructura de archivos creados"""
    print_header("ESTRUCTURA DE ARCHIVOS")
    
    files_info = [
        ("camera_module.py", "Módulo principal con clases de cámara"),
        ("app.py", "Servidor WebRTC mejorado"),
        ("index.html", "Interface web actualizada"),
        ("setup_raspberry.py", "Script de configuración para Raspberry Pi"),
        ("requirements-raspberry.txt", "Dependencias específicas para RPi"),
        ("README-raspberry.md", "Documentación completa"),
        ("TESTING.md", "Guía de pruebas")
    ]
    
    print("📁 Archivos creados/modificados:")
    for filename, description in files_info:
        if Path(filename).exists():
            size = Path(filename).stat().st_size
            print(f"  ✅ {filename:<25} ({size:,} bytes) - {description}")
        else:
            print(f"  ❌ {filename:<25} (no encontrado) - {description}")

def demo_comparison():
    """Comparar versión original vs nueva"""
    print_header("COMPARACIÓN: ANTES vs AHORA")
    
    print("📊 Funcionalidades añadidas:")
    
    features = [
        "✅ Auto-detección de plataforma (Raspberry Pi vs Computer)",
        "✅ Soporte modular para múltiples tipos de cámara",
        "✅ PiCamera2 para Raspberry Pi Camera Module",
        "✅ Argumentos CLI para configuración completa",
        "✅ Endpoint de información del sistema (/camera-info)",
        "✅ Fallback automático entre tipos de cámara",
        "✅ Configuración dinámica de resolución y FPS",
        "✅ Script de setup automático para Raspberry Pi",
        "✅ Requirements separados por plataforma",
        "✅ Interface web con información del sistema",
        "✅ Manejo robusto de errores",
        "✅ Documentación completa y guías de prueba"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n📈 Estadísticas:")
    print(f"  • Archivos añadidos: 5 nuevos")
    print(f"  • Archivos modificados: 2 existentes") 
    print(f"  • Líneas de código: ~800+ nuevas")
    print(f"  • Comandos CLI: 8+ opciones")
    print(f"  • Tipos de cámara soportados: 2 (OpenCV + PiCamera2)")

def main():
    """Función principal de la demostración"""
    print("🎬 DEMO: WebRTC Camera Stream - Raspberry Pi Edition")
    print("🍓 Mostrando todas las nuevas características implementadas")
    print("⏰ Duración estimada: 3-5 minutos")
    
    input("\n👆 Presiona Enter para comenzar...")
    
    # Ejecutar demostraciones
    demo_system_info()
    input("\n👆 Presiona Enter para continuar...")
    
    demo_module_features()
    input("\n👆 Presiona Enter para continuar...")
    
    demo_cli_arguments()
    input("\n👆 Presiona Enter para continuar...")
    
    demo_file_structure()
    input("\n👆 Presiona Enter para continuar...")
    
    demo_comparison()
    input("\n👆 Presiona Enter para continuar...")
    
    demo_api_endpoints()
    
    # Conclusión
    print_header("DEMO COMPLETADA")
    print("🎉 ¡Felicitaciones! Has visto todas las nuevas características.")
    print("\n📋 Próximos pasos sugeridos:")
    print("  1. Probar en Raspberry Pi real con: python setup_raspberry.py")
    print("  2. Ejecutar pruebas completas con: python -m pytest (si tienes tests)")
    print("  3. Crear Pull Request para merge a main")
    print("  4. Actualizar documentación principal")
    
    print("\n💡 Comandos útiles para recordar:")
    print("  • python app.py --info           (información del sistema)")
    print("  • python app.py --camera-type picamera2  (forzar PiCamera2)")
    print("  • python app.py --width 1280 --height 720  (resolución HD)")
    print("  • python setup_raspberry.py     (setup para Raspberry Pi)")
    
    print("\n🔗 Enlaces importantes:")
    print("  • Documentación: README-raspberry.md")
    print("  • Guía de pruebas: TESTING.md")
    print("  • Repositorio: https://github.com/Mozta/WebRTC-Camera-Stream")
    
    print("\n✨ ¡Gracias por usar WebRTC Camera Stream!")

if __name__ == "__main__":
    main()

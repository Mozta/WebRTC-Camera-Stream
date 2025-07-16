#!/usr/bin/env python3
"""
Script optimizado para Raspberry Pi con PiCamera2
"""

import sys
import subprocess
import pkg_resources

def check_dependencies():
    """Verificar e instalar dependencias necesarias"""
    required_packages = [
        'picamera2',
        'libcamera',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print(f"✅ {package} está instalado")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
            print(f"❌ {package} no está instalado")
    
    if missing_packages:
        print(f"\n📦 Instalando paquetes faltantes: {', '.join(missing_packages)}")
        
        for package in missing_packages:
            if package == 'picamera2':
                # PiCamera2 requiere instalación especial en Raspberry Pi
                try:
                    subprocess.check_call([
                        sys.executable, '-m', 'pip', 'install', 
                        'picamera2', '--break-system-packages'
                    ])
                    print(f"✅ {package} instalado correctamente")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Error instalando {package}: {e}")
                    print("💡 Intenta: sudo apt update && sudo apt install -y python3-picamera2")
                    return False
    
    return True

def setup_raspberry_pi():
    """Configuración específica para Raspberry Pi"""
    print("🔧 Configurando Raspberry Pi...")
    
    # Verificar que estamos en Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'BCM' not in cpuinfo and 'Raspberry Pi' not in cpuinfo:
                print("⚠️  Este script está optimizado para Raspberry Pi")
                return True  # Continuar de todas formas
    except FileNotFoundError:
        print("⚠️  No se pudo verificar si es Raspberry Pi")
        return True
    
    # Verificar que la cámara esté habilitada
    try:
        import subprocess
        result = subprocess.run(['vcgencmd', 'get_camera'], 
                              capture_output=True, text=True)
        if 'detected=1' not in result.stdout:
            print("❌ Cámara no detectada")
            print("💡 Habilita la cámara con: sudo raspi-config")
            print("   Interfacing Options -> Camera -> Enable")
            return False
    except FileNotFoundError:
        print("⚠️  No se pudo verificar el estado de la cámara")
    
    print("✅ Raspberry Pi configurado correctamente")
    return True

def main():
    """Función principal para setup de Raspberry Pi"""
    print("🍓 Setup para Raspberry Pi - WebRTC Camera Stream")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Error en las dependencias. Abortando.")
        sys.exit(1)
    
    # Configurar Raspberry Pi
    if not setup_raspberry_pi():
        print("❌ Error en la configuración. Abortando.")
        sys.exit(1)
    
    print("\n🎉 ¡Setup completado!")
    print("\n📋 Comandos útiles:")
    print("  - Iniciar con PiCamera2: python app.py --camera-type picamera2")
    print("  - Información de cámaras: python app.py --info")
    print("  - Resolución HD: python app.py --width 1280 --height 720")
    print("  - Servidor público: python app.py --host 0.0.0.0")
    
    # Probar el módulo de cámara
    print("\n🧪 Probando módulo de cámara...")
    try:
        from camera_module import print_camera_info
        print_camera_info()
    except Exception as e:
        print(f"❌ Error probando cámara: {e}")

if __name__ == "__main__":
    main()

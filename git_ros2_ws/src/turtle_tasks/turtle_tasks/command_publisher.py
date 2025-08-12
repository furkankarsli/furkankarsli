# command_publisher.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import tty
import termios
import os
from datetime import datetime

def write_to_log(message: str):
    """Log mesajını dosyaya yazar"""
    try:
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        log_file = os.path.join(log_dir, "command_publisher.log")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"Log yazma hatası: {e}")

def publish_and_log(publisher, command):
    """Komutu yayınla ve logla - DRY prensibi"""
    msg = String()
    msg.data = command
    publisher.publish(msg)
    log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Komut gönderildi: {msg.data}"
    write_to_log(log_msg)
    print(f"'{msg.data}' komutu gönderildi.")

# Kullanıcıya menü ve talimatları göstermek için
def print_menu():
    print("\n--- Komut Menüsü ---")
    print("1: Task1 -> A'ya git, 2 saniye bekle")
    print("2: Task2 -> A'ya git, B'ye git, 2'şer saniye bekle")
    print("3: Task3 -> A'ya git, B'ye git, C'ye git, 2'şer saniye bekle")
    print("i: Idle konumuna git")
    print("s: Robotu durdur -> stop")
    print("q: Çıkış")
    print("--------------------")
    print("Seçiminiz: ", end="", flush=True)

# Tek tuşla input almak için
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main(args=None):
    rclpy.init(args=args)
    node = Node('command_publisher')
    
    # Behavior tree ile uyumlu topic
    robot_cmd_pub = node.create_publisher(String, '/robot_command', 10)
    
    # Komutları bir sözlükte topluyoruz - DRY prensibi
    commands = {
        '1': 'task1',
        '2': 'task2',
        '3': 'task3',
        'i': 'idle',
        's': 'stop',
    }
    
    print_menu()
    
    while rclpy.ok():
        key = getch().lower()  # Gelen tuşu küçültelim
        
        if key in commands:
            publish_and_log(robot_cmd_pub, commands[key])
        elif key == 'q':
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Program kapatılıyor"
            write_to_log(log_msg)
            print("Çıkılıyor...")
            break
        else:
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Geçersiz tuş: {key}"
            write_to_log(log_msg)
            print("Geçersiz tuş.")
        
        print_menu()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
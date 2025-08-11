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
    
    print_menu()
    
    while rclpy.ok():
        key = getch()
        msg = String()
        
        if key == '1':
            msg.data = 'task1'
            robot_cmd_pub.publish(msg)
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Komut gönderildi: {msg.data}"
            write_to_log(log_msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key == '2':
            msg.data = 'task2'
            robot_cmd_pub.publish(msg)
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Komut gönderildi: {msg.data}"
            write_to_log(log_msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key == '3':
            msg.data = 'task3'
            robot_cmd_pub.publish(msg)
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Komut gönderildi: {msg.data}"
            write_to_log(log_msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key == 'i':
            msg.data = 'idle'
            robot_cmd_pub.publish(msg)
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Komut gönderildi: {msg.data}"
            write_to_log(log_msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key.lower() == 's':
            msg.data = 'stop'
            robot_cmd_pub.publish(msg)
            log_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Komut gönderildi: {msg.data}"
            write_to_log(log_msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key.lower() == 'q':
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
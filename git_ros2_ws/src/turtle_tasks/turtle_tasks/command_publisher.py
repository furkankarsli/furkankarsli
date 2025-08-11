# command_publisher.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import sys
import tty
import termios

# Kullanıcıya menü ve talimatları göstermek için
def print_menu():
    print("\n--- Komut Menüsü ---")
    print("1: task_1'e git -> task_1")
    print("2: sarj'a git -> sarj")
    print("i: idle noktasına git -> idle")
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
            msg.data = 'task_1'
            robot_cmd_pub.publish(msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key == '2':
            msg.data = 'sarj'
            robot_cmd_pub.publish(msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key == 'i':
            msg.data = 'idle'
            robot_cmd_pub.publish(msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key.lower() == 's':
            msg.data = 'stop'
            robot_cmd_pub.publish(msg)
            print(f"'{msg.data}' komutu gönderildi.")
        elif key.lower() == 'q':
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz tuş.")
        
        print_menu()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
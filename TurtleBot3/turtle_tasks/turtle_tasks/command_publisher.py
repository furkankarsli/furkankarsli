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
    print("1: Masayı seç -> table_1")
    print("2: Masayı seç -> table_2")
    print("c: Siparişi onayla -> confirm")
    print("s: Robotu durdur -> stop")
    print("k: Mutfağa git -> go_kitchen")
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
    
    table_pub = node.create_publisher(String, '/table_selection', 10)
    order_pub = node.create_publisher(String, '/order_confirmation', 10)
    web_cmd_pub = node.create_publisher(String, '/web_commands', 10)
    
    print_menu()
    
    while rclpy.ok():
        key = getch()
        msg = String()
        
        if key == '1':
            msg.data = 'table_1'
            table_pub.publish(msg)
            print(f"'{msg.data}' gönderildi.")
        elif key == '2':
            msg.data = 'table_2'
            table_pub.publish(msg)
            print(f"'{msg.data}' gönderildi.")
        elif key.lower() == 'c':
            msg.data = 'confirm'
            order_pub.publish(msg)
            print(f"Sipariş onayı '{msg.data}' gönderildi.")
        elif key.lower() == 's':
            msg.data = 'stop'
            web_cmd_pub.publish(msg)
            print(f"Web komutu '{msg.data}' gönderildi.")
        elif key.lower() == 'k':
            msg.data = 'go_kitchen'
            web_cmd_pub.publish(msg)
            print(f"Web komutu '{msg.data}' gönderildi.")
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
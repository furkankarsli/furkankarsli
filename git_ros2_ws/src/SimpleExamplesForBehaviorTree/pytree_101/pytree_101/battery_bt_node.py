#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import py_trees
import sys
import time
import select
import termios
import tty
import threading

CRITICAL_BATTERY = 25

# Batarya dinleyici node (thread ile)
class BatteryListener(Node):
    def __init__(self, blackboard):
        super().__init__('battery_listener')
        self.subscription = self.create_subscription(
            Int32,
            'battery_level',
            self.listener_callback,
            10
        )
        self.blackboard = blackboard
        self._stop_event = threading.Event()
    def listener_callback(self, msg):
        self.blackboard.battery_level = msg.data
    def run(self):
        while rclpy.ok() and not self._stop_event.is_set():
            rclpy.spin_once(self, timeout_sec=0.1)
    def stop(self):
        self._stop_event.set()

def get_input_with_timeout(prompt, timeout=2.0):
    print(prompt, end='', flush=True)
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                return None
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                return sys.stdin.readline().strip().lower()
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# Ortak batarya kontrol davranışı
class CheckBattery(py_trees.behaviour.Behaviour):
    def __init__(self, name="BataryaKontrol"):
        super().__init__(name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("battery_level", access=py_trees.common.Access.READ)
        self.blackboard.register_key("shutdown", access=py_trees.common.Access.WRITE)
    def update(self):
        if getattr(self.blackboard, "battery_level", 100) < CRITICAL_BATTERY:
            print(f"\n⚠️  Kritik: Pil seviyesi ({self.blackboard.battery_level}%) {CRITICAL_BATTERY}% altına düştü! Program sonlandırılıyor.")
            self.blackboard.shutdown = True
            return py_trees.common.Status.FAILURE
        return py_trees.common.Status.SUCCESS

# Durum davranışları
class StateBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, state_name, prompt, transitions):
        super().__init__(state_name)
        self.state_name = state_name
        self.prompt = prompt
        self.transitions = transitions  # dict: komut -> yeni durum
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("next_state", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("shutdown", access=py_trees.common.Access.READ)
    def update(self):
        if getattr(self.blackboard, "shutdown", False):
            return py_trees.common.Status.FAILURE
        cmd = get_input_with_timeout(f"{self.state_name}: {self.prompt}\nKomut girin: ")
        if cmd == 's':
            self.blackboard.shutdown = True
            return py_trees.common.Status.FAILURE
        if cmd in self.transitions:
            self.blackboard.next_state = self.transitions[cmd]
            return py_trees.common.Status.SUCCESS
        print("Geçersiz komut!")
        return py_trees.common.Status.FAILURE

def create_tree():
    # Durumlar ve geçişler
    states = {
        "UYAN": StateBehaviour("UYAN", "Uyandınız.", {'k': 'KALK', 'y': 'GERI_YAT', 'i': 'IDLE'}),
        "KALK": StateBehaviour("KALK", "Kalktınız.", {'y': 'GERI_YAT', 'i': 'IDLE'}),
        "GERI_YAT": StateBehaviour("GERI_YAT", "Geri yattınız.", {'k': 'KALK', 'i': 'IDLE'}),
        "IDLE": StateBehaviour("IDLE", "Boşta bekliyorsunuz.", {'k': 'KALK', 'y': 'GERI_YAT'})
    }
    return states

def main():
    rclpy.init()
    blackboard = py_trees.blackboard.Client(name="MainClient")
    blackboard.register_key("battery_level", access=py_trees.common.Access.WRITE)
    blackboard.register_key("shutdown", access=py_trees.common.Access.WRITE)
    blackboard.register_key("next_state", access=py_trees.common.Access.WRITE)
    blackboard.battery_level = 100
    blackboard.shutdown = False
    blackboard.next_state = "UYAN"
    node = BatteryListener(blackboard)
    battery_thread = threading.Thread(target=node.run, daemon=True)
    battery_thread.start()
    states = create_tree()
    battery_check = CheckBattery()
    print("\n--- Durum Makinesi Başladı ---\nKomutlar: k=kalk, y=geri yat, i=idle, s=son")
    try:
        while rclpy.ok() and not blackboard.shutdown:
            if battery_check.tick() == py_trees.common.Status.FAILURE:
                break
            state = blackboard.next_state
            if state not in states:
                print("Bilinmeyen durum! Çıkılıyor.")
                break
            if states[state].tick() == py_trees.common.Status.SUCCESS:
                continue
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor...")
    print("\nProgram kapandı.")
    node.stop()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
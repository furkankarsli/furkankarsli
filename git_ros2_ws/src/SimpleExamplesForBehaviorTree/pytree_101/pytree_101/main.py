#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import py_trees
import threading
import time
import sys
import select
import termios
import tty
from tree_builder import create_behavior_tree

class TimerThread(threading.Thread):
    def __init__(self, timeout, blackboard):
        super().__init__()
        self.timeout = timeout
        self.blackboard = blackboard
        self._stop_event = threading.Event()
        self.start_time = time.time()

    def run(self):
        while not self._stop_event.is_set() and (time.time() - self.start_time < self.timeout):
            self.blackboard.set("remaining_time", max(0, self.timeout - (time.time() - self.start_time)))
            self.blackboard.set("timeout", (time.time() - self.start_time) >= self.timeout)
            time.sleep(0.1)
        self.blackboard.set("timeout", True)

    def stop(self):
        self._stop_event.set()

def get_input_with_timeout(prompt, timeout):
    """Zaman aşımı ile kullanıcı girişi alır."""
    print(prompt, end='', flush=True)
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            return sys.stdin.readline().strip().lower()
        return None
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

class PytreesNode(Node):
    def __init__(self):
        super().__init__('pytrees_node')
        self.declare_parameter("interactive", sys.stdin.isatty())
        self.tree = py_trees.trees.BehaviourTree(create_behavior_tree(self))
        self.tree.setup()
        py_trees.display.render_dot_tree(self.tree.root)
        self.running = True
        self.blackboard = py_trees.blackboard.Blackboard()
        self.blackboard.set("end_program", False)
        self.blackboard.set("timeout", False)
        self.blackboard.set("remaining_time", 10.0)

    def spin(self):
        end_program = self.blackboard.get("end_program") if self.blackboard.exists("end_program") else False
        timeout = self.blackboard.get("timeout") if self.blackboard.exists("timeout") else False
        while rclpy.ok() and self.running and not end_program and not timeout:
            self.tree.tick()
            time.sleep(0.1)
            end_program = self.blackboard.get("end_program") if self.blackboard.exists("end_program") else False
            timeout = self.blackboard.get("timeout") if self.blackboard.exists("timeout") else False
        self.get_logger().info("Sistem kapatılıyor...")
        self.tree.shutdown()
        self.destroy_node()
        rclpy.shutdown()

def print_final_state(blackboard):
    try:
        print("\nSon durum:")
        keys_to_print = ["uyan_secenek", "kahvalti_secenek", "calis_secenek", "spor_secenek", "dinlen_secenek", "idle_secenek"]
        for key in keys_to_print:
            value = blackboard.get(key) if blackboard.exists(key) else "N/A"
            print(f"{key.replace('_secenek', '').capitalize()} seçeneği: {value}")
    except Exception as e:
        print(f"\nSon durum bilgisi alınamadı: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = PytreesNode()
    timer_thread = TimerThread(10.0, node.blackboard)
    timer_thread.start()
    try:
        node.spin()
    except KeyboardInterrupt:
        node.get_logger().info("Kullanıcı tarafından durduruldu")
    finally:
        timer_thread.stop()
        timer_thread.join()
        if rclpy.ok():
            node.tree.shutdown()
            node.destroy_node()
            rclpy.shutdown()
        print_final_state(node.blackboard)
        print("\nSüre bitti!")

if __name__ == '__main__':
    main()
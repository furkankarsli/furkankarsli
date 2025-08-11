#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import py_trees
import py_trees.trees
import threading
import time
import sys
import select
import termios
import tty

# Initialize global variable
end_program = False

class TimerThread(threading.Thread):
    def __init__(self, timeout):
        super().__init__()
        self.timeout = timeout
        self._stop_event = threading.Event()
        self.start_time = time.time()

    def run(self):
        while not self._stop_event.is_set() and (time.time() - self.start_time < self.timeout):
            time.sleep(0.1)

    def stop(self):
        self._stop_event.set()

    def is_timeout(self):
        return (time.time() - self.start_time) >= self.timeout

    def remaining_time(self):
        return max(0, self.timeout - (time.time() - self.start_time))

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

class BaseBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, node, name, prompt, valid_inputs, success_inputs):
        super().__init__(name)
        self.node = node
        self.prompt = prompt
        self.valid_inputs = valid_inputs
        self.success_inputs = success_inputs
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(f"{name.lower()}_secenek", access=py_trees.common.Access.WRITE)

    def update(self):
        global timer_thread, end_program
        if end_program or timer_thread.is_timeout():
            self.node.get_logger().warn(f"Zaman aşımı veya son: {self.name} davranışı başarısız")
            return py_trees.common.Status.FAILURE
        if not sys.stdin.isatty():
            self.node.get_logger().warn("Terminal interaktif değil, giriş beklenemez")
            return py_trees.common.Status.FAILURE
        try:
            remaining_time = timer_thread.remaining_time()
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE
            secenek = get_input_with_timeout(self.prompt, remaining_time)
            if secenek is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE
            self.blackboard.set(f"{self.name.lower()}_secenek", secenek)
            if secenek in self.success_inputs:
                self.node.get_logger().info(f"{self.name}: {secenek} seçildi")
                return py_trees.common.Status.SUCCESS
            elif secenek == 'i':
                self.node.get_logger().info("Idle durumuna geçiliyor...")
                return py_trees.common.Status.FAILURE
            elif secenek == 'e':
                self.node.get_logger().info("Program sonlandırılıyor...")
                end_program = True
                return py_trees.common.Status.FAILURE
            else:
                self.node.get_logger().warn(f"Geçersiz giriş! {', '.join(self.valid_inputs)} girin")
                return py_trees.common.Status.RUNNING
        except Exception as e:
            self.node.get_logger().error(f"Hata in {self.name}: {str(e)}")
            return py_trees.common.Status.FAILURE

class IdleBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, node, name="Idle"):
        super().__init__(name)
        self.node = node
        self.prompt = "uyumak için 'u', dinlenmek için 'd', spor için 's', çalışmak için 'c', uyanmak için 'k', son için 'e': "
        self.valid_inputs = [ 'u', 'd', 's', 'c', 'k', 'e']
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("idle_secenek", access=py_trees.common.Access.WRITE)

    def update(self):
        global timer_thread, end_program
        if end_program or timer_thread.is_timeout():
            self.node.get_logger().warn("Zaman aşımı veya son: Idle davranışı başarısız")
            return py_trees.common.Status.FAILURE
        if not sys.stdin.isatty():
            self.node.get_logger().warn("Terminal interaktif değil, giriş beklenemez")
            return py_trees.common.Status.FAILURE
        try:
            remaining_time = timer_thread.remaining_time()
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE
            secenek = get_input_with_timeout(self.prompt, remaining_time)
            if secenek is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE
            self.blackboard.idle_secenek = secenek
            if secenek in ['u', 'd', 's', 'c', 'k']:
                self.node.get_logger().info(f"{secenek} durumuna geçiliyor...")
                return py_trees.common.Status.FAILURE
            elif secenek == 'e':
                self.node.get_logger().info("Program sonlandırılıyor...")
                end_program = True
                return py_trees.common.Status.FAILURE
            else:
                self.node.get_logger().warn("Geçersiz giriş!  'u', 'd', 's', 'c', 'k' veya 'e' girin")
                return py_trees.common.Status.RUNNING
        except Exception as e:
            self.node.get_logger().error(f"Hata in Idle: {str(e)}")
            return py_trees.common.Status.FAILURE

class PytreesNode(Node):
    def __init__(self):
        super().__init__('pytrees_node')
        self.tree = py_trees.trees.BehaviourTree(self.create_behavior_tree())
        self.tree.setup()
        py_trees.display.render_dot_tree(self.tree.root)
        self.running = True

    def create_behavior_tree(self):
        root = py_trees.composites.Selector(name="Root", memory=True)
        main_flow = py_trees.composites.Sequence(name="AnaAkis", memory=True)
        calis_akisi = py_trees.composites.Sequence(name="CalisAkisi", memory=True)
        calis_akisi.add_children([
            BaseBehaviour(self, "Calis", "Dinlenmek için 'd', idle için 'i', son için 'e': ", ['d', 'i', 'e'], ['d']),
            BaseBehaviour(self, "Dinlen", "Uyumak için 'u', idle için 'i', son için 'e': ", ['u', 'i', 'e'], ['u'])
        ])
        spor_akisi = py_trees.composites.Sequence(name="SporAkisi", memory=True)
        spor_akisi.add_children([
            BaseBehaviour(self, "Spor", "Dinlenmek için 'd', idle için 'i', son için 'e': ", ['d', 'i', 'e'], ['d']),
            BaseBehaviour(self, "Dinlen", "Uyumak için 'u', idle için 'i', son için 'e': ", ['u', 'i', 'e'], ['u'])
        ])
        secim_agaci = py_trees.composites.Selector(name="SecimAgaci", memory=True)
        secim_agaci.add_children([calis_akisi, spor_akisi])
        main_flow.add_children([
            BaseBehaviour(self, "Uyan", "Kalkmak için 'k', devam için 'd', idle için 'i', son için 'e': ", ['k', 'd', 'i', 'e'], ['k']),
            BaseBehaviour(self, "Kahvalti", "Çalışmaya gitmek için 'c', spor yapmak için 's', idle için 'i', son için 'e': ", ['c', 's', 'i', 'e'], ['c', 's']),
            secim_agaci
        ])
        root.add_children([main_flow, IdleBehaviour(self)])
        return root

    def spin(self):
        global timer_thread, end_program
        while rclpy.ok() and self.running and not timer_thread.is_timeout() and not end_program:
            self.tree.tick()
            time.sleep(0.1)
        self.get_logger().info("Sistem kapatılıyor...")
        self.tree.shutdown()
        self.destroy_node()
        rclpy.shutdown()

def print_final_state(node):
    try:
        print("\nSon durum:")
        root = node.tree.root
        main_flow = root.children[0]
        bb = main_flow.children[0].blackboard
        print(f"Uyan seçeneği: {bb.uyan_secenek if bb.has_key('uyan_secenek') else 'N/A'}")
        bb = main_flow.children[1].blackboard
        print(f"Kahvaltı seçeneği: {bb.kahvalti_secenek if bb.has_key('kahvalti_secenek') else 'N/A'}")
        if main_flow.children[2].children[0].status == py_trees.common.Status.SUCCESS:
            bb = main_flow.children[2].children[0].children[0].blackboard
            print(f"Çalış seçeneği: {bb.calis_secenek if bb.has_key('calis_secenek') else 'N/A'}")
            bb = main_flow.children[2].children[0].children[1].blackboard
            print(f"Çalış-Dinlen seçeneği: {bb.dinlen_secenek if bb.has_key('dinlen_secenek') else 'N/A'}")
        elif main_flow.children[2].children[1].status == py_trees.common.Status.SUCCESS:
            bb = main_flow.children[2].children[1].children[0].blackboard
            print(f"Spor seçeneği: {bb.spor_secenek if bb.has_key('spor_secenek') else 'N/A'}")
            bb = main_flow.children[2].children[1].children[1].blackboard
            print(f"Spor-Dinlen seçeneği: {bb.dinlen_secenek if bb.has_key('dinlen_secenek') else 'N/A'}")
        bb = root.children[1].blackboard
        print(f"Idle seçeneği: {bb.idle_secenek if bb.has_key('idle_secenek') else 'N/A'}")
    except Exception as e:
        print(f"\nSon durum bilgisi alınamadı: {str(e)}")

def main(args=None):
    global timer_thread, end_program
    end_program = False
    rclpy.init(args=args)
    timer_thread = TimerThread(100.0)  # 10-second timeout
    timer_thread.start()
    node = PytreesNode()
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
        print_final_state(node)
        print("\nSüre bitti!")

if __name__ == '__main__':
    main()
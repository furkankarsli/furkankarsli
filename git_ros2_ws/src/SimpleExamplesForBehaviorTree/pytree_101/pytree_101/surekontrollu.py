#!/usr/bin/env python3
import rclpy
import time
import py_trees
import py_trees_ros.trees
import threading
import sys
import select
import termios
import tty

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

def get_input_with_timeout(prompt, timeout):
    """Zaman aşımı ile kullanıcı girişi alır."""
    print(prompt, end='', flush=True)
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            response = sys.stdin.readline().strip()
            return response
        else:
            return None
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

class HesapMakinesi(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self._setup_blackboard()

    def _setup_blackboard(self):
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("sonuc", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("/isim", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("/yas", access=py_trees.common.Access.WRITE)

    def update(self):
        if timer_thread.is_timeout():
            return py_trees.common.Status.FAILURE

        try:
            remaining_time = timer_thread.timeout - (time.time() - timer_thread.start_time)
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE

            sayi1_str = get_input_with_timeout("Birinci sayı: ", remaining_time)
            if sayi1_str is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE
            sayi1 = float(sayi1_str)

            sayi2_str = get_input_with_timeout("İkinci sayı: ", remaining_time)
            if sayi2_str is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE
            sayi2 = float(sayi2_str)

            islem = get_input_with_timeout("İşlem (+, -, *, /): ", remaining_time)
            if islem is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE

            if islem == '+':
                result = sayi1 + sayi2
            elif islem == '-':
                result = sayi1 - sayi2
            elif islem == '*':
                result = sayi1 * sayi2
            elif islem == '/':
                result = sayi1 / sayi2
            else:
                return py_trees.common.Status.FAILURE

            self.blackboard.sonuc = result
            print(f"Sonuç: {result}")
            return py_trees.common.Status.SUCCESS

        except (ValueError, TypeError):
            return py_trees.common.Status.FAILURE

class IsimSor(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self._setup_blackboard()

    def _setup_blackboard(self):
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("/isim", access=py_trees.common.Access.WRITE)

    def update(self):
        if timer_thread.is_timeout():
            return py_trees.common.Status.FAILURE

        try:
            remaining_time = timer_thread.timeout - (time.time() - timer_thread.start_time)
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE

            name = get_input_with_timeout("Adınız: ", remaining_time)
            if name is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE

            self.blackboard.isim = name
            return py_trees.common.Status.SUCCESS
        except:
            return py_trees.common.Status.FAILURE

class YasSor(py_trees.behaviour.Behaviour):
    def __init__(self, name):
        super().__init__(name)
        self._setup_blackboard()

    def _setup_blackboard(self):
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("/yas", access=py_trees.common.Access.WRITE)

    def update(self):
        if timer_thread.is_timeout():
            return py_trees.common.Status.FAILURE

        try:
            remaining_time = timer_thread.timeout - (time.time() - timer_thread.start_time)
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE

            age_str = get_input_with_timeout("Yaşınız: ", remaining_time)
            if age_str is None or timer_thread.is_timeout():
                return py_trees.common.Status.FAILURE
            age = int(age_str)

            self.blackboard.yas = age
            return py_trees.common.Status.SUCCESS
        except (ValueError, TypeError):
            return py_trees.common.Status.FAILURE

def create_tree():
    root = py_trees.composites.Sequence(name="Ana Döngü", memory=True)
    root.add_children([
        HesapMakinesi("Hesap Makinesi"),
        IsimSor("İsim Sorma"),
        YasSor("Yaş Sorma")
    ])
    return root

def main():
    global timer_thread
    rclpy.init()
    tree = py_trees_ros.trees.BehaviourTree(create_tree())
    tree.setup(timeout=15.0)

    # 10 saniyelik zaman aşımı (örnek olarak kısa süre)
    timer_thread = TimerThread(10.0)
    timer_thread.start()

    try:
        while not timer_thread.is_timeout():
            tree.tick()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        timer_thread.stop()
        timer_thread.join()
        rclpy.shutdown()

        # Son durumu güvenli şekilde yazdır
        try:
            print("\nSon durum:")
            print(f"Sonuç: {tree.root.children[0].blackboard.get('sonuc', 'N/A')}")
            print(f"İsim: {tree.root.children[1].blackboard.get('/isim', 'N/A')}")
            print(f"Yaş: {tree.root.children[2].blackboard.get('/yas', 'N/A')}")
        except:
            print("\nSon durum bilgisi alınamadı")
        print("\nSüre bitti!")

if __name__ == '__main__':
    main()
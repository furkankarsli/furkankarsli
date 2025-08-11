import rclpy
from rclpy.node import Node
import py_trees
import threading
import time
import sys

class PytreesNode(Node):
    def __init__(self):
        super().__init__('pytrees_node')
        self.batarya_bitisi = threading.Event()
        self.agac = py_trees.trees.BehaviourTree(self.agac_olustur())
        self.agac.setup(timeout=10)
        
        # Batarya thread'i başlat
        self.batarya_thread = threading.Thread(
            target=self.batarya_geri_sayim,
            args=(self.batarya_bitisi,),
            daemon=True
        )
        self.batarya_thread.start()

    def agac_olustur(self):
        kok = py_trees.composites.Sequence(name="Ana Akış", memory=True)
        kok.add_children([
            Dogum(self),
            Isim(self)
        ])
        return kok

    def batarya_geri_sayim(self, event):
        sure = 10  # 10 saniye
        while sure > 0 and not event.is_set():
            time.sleep(1)
            sure -= 1
        event.set()
        self.get_logger().warn("Zaman doldu!")
        rclpy.shutdown()

    def calistir(self):
        try:
            while rclpy.ok() and not self.batarya_bitisi.is_set():
                self.agac.tick()
                time.sleep(0.1)  # CPU kullanımını azaltmak için
        except KeyboardInterrupt:
            self.batarya_bitisi.set()

class Dogum(py_trees.behaviour.Behaviour):
    def __init__(self, node):
        super().__init__(name="Dogum")
        self.node = node
        self.yapildi = False

    def update(self):
        if self.yapildi:
            return py_trees.common.Status.SUCCESS
            
        try:
            gun = int(input("Doğduğunuz gün: "))
            ay = int(input("Doğduğunuz ay: "))
            self.node.get_logger().info(f"Doğum tarihi: {gun}.{ay}")
            self.yapildi = True
            return py_trees.common.Status.SUCCESS
        except ValueError:
            print("Geçersiz giriş! Lütfen sayı girin.")
            return py_trees.common.Status.RUNNING

class Isim(py_trees.behaviour.Behaviour):
    def __init__(self, node):
        super().__init__(name="Isim")
        self.node = node
        self.yapildi = False

    def update(self):
        if self.yapildi:
            return py_trees.common.Status.SUCCESS
            
        try:
            isim = input("İsminiz: ").strip()
            if not isim:
                raise ValueError("Boş isim")
            self.node.get_logger().info(f"İsim: {isim}")
            self.yapildi = True
            return py_trees.common.Status.SUCCESS
        except Exception:
            print("Geçersiz giriş! Lütfen tekrar deneyin.")
            return py_trees.common.Status.RUNNING

def main():
    rclpy.init()
    node = PytreesNode()
    node.calistir()
    
    # Temizlik
    node.batarya_bitisi.set()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
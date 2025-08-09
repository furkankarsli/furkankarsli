# run_tree.py dosyasının Humble viewer ile uyumlu, kanıta dayalı son hali

import rclpy
from rclpy.node import Node
import py_trees
import py_trees_ros
from turtle_tasks.turtle_behavior_tree import create_service_robot_tree
import sys
import logging
import os

# VIEWER İÇİN GEREKLİ DOĞRU İÇE AKTARMALAR
from py_trees_ros.visitors import TreeToMsgVisitor
from py_trees_msgs.msg import BehaviourTree as BehaviourTreeMsg

class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('behavior_tree_node')
        
        # --- LOGLAMA KURULUMU (DEĞİŞİKLİK YOK) ---
        log_file_path = os.path.join(os.path.expanduser('~'), 'ros2_ws', 'bt_debug.log')
        # ... (loglama kodunun geri kalanı aynı) ...
        if os.path.exists(log_file_path):
            open(log_file_path, 'w').close()
        self.file_logger = logging.getLogger('file_logger')
        self.file_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.file_logger.addHandler(handler)
        self.file_logger.info("Davranış ağacı loglaması başlatıldı.")
        
        # --- AĞAÇ OLUŞTURMA (DEĞİŞİKLİK YOK) ---
        root_behavior = create_service_robot_tree(self, self.file_logger) 
        
        self.tree = py_trees_ros.trees.BehaviourTree(root=root_behavior)

        # --- VIEWER İÇİN GEREKLİ YENİ KODLAR ---
        # 1. Ağacı mesaja çevirecek ziyaretçiyi oluştur
        self.snapshot_visitor = TreeToMsgVisitor()
        self.tree.add_visitor(self.snapshot_visitor)

        # 2. Mesajı yayınlayacak ROS publisher'ı oluştur
        self.snapshot_publisher = self.create_publisher(
            msg_type=BehaviourTreeMsg,
            topic="/tree/snapshot_stream",
            qos_profile=10
        )
        # --- YENİ KODLARIN SONU ---
        
        self.last_tree_snapshot = ""
        self.last_blackboard_str = ""
        
        try:
            self.tree.setup(timeout=15.0)
        except Exception as e:
            self.get_logger().error(f"Ağaç kurulumu sırasında hata oluştu: {e}")
            self.file_logger.error(f"Ağaç kurulumu sırasında hata oluştu: {e}")
            self.destroy_node()
            rclpy.shutdown()
            sys.exit(1)

        self.timer = self.create_timer(1.0 / 2.0, self.tick)

    def tick(self):
        # Ağacı ve ziyaretçileri tetikle
        self.tree.tick()

        # --- VIEWER İÇİN YAYINLAMA KODU ---
        # Ziyaretçiden güncel ağaç mesajını al ve yayınla
        tree_msg = self.snapshot_visitor.msg
        self.snapshot_publisher.publish(tree_msg)
        # --- YAYINLAMA KODU SONU ---

        # Loglama ve konsol çıktısı için olan kodlar aynı kalıyor
        current_tree_snapshot = py_trees.display.ascii_tree(self.tree.root, show_status=True)
        if current_tree_snapshot != self.last_tree_snapshot:
            self.file_logger.info("Ağaç Durumu Değişti:\n" + current_tree_snapshot)
            self.last_tree_snapshot = current_tree_snapshot
            
        bb = py_trees.blackboard.Blackboard()
        current_blackboard_str = (
            f"robot_location: {bb.get('robot_location')}, "
            f"last_command: {bb.get('last_command')}"
        )
        if current_blackboard_str != self.last_blackboard_str:
             self.file_logger.info(f"Blackboard Değişti: {current_blackboard_str}")
             self.last_blackboard_str = current_blackboard_str
        
        print(current_tree_snapshot)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = BehaviorTreeNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        if node:
            if hasattr(node, 'file_logger'):
                node.file_logger.info("Düğüm kapatılıyor, loglama sonlandırıldı.")
            if hasattr(node, 'tree'):
                node.tree.shutdown()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
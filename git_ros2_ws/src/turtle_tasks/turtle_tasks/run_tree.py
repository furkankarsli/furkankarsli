# run_tree.py dosyasının Humble viewer ile uyumlu, kanıta dayalı son hali

import rclpy
from rclpy.node import Node
import py_trees
import py_trees_ros
from turtle_tasks.turtle_behavior_tree import create_service_robot_tree
import sys
import logging
import os
from datetime import datetime

def write_to_log(message: str):
    """Basit log yazma fonksiyonu"""
    try:
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "run_tree.log")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"Log yazma hatası: {e}")

class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('behavior_tree_node')
        
        # Basit loglama kurulumu
        log_file_path = os.path.join(os.path.expanduser('~'), 'ros2_ws', 'bt_debug.log')
        if os.path.exists(log_file_path):
            open(log_file_path, 'w').close()
        self.file_logger = logging.getLogger('file_logger')
        self.file_logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.file_logger.addHandler(handler)
        self.file_logger.info("Davranış ağacı loglaması başlatıldı.")
        
        # Behavior tree oluştur
        root_behavior = create_service_robot_tree(self, self.file_logger) 
        self.tree = py_trees_ros.trees.BehaviourTree(root=root_behavior)
        
        # Tree kurulumu
        try:
            self.tree.setup(timeout=30.0)
            self.file_logger.info("Behavior tree başarıyla kuruldu")
        except Exception as e:
            self.file_logger.error(f"Behavior tree kurulum hatası: {e}")
            self.destroy_node()
            rclpy.shutdown()
            sys.exit(1)

        # Timer kurulumu
        self.timer = self.create_timer(0.5, self.tick)  # 2 Hz
        self.last_tree_snapshot = ""
        self.last_blackboard_str = ""

    def tick(self):
        """Behavior tree'yi çalıştır"""
        try:
            self.tree.tick()
            
            # Tree durumunu logla
            current_tree_snapshot = py_trees.display.ascii_tree(self.tree.root, show_status=True)
            if current_tree_snapshot != self.last_tree_snapshot:
                self.file_logger.info("Tree Durumu Değişti:\n" + current_tree_snapshot)
                self.last_tree_snapshot = current_tree_snapshot
                
            # Blackboard durumunu logla
            bb = py_trees.blackboard.Blackboard()
            current_blackboard_str = (
                f"robot_location: {bb.get('robot_location')}, "
                f"last_command: {bb.get('last_command')}, "
                f"battery_low: {bb.get('battery_low')}"
            )
            if current_blackboard_str != self.last_blackboard_str:
                self.file_logger.info(f"Blackboard Değişti: {current_blackboard_str}")
                self.last_blackboard_str = current_blackboard_str
            
            # Konsola yazdır
            print(current_tree_snapshot)
            
        except Exception as e:
            self.file_logger.error(f"Tick hatası: {e}")

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
                node.file_logger.info("Düğüm kapatılıyor")
            if hasattr(node, 'tree'):
                node.tree.shutdown()
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
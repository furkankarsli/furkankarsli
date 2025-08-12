import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.action.client import ClientGoalHandle
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String
import py_trees
import py_trees.behaviours
import py_trees.composites
import py_trees.decorators
import py_trees.blackboard
import logging
import time
import os
import yaml
from datetime import datetime
import threading

def write_tree_log(message: str):
    """Basit log yazma fonksiyonu"""
    try:
        log_dir = os.path.join(os.path.expanduser("~/ros2_ws/src/turtle_tasks"), "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "treeloglari.txt")
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message)
    except Exception as e:
        print(f"Log yazma hatası: {e}")

class BatteryManager:
    """Basit ve sağlam batarya yöneticisi"""
    def __init__(self):
        self.battery_level = 100.0
        self.charging_timer = None
        self.charging_duration = 120.0
        self.is_charging = False
        self.charging_start_time = None
        self.lock = threading.Lock()
        
    def start_charging(self):
        """Şarjı başlat"""
        with self.lock:
            if not self.is_charging:
                self.is_charging = True
                self.charging_start_time = time.time()
                self.charging_timer = threading.Timer(self.charging_duration, self._charging_complete)
                self.charging_timer.start()
                write_tree_log(f"BatteryManager: Şarj başladı, {self.charging_duration} saniye")
    
    def _charging_complete(self):
        """Şarj tamamlandığında çağrılır"""
        with self.lock:
            self.is_charging = False
            self.battery_level = 100.0
            self.charging_timer = None
            write_tree_log(f"BatteryManager: Şarj tamamlandı!")
    
    def get_remaining_charging_time(self):
        """Kalan şarj süresini döndür"""
        with self.lock:
            if self.is_charging and self.charging_start_time:
                elapsed = time.time() - self.charging_start_time
                remaining = max(0, self.charging_duration - elapsed)
                return remaining
            return 0.0
    
    def is_charging_active(self):
        """Şarj aktif mi kontrol et"""
        with self.lock:
            return self.is_charging
    
    def get_battery_level(self):
        """Batarya seviyesini döndür"""
        with self.lock:
            return self.battery_level
    
    def decrease_battery(self, amount=0.5):
        """Bataryayı azalt"""
        with self.lock:
            self.battery_level = max(0.0, self.battery_level - amount)
            return self.battery_level
    
    def cleanup(self):
        """Temizlik yap"""
        if self.charging_timer:
            self.charging_timer.cancel()

# Global battery manager instance
battery_manager = BatteryManager()

class Navigate(py_trees.behaviour.Behaviour):
    """Basitleştirilmiş navigasyon behavior'ı"""
    def __init__(self, name: str, node: Node, pose: dict, location_name: str, logger: logging.Logger):
        super().__init__(name)
        self.node = node
        self.pose = pose
        self.location_name = location_name
        self.logger = logger
        self.client = ActionClient(self.node, NavigateToPose, "/navigate_to_pose")
        self.blackboard = py_trees.blackboard.Blackboard()
        self.goal_handle = None
        self.final_status = None
        self.start_time = None
        self.timeout_seconds = 300.0
        self.goal_sent = False

    def setup(self, **kwargs):
        if not self.client.wait_for_server(timeout_sec=10.0):
            self.logger.error(f"[{self.name}] Navigasyon sunucusu bulunamadı!")
            return False
        return True

    def initialise(self):
        if self.final_status == py_trees.common.Status.FAILURE:
            return

        write_tree_log(f"{self.name}: {self.location_name} konumuna gidiliyor")
        self.start_time = time.time()
        self.goal_sent = False
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(self.pose['x'])
        goal_msg.pose.pose.position.y = float(self.pose['y'])
        goal_msg.pose.pose.position.z = 0.0
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = float(self.pose['oz'])
        goal_msg.pose.pose.orientation.w = float(self.pose['ow'])
        
        try:
            send_goal_future = self.client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.goal_response_callback)
            self.goal_sent = True
        except Exception as e:
            self.logger.error(f"[{self.name}] Hedef gönderilirken hata: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def goal_response_callback(self, future):
        try:
            self.goal_handle = future.result()
            if not self.goal_handle or not self.goal_handle.accepted:
                self.logger.error(f"[{self.name}] Hedef reddedildi.")
                self.final_status = py_trees.common.Status.FAILURE
                return
            
            get_result_future = self.goal_handle.get_result_async()
            get_result_future.add_done_callback(self.get_result_callback)
        except Exception as e:
            self.logger.error(f"[{self.name}] Hedef yanıtı alınırken hata: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def get_result_callback(self, future):
        try:
            result = future.result()
            status = result.status
            
            if status == 4:  # SUCCEEDED
                self.final_status = py_trees.common.Status.SUCCESS
            else:
                self.final_status = py_trees.common.Status.FAILURE
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Sonuç alınırken hata: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def update(self) -> py_trees.common.Status:
        if self.start_time and time.time() - self.start_time > self.timeout_seconds:
            if self.goal_handle:
                self.goal_handle.cancel_goal_async()
            self.final_status = py_trees.common.Status.FAILURE
        
        if self.final_status:
            return self.final_status
            
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status: py_trees.common.Status):
        if new_status == py_trees.common.Status.SUCCESS:
            self.blackboard.set("robot_location", self.location_name)
            write_tree_log(f"{self.name}: {self.location_name} konumuna ulaşıldı")
        
        if self.goal_handle and self.final_status is None:
            self.goal_handle.cancel_goal_async()
        
        self.goal_handle = None
        self.final_status = None
        self.start_time = None
        self.goal_sent = False

class Wait(py_trees.behaviour.Behaviour):
    """Basit bekleme behavior'ı"""
    def __init__(self, name: str, wait_time: float):
        super().__init__(name)
        self.wait_time = wait_time
        self.start_time = None

    def initialise(self):
        self.start_time = time.time()

    def update(self) -> py_trees.common.Status:
        if time.time() - self.start_time >= self.wait_time:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING

class CheckForCommand(py_trees.behaviour.Behaviour):
    """Komut kontrol behavior'ı"""
    def __init__(self, name: str, expected_command: str):
        super().__init__(name)
        self.expected_command = expected_command
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        command = self.blackboard.get("last_command")
        
        if command == self.expected_command:
            return py_trees.common.Status.SUCCESS
        
        return py_trees.common.Status.FAILURE

class ClearCommand(py_trees.behaviour.Behaviour):
    """Komut temizleme behavior'ı"""
    def __init__(self, name: str = "Komutu Temizle"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        self.blackboard.set("last_command", None)
        return py_trees.common.Status.SUCCESS

class BatteryMonitor(py_trees.behaviour.Behaviour):
    """Basitleştirilmiş batarya monitörü"""
    def __init__(self, name: str = "Batarya Monitörü"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.last_update = time.time()

    def update(self) -> py_trees.common.Status:
        current_time = time.time()
        current_location = self.blackboard.get("robot_location")
        
        # Her 2 saniyede bir bataryayı azalt
        if current_time - self.last_update >= 2.0:
            if current_location != "sarj" and not battery_manager.is_charging_active():
                battery_manager.decrease_battery(0.5)
            self.last_update = current_time
        
        battery_level = battery_manager.get_battery_level()
        write_tree_log(f"{self.name}: Konum: {current_location}, Batarya: {battery_level:.1f}%")
        
        # Batarya kritik seviyede mi kontrol et
        if battery_level <= 20.0 and not battery_manager.is_charging_active():
            write_tree_log(f"{self.name}: BATARYA KRİTİK! Acil şarj gerekli!")
            self.blackboard.set("battery_low", True)
            return py_trees.common.Status.FAILURE
        
        # Şarj aktif mi kontrol et
        if battery_manager.is_charging_active():
            remaining_time = battery_manager.get_remaining_charging_time()
            if remaining_time <= 0:
                write_tree_log(f"{self.name}: Şarj tamamlandı!")
                self.blackboard.set("battery_low", False)
                return py_trees.common.Status.SUCCESS
            return py_trees.common.Status.RUNNING
        
        self.blackboard.set("battery_low", False)
        return py_trees.common.Status.SUCCESS

class ChargingStation(py_trees.behaviour.Behaviour):
    """Şarj istasyonunda bekleyen behavior"""
    def __init__(self, name: str, wait_time: float = 10.0):
        super().__init__(name)
        self.wait_time = wait_time
        self.start_time = None
        self.charging_started = False

    def initialise(self):
        self.start_time = time.time()
        self.charging_started = False

    def update(self) -> py_trees.common.Status:
        current_time = time.time()
        
        # Şarjı başlat
        if not self.charging_started:
            battery_manager.start_charging()
            self.charging_started = True
            write_tree_log(f"{self.name}: Şarj başlatıldı, 120 saniye geri sayım başladı!")
        
        # 10 saniye bekle
        if current_time - self.start_time >= self.wait_time:
            write_tree_log(f"{self.name}: 10 saniye bekleme tamamlandı, şarj arka planda devam ediyor...")
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.RUNNING

class CommandSubscriber(py_trees.behaviour.Behaviour):
    """Komut dinleyici behavior'ı"""
    def __init__(self, name: str, node: Node):
        super().__init__(name)
        self.node = node
        self.blackboard = py_trees.blackboard.Blackboard()
        self.subscription = node.create_subscription(String, "/robot_command", self.command_callback, 10)

    def command_callback(self, msg):
        write_tree_log(f"CommandSubscriber: Yeni komut alındı: '{msg.data}'")
        self.blackboard.set("last_command", msg.data)

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.SUCCESS

def create_task1_sequence(node, logger, poses):
    """Task1 için basit sequence"""
    task1_seq = py_trees.composites.Sequence(name="Task1", memory=True)
    task1_seq.add_children([
        CheckForCommand(name="task1KomutuVarMi?", expected_command="task1"),
        Navigate(name="AyaGit_Task1", node=node, pose=poses["A"], location_name="A", logger=logger),
        Wait(name="Task1Bekle", wait_time=2.0),
        ClearCommand(name="Task1KomutunuTemizle")
    ])
    return task1_seq

def create_task2_sequence(node, logger, poses):
    """Task2 için basit sequence"""
    task2_seq = py_trees.composites.Sequence(name="Task2", memory=True)
    task2_seq.add_children([
        CheckForCommand(name="task2KomutuVarMi?", expected_command="task2"),
        Navigate(name="AyaGit_Task2", node=node, pose=poses["A"], location_name="A", logger=logger),
        Wait(name="Task2ABekle", wait_time=2.0),
        Navigate(name="ByeGit_Task2", node=node, pose=poses["B"], location_name="B", logger=logger),
        Wait(name="Task2BBekle", wait_time=2.0),
        ClearCommand(name="Task2KomutunuTemizle")
    ])
    return task2_seq

def create_task3_sequence(node, logger, poses):
    """Task3 için basit sequence"""
    task3_seq = py_trees.composites.Sequence(name="Task3", memory=True)
    task3_seq.add_children([
        CheckForCommand(name="task3KomutuVarMi?", expected_command="task3"),
        Navigate(name="AyaGit_Task3", node=node, pose=poses["A"], location_name="A", logger=logger),
        Wait(name="Task3ABekle", wait_time=2.0),
        Navigate(name="ByeGit_Task3", node=node, pose=poses["B"], location_name="B", logger=logger),
        Wait(name="Task3BBekle", wait_time=2.0),
        Navigate(name="CyeGit_Task3", node=node, pose=poses["C"], location_name="C", logger=logger),
        Wait(name="Task3CBekle", wait_time=2.0),
        ClearCommand(name="Task3KomutunuTemizle")
    ])
    return task3_seq

def create_emergency_charge_sequence(node, logger, poses):
    """Acil şarj için sequence"""
    emergency_charge = py_trees.composites.Sequence(name="AcilŞarj", memory=True)
    emergency_charge.add_children([
        BatteryMonitor(name="BataryaKontrol"),
        Navigate(name="sarjaGit", node=node, pose=poses["sarj"], location_name="sarj", logger=logger),
        ChargingStation(name="Şarjİstasyonu", wait_time=10.0),
        Navigate(name="Idle'aDön", node=node, pose=poses["idle"], location_name="idle", logger=logger)
    ])
    return emergency_charge

def create_service_robot_tree(node: Node, logger: logging.Logger) -> py_trees.behaviour.Behaviour:
    # Pozisyonları yükle
    try:
        yaml_path = os.path.join(os.path.dirname(__file__), "poses.yaml")
        with open(yaml_path, 'r') as f:
            POSES = yaml.safe_load(f)['poses']
        logger.info("Pozisyonlar YAML dosyasından başarıyla yüklendi")
    except Exception as e:
        logger.error(f"YAML dosyası yüklenemedi: {e}")
        # Fallback pozisyonlar
        POSES = {
            "baslangic": {'x': 0.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
            "sarj": {'x': 0.2, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
            "idle": {'x': 1.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
            "A": {'x': 2.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
            "B": {'x': 3.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
            "C": {'x': 4.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        }

    root = py_trees.composites.Parallel(
        name="Servis Robotu",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )

    background_tasks = CommandSubscriber(name="KomutDinleyici", node=node)
    
    main_logic = py_trees.composites.Selector(name="Ana Mantık", memory=False)
    
    # Görevleri oluştur
    emergency_charge = create_emergency_charge_sequence(node, logger, POSES)
    task1_sequence = create_task1_sequence(node, logger, POSES)
    task2_sequence = create_task2_sequence(node, logger, POSES)
    task3_sequence = create_task3_sequence(node, logger, POSES)
    
    idle = py_trees.behaviours.Running(name="Bosta")

    main_logic.add_children([
        emergency_charge,  # Öncelik: Acil şarj
        task1_sequence,
        task2_sequence, 
        task3_sequence,
        idle
    ])
    
    root.add_children([background_tasks, main_logic])
    
    # Blackboard'ı başlat
    py_trees.blackboard.Blackboard().set("robot_location", "baslangic")
    py_trees.blackboard.Blackboard().set("last_command", None)
    py_trees.blackboard.Blackboard().set("battery_low", False)

    return root
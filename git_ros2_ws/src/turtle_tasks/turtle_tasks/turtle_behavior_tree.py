import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient, ClientGoalHandle
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
from datetime import datetime

def write_tree_log(message: str):
    try:
        log_dir = os.path.join(os.path.expanduser("~/ros2_ws/src/turtle_tasks"), "logs")
        log_file = os.path.join(log_dir, "treeloglari.txt")
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}\n"
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message)
    except Exception as e:
        print(f"Log yazma hatası: {e}")

class Navigate(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, node: Node, pose: dict, location_name: str, logger: logging.Logger):
        super().__init__(name)
        self.node = node
        self.pose = pose
        self.location_name = location_name
        self.logger = logger
        self.client = ActionClient(self.node, NavigateToPose, "/navigate_to_pose")
        self.blackboard = py_trees.blackboard.Blackboard()
        self.goal_handle: ClientGoalHandle = None
        self.final_status = None
        self.start_time = None
        self.timeout_seconds = 300.0
        self.max_retries = 5
        self.retry_count = 0
        self.is_initialized = False

    def setup(self, **kwargs):
        self.logger.info(f"[{self.name}] Kurulum yapılıyor...")
        if not self.client.wait_for_server(timeout_sec=5.0):
            self.logger.error(f"[{self.name}] Navigasyon sunucusu bulunamadı!")
            self.final_status = py_trees.common.Status.FAILURE
            return False
        return True

    def initialise(self):
        if self.final_status == py_trees.common.Status.FAILURE:
            return

        write_tree_log(f"{self.name}: {self.location_name} konumuna gidiliyor. Hedef: {self.pose}")
        self.logger.info(f"[{self.name}] {self.location_name} konumuna gidiliyor. Hedef: {self.pose}")
        self.start_time = time.time()
        self.is_initialized = True
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = self.pose['x']
        goal_msg.pose.pose.position.y = self.pose['y']
        goal_msg.pose.pose.orientation.z = self.pose['oz']
        goal_msg.pose.pose.orientation.w = self.pose['ow']
        
        try:
            send_goal_future = self.client.send_goal_async(goal_msg)
            send_goal_future.add_done_callback(self.goal_response_callback)
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
            
            self.logger.info(f"[{self.name}] Hedef kabul edildi, sonuç bekleniyor...")
            get_result_future = self.goal_handle.get_result_async()
            get_result_future.add_done_callback(self.get_result_callback)
        except Exception as e:
            self.logger.error(f"[{self.name}] Hedef yanıtı alınırken hata: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def get_result_callback(self, future):
        try:
            result = future.result()
            status = result.status
            self.logger.info(f"[{self.name}] Navigasyon sonucu geldi. Durum Kodu: {status}")
            
            if status == 4:
                self.final_status = py_trees.common.Status.SUCCESS
                self.logger.info(f"[{self.name}] Navigasyon başarılı!")
            elif status == 5:
                self.logger.warning(f"[{self.name}] Görev iptal edildi.")
                self.final_status = py_trees.common.Status.FAILURE
            elif status == 6:
                self.logger.warning(f"[{self.name}] Görev iptal edildi (ABORTED).")
                self.final_status = py_trees.common.Status.FAILURE
            else:
                self.logger.error(f"[{self.name}] Navigasyon başarısız oldu. Durum: {status}")
                self.final_status = py_trees.common.Status.FAILURE
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Sonuç alınırken hata oluştu: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def update(self) -> py_trees.common.Status:
        if self.start_time and time.time() - self.start_time > self.timeout_seconds:
            self.logger.warning(f"[{self.name}] Timeout! {self.timeout_seconds} saniye geçti.")
            if self.goal_handle:
                self.goal_handle.cancel_goal_async()
            self.final_status = py_trees.common.Status.FAILURE
        
        if (self.final_status == py_trees.common.Status.FAILURE and 
            self.retry_count < self.max_retries and 
            self.is_initialized):
            
            self.retry_count += 1
            self.logger.info(f"[{self.name}] Retry {self.retry_count}/{self.max_retries} deneniyor...")
            self.final_status = None
            self.start_time = None
            self.is_initialized = False
            self.initialise()
            return py_trees.common.Status.RUNNING
        
        if self.final_status:
            return self.final_status
            
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status: py_trees.common.Status):
        current_location = self.blackboard.get("robot_location")
        self.logger.info(f"[{self.name}] Sonlandırılıyor. Önceki konum: '{current_location}', Yeni durum: {new_status.name}")
        
        if self.goal_handle and self.final_status is None:
            self.logger.warning(f"[{self.name}] Yeni bir komut nedeniyle görev iptal ediliyor...")
            self.goal_handle.cancel_goal_async()

        if new_status == py_trees.common.Status.SUCCESS:
            self.blackboard.set("robot_location", self.location_name)
            self.logger.info(f"[{self.name}] Başarıyla ulaşıldı. Yeni konum karatahtaya yazıldı: {self.location_name}")
        elif new_status == py_trees.common.Status.FAILURE:
            current_command = self.blackboard.get("last_command")
            if current_command:
                self.blackboard.set("failed_task", current_command)
                self.logger.warning(f"[{self.name}] Görev başarısız, yeniden denenecek: {current_command}")
        
        self.goal_handle = None
        self.final_status = None
        self.start_time = None
        self.is_initialized = False
        self.retry_count = 0

class Wait(py_trees.behaviour.Behaviour):
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
    def __init__(self, name: str, expected_command: str):
        super().__init__(name)
        self.expected_command = expected_command
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        command = self.blackboard.get("last_command")
        write_tree_log(f"{self.name}: Beklenen='{self.expected_command}', Gelen='{command}'")
        
        if command == self.expected_command:
            write_tree_log(f"{self.name}: Komut eşleşti! SUCCESS")
            return py_trees.common.Status.SUCCESS
        
        write_tree_log(f"{self.name}: Komut eşleşmedi! FAILURE")
        return py_trees.common.Status.FAILURE

class ClearCommand(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "Komutu Temizle"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        self.blackboard.set("last_command", None)
        return py_trees.common.Status.SUCCESS

class CheckLocation(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, location: str):
        super().__init__(name)
        self.location = location
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        current_location = self.blackboard.get("robot_location")
        if current_location == self.location:
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.FAILURE

class CommandSubscriber(py_trees.behaviour.Behaviour):
    def __init__(self, name: str, node: Node):
        super().__init__(name)
        self.node = node
        self.blackboard = py_trees.blackboard.Blackboard()
        self.subscription = node.create_subscription(String, "/robot_command", self.command_callback, 10)

    def command_callback(self, msg):
        write_tree_log(f"CommandSubscriber: Yeni komut alındı: '{msg.data}'")
        self.node.get_logger().info(f"Yeni komut alındı: '{msg.data}'")
        self.blackboard.set("last_command", msg.data)

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.SUCCESS

class BatteryMonitor(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "Batarya Monitörü"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.battery_level = 100.0
        self.last_update = time.time()

    def update(self) -> py_trees.common.Status:
        current_time = time.time()
        current_location = self.blackboard.get("robot_location")
        write_tree_log(f"{self.name}: Mevcut konum: {current_location}, Batarya: {self.battery_level:.1f}%")
        
        if current_location != "sarj":
            if current_time - self.last_update >= 60.0:
                self.battery_level = 20.0
                self.last_update = current_time
                write_tree_log(f"{self.name}: Batarya kritik seviyeye düştü: %{self.battery_level}")
            
            if self.battery_level <= 20.0:
                write_tree_log(f"{self.name}: BATARYA KRİTİK! Acil şarj gerekli!")
                self.blackboard.set("battery_low", True)
                return py_trees.common.Status.FAILURE
            
            self.blackboard.set("battery_low", False)
            return py_trees.common.Status.SUCCESS
        
        if self.battery_level >= 100.0:
            self.blackboard.set("battery_low", False)
            return py_trees.common.Status.SUCCESS
        
        if current_time - self.last_update >= 10.0:
            self.battery_level = 100.0
            self.last_update = current_time
            write_tree_log(f"{self.name}: Şarj tamamlandı! Batarya: %{self.battery_level}")
            return py_trees.common.Status.SUCCESS
            
        return py_trees.common.Status.RUNNING

def create_service_robot_tree(node: Node, logger: logging.Logger) -> py_trees.behaviour.Behaviour:
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

    go_to_sarj = Navigate(name="sarjaGit", node=node, pose=POSES["sarj"], location_name="sarj", logger=logger)
    go_to_idle = Navigate(name="idleaGit", node=node, pose=POSES["idle"], location_name="idle", logger=logger)
    
    go_to_A_task1 = Navigate(name="AyaGit_Task1", node=node, pose=POSES["A"], location_name="A", logger=logger)
    go_to_A_task2 = Navigate(name="AyaGit_Task2", node=node, pose=POSES["A"], location_name="A", logger=logger)
    go_to_B_task2 = Navigate(name="ByeGit_Task2", node=node, pose=POSES["B"], location_name="B", logger=logger)
    go_to_A_task3 = Navigate(name="AyaGit_Task3", node=node, pose=POSES["A"], location_name="A", logger=logger)
    go_to_B_task3 = Navigate(name="ByeGit_Task3", node=node, pose=POSES["B"], location_name="B", logger=logger)
    go_to_C_task3 = Navigate(name="CyeGit_Task3", node=node, pose=POSES["C"], location_name="C", logger=logger)
    
    wait_charge = Wait(name="ŞarjBekle", wait_time=10.0)
    wait_task1 = Wait(name="Task1Bekle", wait_time=2.0)
    wait_task2_A = Wait(name="Task2ABekle", wait_time=2.0)
    wait_task2_B = Wait(name="Task2BBekle", wait_time=2.0)
    wait_task3_A = Wait(name="Task3ABekle", wait_time=2.0)
    wait_task3_B = Wait(name="Task3BBekle", wait_time=2.0)
    wait_task3_C = Wait(name="Task3CBekle", wait_time=2.0)
    
    background_tasks = CommandSubscriber(name="KomutDinleyici", node=node)
    
    main_logic = py_trees.composites.Selector(name="Ana Mantık", memory=False)

    emergency_charge = py_trees.composites.Sequence(name="AcilŞarj", memory=True)
    emergency_charge.add_children([
        BatteryMonitor(name="BataryaKontrol"),
        go_to_sarj,
        wait_charge,
        ClearCommand(name="ŞarjKomutunuTemizle")
    ])

    task1_sequence = py_trees.composites.Sequence(name="Task1", memory=True)
    task1_sequence.add_children([
        CheckForCommand(name="task1KomutuVarMi?", expected_command="task1"),
        go_to_A_task1,
        wait_task1,
        ClearCommand(name="Task1KomutunuTemizle")
    ])

    task2_sequence = py_trees.composites.Sequence(name="Task2", memory=True)
    task2_sequence.add_children([
        CheckForCommand(name="task2KomutuVarMi?", expected_command="task2"),
        go_to_A_task2,
        wait_task2_A,
        go_to_B_task2,
        wait_task2_B,
        ClearCommand(name="Task2KomutunuTemizle")
    ])

    task3_sequence = py_trees.composites.Sequence(name="Task3", memory=True)
    task3_sequence.add_children([
        CheckForCommand(name="task3KomutuVarMi?", expected_command="task3"),
        go_to_A_task3,
        wait_task3_A,
        go_to_B_task3,
        wait_task3_B,
        go_to_C_task3,
        wait_task3_C,
        ClearCommand(name="Task3KomutunuTemizle")
    ])

    return_to_idle_sequence = py_trees.composites.Sequence(name="Idle'aDön", memory=True)
    return_to_idle_sequence.add_children([
        CheckLocation(name="idledaMi?", location="idle"),
        go_to_idle
    ])

    idle = py_trees.behaviours.Running(name="Bosta")

    main_logic.add_children([
        emergency_charge,
        task1_sequence,
        task2_sequence, 
        task3_sequence,
        return_to_idle_sequence,
        idle
    ])
    
    root.add_children([background_tasks, main_logic])
    
    py_trees.blackboard.Blackboard().set("robot_location", "baslangic")
    py_trees.blackboard.Blackboard().set("last_command", None)
    py_trees.blackboard.Blackboard().set("battery_low", False)
    py_trees.blackboard.Blackboard().set("failed_task", None)

    return root
import py_trees
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String
from rclpy.action.client import ClientGoalHandle
import logging 
import time

# ==============================================================================
#  TEMEL DAVRANIŞLAR
# ==============================================================================
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
        self.timeout_seconds = 300.0  # 5 dakika timeout
        self.max_retries = 5  # 5 kez retry
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
            
            if status == 4:  # SUCCEEDED
                self.final_status = py_trees.common.Status.SUCCESS
                self.logger.info(f"[{self.name}] Navigasyon başarılı!")
            elif status == 5:  # CANCELED
                self.logger.warning(f"[{self.name}] Görev iptal edildi.")
                self.final_status = py_trees.common.Status.FAILURE
            elif status == 6:  # ABORTED
                self.logger.warning(f"[{self.name}] Görev iptal edildi (ABORTED).")
                self.final_status = py_trees.common.Status.FAILURE
            else:
                self.logger.error(f"[{self.name}] Navigasyon başarısız oldu. Durum: {status}")
                self.final_status = py_trees.common.Status.FAILURE
                
        except Exception as e:
            self.logger.error(f"[{self.name}] Sonuç alınırken hata oluştu: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def update(self) -> py_trees.common.Status:
        # Timeout kontrolü
        if self.start_time and time.time() - self.start_time > self.timeout_seconds:
            self.logger.warning(f"[{self.name}] Timeout! {self.timeout_seconds} saniye geçti.")
            if self.goal_handle:
                self.goal_handle.cancel_goal_async()
            self.final_status = py_trees.common.Status.FAILURE
        
        # Retry mekanizması - sadece gerçek hatalarda çalışsın
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
            # Başarısız görevi blackboard'a kaydet
            current_command = self.blackboard.get("last_command")
            if current_command:
                self.blackboard.set("failed_task", current_command)
                self.logger.warning(f"[{self.name}] Görev başarısız, yeniden denenecek: {current_command}")
        
        # Reset state
        self.goal_handle = None
        self.final_status = None
        self.start_time = None
        self.is_initialized = False
        self.retry_count = 0

class Wait(py_trees.behaviour.Behaviour):
    """Belirtilen süre kadar bekleyen davranış"""
    def __init__(self, name: str, wait_time: float):
        super().__init__(name)
        self.wait_time = wait_time
        self.start_time = None

    def initialise(self):
        self.start_time = time.time()
        print(f"[{self.name}] {self.wait_time} saniye bekleniyor...")

    def update(self) -> py_trees.common.Status:
        if time.time() - self.start_time >= self.wait_time:
            print(f"[{self.name}] Bekleme tamamlandı!")
            return py_trees.common.Status.SUCCESS
        return py_trees.common.Status.RUNNING

class CheckForCommand(py_trees.behaviour.Behaviour):
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
    """Komutu temizleyen davranış"""
    def __init__(self, name: str = "Komutu Temizle"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        self.blackboard.set("last_command", None)
        print("Görev tamamlandı, komut temizlendi.")
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
        self.node.get_logger().info(f"Yeni komut alındı: '{msg.data}'")
        self.blackboard.set("last_command", msg.data)

    def update(self) -> py_trees.common.Status:
        return py_trees.common.Status.SUCCESS

class BatteryManager(py_trees.behaviour.Behaviour):
    """Şarj yönetimi davranışı"""
    def __init__(self, name: str = "Şarj Yöneticisi"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()
        self.battery_level = 100.0
        self.last_update = time.time()
        self.charging = False
        self.charge_start_time = None

    def update(self) -> py_trees.common.Status:
        current_time = time.time()
        
        # Şarj istasyonunda mı kontrol et
        current_location = self.blackboard.get("robot_location")
        if current_location == "sarj":
            if not self.charging:
                self.charging = True
                self.charge_start_time = current_time
                print(f"[{self.name}] Şarj başladı...")
            
            # 20 saniye şarj ol
            if current_time - self.charge_start_time >= 20.0:
                self.battery_level = 100.0
                self.charging = False
                print(f"[{self.name}] Şarj tamamlandı! Batarya: %{self.battery_level}")
                return py_trees.common.Status.SUCCESS
                
            return py_trees.common.Status.RUNNING
        else:
            self.charging = False
            self.charge_start_time = None
        
        # Şarj istasyonunda değilse batarya azalır (120 saniyede)
        if current_time - self.last_update >= 120.0:
            self.battery_level -= 20.0  # 120 saniyede %20 azalır
            self.last_update = current_time
            print(f"[{self.name}] Batarya azaldı: %{self.battery_level}")
        
        # Batarya kritik seviyede mi?
        if self.battery_level <= 20.0:
            print(f"[{self.name}] Batarya kritik! Şarj istasyonuna gidiliyor...")
            self.blackboard.set("battery_low", True)
            return py_trees.common.Status.FAILURE
        
        self.blackboard.set("battery_low", False)
        return py_trees.common.Status.SUCCESS

class ReturnToIdle(py_trees.behaviour.Behaviour):
    """Görev tamamlandığında idle'a dönen davranış"""
    def __init__(self, name: str = "Idle'a Dön"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        current_location = self.blackboard.get("robot_location")
        if current_location == "idle":
            print(f"[{self.name}] Zaten idle konumundayız.")
            return py_trees.common.Status.SUCCESS
        else:
            print(f"[{self.name}] Idle konumuna dönülüyor...")
            # Bu davranış Navigate davranışı ile birlikte kullanılacak
            return py_trees.common.Status.RUNNING

# ==============================================================================
#  DAVRANIŞ AĞACI OLUŞTURMA
# ==============================================================================
def create_service_robot_tree(node: Node, logger: logging.Logger) -> py_trees.behaviour.Behaviour:
    
    # Yeni konumlar: sarj(x=0), idle(x=1), A(x=2), B(x=3), C(x=4)
    POSES = {
        "sarj": {'x': 0.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        "idle": {'x': 1.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        "A": {'x': 2.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        "B": {'x': 3.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        "C": {'x': 4.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
    }

    root = py_trees.composites.Parallel(
        name="Servis Robotu",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )

    # Navigasyon davranışları
    go_to_sarj = Navigate(name="sarjaGit", node=node, pose=POSES["sarj"], location_name="sarj", logger=logger)
    go_to_idle = Navigate(name="idleaGit", node=node, pose=POSES["idle"], location_name="idle", logger=logger)
    go_to_A = Navigate(name="AyaGit", node=node, pose=POSES["A"], location_name="A", logger=logger)
    go_to_B = Navigate(name="ByeGit", node=node, pose=POSES["B"], location_name="B", logger=logger)
    go_to_C = Navigate(name="CyeGit", node=node, pose=POSES["C"], location_name="C", logger=logger)
    
    # Bekleme davranışları
    wait_2sec = Wait(name="2SaniyeBekle", wait_time=2.0)
    
    # Diğer davranışlar
    background_tasks = CommandSubscriber(name="KomutDinleyici", node=node)
    battery_manager = BatteryManager(name="ŞarjYöneticisi")
    
    main_logic = py_trees.composites.Selector(name="Ana Mantık", memory=False)

    # ==============================================================================
    # GÖREV SIRALARI (SEKANSLAR)
    # ==============================================================================

    # 1. Öncelik: Şarj düşükse şarj istasyonuna git
    charge_sequence = py_trees.composites.Sequence(name="ŞarjEt", memory=True)
    charge_sequence.add_children([
        py_trees.decorators.FailureIsSuccess(name="BataryaKontrol", child=battery_manager),
        CheckLocation(name="sarjtaMi?", location="sarj"),
        go_to_sarj,
        wait_2sec,  # Şarj için bekle
        ClearCommand(name="ŞarjKomutunuTemizle")
    ])

    # 2. Öncelik: Task1 - A'ya git ve 2 saniye bekle
    task1_sequence = py_trees.composites.Sequence(name="Task1", memory=True)
    task1_sequence.add_children([
        CheckForCommand(name="task1KomutuVarMi?", expected_command="task1"),
        go_to_A,
        wait_2sec,
        ClearCommand(name="Task1KomutunuTemizle")
    ])

    # 3. Öncelik: Task2 - A'ya git, B'ye git, 2'şer saniye bekle
    task2_sequence = py_trees.composites.Sequence(name="Task2", memory=True)
    task2_sequence.add_children([
        CheckForCommand(name="task2KomutuVarMi?", expected_command="task2"),
        go_to_A,
        wait_2sec,
        go_to_B,
        wait_2sec,
        ClearCommand(name="Task2KomutunuTemizle")
    ])

    # 4. Öncelik: Task3 - A'ya git, B'ye git, C'ye git, 2'şer saniye bekle
    task3_sequence = py_trees.composites.Sequence(name="Task3", memory=True)
    task3_sequence.add_children([
        CheckForCommand(name="task3KomutuVarMi?", expected_command="task3"),
        go_to_A,
        wait_2sec,
        go_to_B,
        wait_2sec,
        go_to_C,
        wait_2sec,
        ClearCommand(name="Task3KomutunuTemizle")
    ])

    # 5. Öncelik: Görev tamamlandıysa idle'a dön
    return_to_idle_sequence = py_trees.composites.Sequence(name="Idle'aDön", memory=True)
    return_to_idle_sequence.add_children([
        py_trees.decorators.SuccessIsFailure(name="GörevVarMi?", child=CheckForCommand(name="HerhangiGörevVarMi?", expected_command="task1")),
        py_trees.decorators.SuccessIsFailure(name="GörevVarMi2?", child=CheckForCommand(name="HerhangiGörevVarMi2?", expected_command="task2")),
        py_trees.decorators.SuccessIsFailure(name="GörevVarMi3?", child=CheckForCommand(name="HerhangiGörevVarMi3?", expected_command="task3")),
        CheckLocation(name="idledaMi?", location="idle"),
        go_to_idle
    ])

    # 6. Öncelik: Hiçbir görev yoksa bekle
    idle = py_trees.behaviours.Running(name="Bosta")

    main_logic.add_children([
        charge_sequence,
        task1_sequence,
        task2_sequence, 
        task3_sequence,
        return_to_idle_sequence,
        idle
    ])
    
    root.add_children([background_tasks, battery_manager, main_logic])
    
    # Başlangıç değerlerini ayarlama
    py_trees.blackboard.Blackboard().set("robot_location", "sarj")  # Başlangıçta şarj istasyonunda
    py_trees.blackboard.Blackboard().set("last_command", None)
    py_trees.blackboard.Blackboard().set("battery_low", False)

    return root
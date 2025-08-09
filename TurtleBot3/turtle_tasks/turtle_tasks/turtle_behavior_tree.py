import py_trees
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import String
from rclpy.action.client import ClientGoalHandle
import logging 

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

    def setup(self, **kwargs):
        self.logger.info(f"[{self.name}] Kurulum yapılıyor...")
        if not self.client.wait_for_server(timeout_sec=5.0):
            self.logger.error(f"[{self.name}] Navigasyon sunucusu bulunamadı!")
            self.final_status = py_trees.common.Status.FAILURE

    def initialise(self):
        if self.final_status == py_trees.common.Status.FAILURE:
            return

        self.logger.info(f"[{self.name}] {self.location_name} konumuna gidiliyor. Hedef: {self.pose}")
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = "map"
        goal_msg.pose.header.stamp = self.node.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = self.pose['x']
        goal_msg.pose.pose.position.y = self.pose['y']
        goal_msg.pose.pose.orientation.z = self.pose['oz']
        goal_msg.pose.pose.orientation.w = self.pose['ow']
        send_goal_future = self.client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle or not self.goal_handle.accepted:
            self.logger.error(f"[{self.name}] Hedef reddedildi.")
            self.final_status = py_trees.common.Status.FAILURE
            return
        
        self.logger.info(f"[{self.name}] Hedef kabul edildi, sonuç bekleniyor...")
        get_result_future = self.goal_handle.get_result_async()
        get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        try:
            result = future.result()
            status = result.status
            self.logger.info(f"[{self.name}] Navigasyon sonucu geldi. Durum Kodu: {status}")
            if status == 4: # SUCCEEDED
                self.final_status = py_trees.common.Status.SUCCESS
            elif status == 5: # CANCELED
                self.logger.warn(f"[{self.name}] Görev iptal edildi.")
                self.final_status = py_trees.common.Status.FAILURE
            else:
                self.logger.error(f"[{self.name}] Navigasyon başarısız oldu. Durum: {status}")
                self.final_status = py_trees.common.Status.FAILURE
        except Exception as e:
            self.logger.error(f"[{self.name}] Sonuç alınırken hata oluştu: {e}")
            self.final_status = py_trees.common.Status.FAILURE

    def update(self) -> py_trees.common.Status:
        if self.final_status:
            return self.final_status
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status: py_trees.common.Status):
        current_location = self.blackboard.get("robot_location")
        self.logger.info(f"[{self.name}] Sonlandırılıyor. Önceki konum: '{current_location}', Yeni durum: {new_status.name}")
        if self.goal_handle and self.final_status is None:
            self.logger.warn(f"[{self.name}] Yeni bir komut nedeniyle görev iptal ediliyor...")
            self.goal_handle.cancel_goal_async()

        if new_status == py_trees.common.Status.SUCCESS:
            self.blackboard.set("robot_location", self.location_name)
            self.logger.info(f"[{self.name}] Başarıyla ulaşıldı. Yeni konum karatahtaya yazıldı: {self.location_name}")
        
        self.goal_handle = None
        self.final_status = None


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
    
    # --- DEĞİŞİKLİK: BU DAVRANIŞ ARTIK KOMUTU SİLMİYOR ---
    # terminate metodu kaldırıldı.

# --- YENİ DAVRANIŞ ---
class ClearCommand(py_trees.behaviour.Behaviour):
    """
    Bu davranış çalıştığı anda karatahtadaki 'last_command' değişkenini temizler.
    Sekansların en sonuna eklenerek tüm görevin başarıyla bittiğinden emin olunur.
    """
    def __init__(self, name: str = "Komutu Temizle"):
        super().__init__(name)
        self.blackboard = py_trees.blackboard.Blackboard()

    def update(self) -> py_trees.common.Status:
        self.blackboard.set("last_command", None)
        self.logger.info("Görev tamamlandı, komut temizlendi.")
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

# ==============================================================================
#  DAVRANIŞ AĞACI OLUŞTURMA
# ==============================================================================
# turtle_behavior_tree.py dosyasındaki YALNIZCA create_service_robot_tree fonksiyonunu güncelleyin

def create_service_robot_tree(node: Node, logger: logging.Logger) -> py_trees.behaviour.Behaviour:
    
    POSES = {
        "sarj":          {'x': 1.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        "task_1":          {'x': 2.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
        "idle": {'x': 3.0, 'y': 0.0, 'oz': 0.0, 'ow': 1.000},
    }

    root = py_trees.composites.Parallel(
        name="Servis Robotu",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll()
    )

    # Davranışlar bir kez burada oluşturulur ve yeniden kullanılır
    go_to_kitchen_nav = Navigate(name="sarjaNavigasyon", node=node, pose=POSES["sarj"], location_name="sarj", logger=logger)
    go_to_table1_nav = Navigate(name="task1eGit", node=node, pose=POSES["task_1"], location_name="task_1", logger=logger)
    go_to_wait_point_nav = Navigate(name="idlenaGit", node=node, pose=POSES["idle"], location_name="idle", logger=logger)
    
    # DİKKAT: Paylaşılan 'clear_command_behaviour' nesnesi buradan kaldırıldı.

    background_tasks = CommandSubscriber(name="KomutDinleyici", node=node)
    main_logic = py_trees.composites.Selector(name="Ana Mantık", memory=False)

    # ==============================================================================
    # GÖREV SIRALARI (SEKANSLAR)
    # ==============================================================================

    # 1. Öncelik: taskdan idle noktasına dönme
    return_to_wait_point_seq = py_trees.composites.Sequence(name="idlenaDon", memory=True)
    return_to_wait_point_seq.add_children([
        CheckLocation(name="taskdaMi?", location="task_1"),
        CheckForCommand(name="taskTamamlandiMi", expected_command="idle"),
        go_to_wait_point_nav,
        ClearCommand(name="KomutuTemizle_1") # DÜZELTME: Yeni bir nesne oluşturuluyor
    ])

    # 2. Öncelik: task'a gitme (SADECE sarjtaysa)
    go_to_table_seq = py_trees.composites.Sequence(name="task'aGit", memory=True)
    go_to_table_seq.add_children([
        CheckLocation(name="sarjtaMi?", location="sarj"),
        CheckForCommand(name="taskSecildiMi?", expected_command="task_1"),
        go_to_table1_nav,
        ClearCommand(name="KomutuTemizle_2") # DÜZELTME: Yeni bir nesne oluşturuluyor
    ])

    # 3. Öncelik: sarj çağrısına uyma (SADECE idle noktasındaysa veya başlangıçtaysa)
    is_at_start_or_wait_point = py_trees.composites.Selector(name="BaslangictaVeyaidledeMi?", memory=False)
    is_at_start_or_wait_point.add_children([
        CheckLocation(name="idlendaMi?", location="idle"),
        CheckLocation(name="BaslangicKonumundaMi?", location="initial")
    ])

    go_to_kitchen_seq = py_trees.composites.Sequence(name="sarjaGit", memory=True)
    go_to_kitchen_seq.add_children([
        is_at_start_or_wait_point,
        CheckForCommand(name="sarjCagrisiVarMi?", expected_command="sarj"),
        go_to_kitchen_nav,
        ClearCommand(name="KomutuTemizle_3") # DÜZELTME: Yeni bir nesne oluşturuluyor
    ])

    # 4. Öncelik: Hiçbir görev yoksa bekle
    idle = py_trees.behaviours.Running(name="Bosta")

    main_logic.add_children([return_to_wait_point_seq, go_to_table_seq, go_to_kitchen_seq, idle])
    root.add_children([background_tasks, main_logic])
    
    # Başlangıç değerlerini ayarlama
    py_trees.blackboard.Blackboard().set("robot_location", "initial")
    py_trees.blackboard.Blackboard().set("last_command", None)

    return root
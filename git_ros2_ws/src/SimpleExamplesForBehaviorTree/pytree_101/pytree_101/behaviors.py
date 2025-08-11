import py_trees

class BaseBehaviour(py_trees.behaviour.Behaviour):
    def __init__(self, node, name, prompt, valid_inputs, success_inputs):
        super().__init__(name)
        self.node = node
        self.prompt = prompt
        self.valid_inputs = valid_inputs
        self.success_inputs = success_inputs
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(f"{name.lower()}_secenek", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("end_program", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("timeout", access=py_trees.common.Access.READ)
        self.blackboard.register_key("remaining_time", access=py_trees.common.Access.READ)

    def update(self):
        from main import get_input_with_timeout
        try:
            end_program = self.blackboard.get("end_program") if self.blackboard.exists("end_program") else False
            timeout = self.blackboard.get("timeout") if self.blackboard.exists("timeout") else False
            if end_program or timeout:
                self.node.get_logger().warn(f"Zaman aşımı veya son: {self.name} davranışı başarısız")
                return py_trees.common.Status.FAILURE
            interactive = self.node.get_parameter("interactive").get_parameter_value().bool_value
            if not interactive:
                self.node.get_logger().warn("Terminal interaktif değil, giriş beklenemez")
                # Allow continuation for testing
            remaining_time = self.blackboard.get("remaining_time") if self.blackboard.exists("remaining_time") else 0.0
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE
            secenek = get_input_with_timeout(self.prompt, remaining_time) if interactive else None
            if secenek is None or timeout:
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
                self.blackboard.set("end_program", True)
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
        self.prompt = " uyumak için 'u', dinlenmek için 'd', spor için 's', çalışmak için 'c', uyanmak için 'k', son için 'e': "
        self.valid_inputs = [ 'u', 'd', 's', 'c', 'k', 'e']
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key("end_program", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("timeout", access=py_trees.common.Access.READ)
        self.blackboard.register_key("remaining_time", access=py_trees.common.Access.READ)

    def update(self):
        from main import get_input_with_timeout
        try:
            end_program = self.blackboard.get("end_program") if self.blackboard.exists("end_program") else False
            timeout = self.blackboard.get("timeout") if self.blackboard.exists("timeout") else False
            if end_program or timeout:
                self.node.get_logger().warn("Zaman aşımı veya son: Idle davranışı başarısız")
                return py_trees.common.Status.FAILURE
            interactive = self.node.get_parameter("interactive").get_parameter_value().bool_value
            if not interactive:
                self.node.get_logger().warn("Terminal interaktif değil, giriş beklenemez")
                # Allow continuation for testing
            remaining_time = self.blackboard.get("remaining_time") if self.blackboard.exists("remaining_time") else 0.0
            if remaining_time <= 0:
                return py_trees.common.Status.FAILURE
            secenek = get_input_with_timeout(self.prompt, remaining_time) if interactive else None
            if secenek is None or timeout:
                return py_trees.common.Status.FAILURE
            self.blackboard.idle_secenek = secenek
            if secenek in ['u', 'd', 's', 'c', 'k']:
                self.node.get_logger().info(f"{secenek} durumuna geçiliyor...")
                return py_trees.common.Status.FAILURE
            elif secenek == 'e':
                self.node.get_logger().info("Program sonlandırılıyor...")
                self.blackboard.set("end_program", True)
                return py_trees.common.Status.FAILURE
            else:
                self.node.get_logger().warn("Geçersiz giriş! 'u', 'd', 's', 'c', 'k' veya 'e' girin")
                return py_trees.common.Status.RUNNING
        except Exception as e:
            self.node.get_logger().error(f"Hata in Idle: {str(e)}")
            return py_trees.common.Status.FAILURE
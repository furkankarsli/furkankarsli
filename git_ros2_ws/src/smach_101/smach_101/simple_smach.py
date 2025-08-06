import smach
import rclpy
from rclpy.node import Node
import smach_ros
import time


class UyanState(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['kalk', 'geriYat', 'idle'])
        self.node = node

    def execute(self, ud):
        self.node.get_logger().info("Uyandınız")
        secenek = input("kalkmak k, yatmak y, idle için 'i' yazınız: ").lower()
        return 'kalk' if secenek == 'k' else 'idle' if secenek == 'i' else 'geriYat'


class KalkState(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['geriYat', 'kahvalti', 'idle'])
        self.node = node

    def execute(self, ud):
        self.node.get_logger().info("kalktınız")
        secenek = input("Kahvaltı için 'k', geri yatmak için 'y' , ,idle için i yazınız: ").lower()
        return 'kahvalti' if secenek == 'k' else 'idle' if secenek == 'i' else 'geriYat'


class KahvaltiState(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['geriYat', 'idle'])
        self.node = node

    def execute(self, ud):
        self.node.get_logger().info("kahvaltıdasınız")
        secenek = input("geriyatmak için y, idle için i...").lower()
        return 'geriYat' if secenek == 'y' else 'idle'


class IdleState(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['kalk', 'son', 'kahvalti', 'geriYat'])
        self.node = node

    def execute(self, ud):
        self.node.get_logger().info("idle durumundasınız, sıradaki görevi bekleyiniz")
        secenek = input("kalkmak için k,kahvaltı yapmak için e, programı sonlandırmak için s, yatmak için y'ye basınız...").lower()
        return 'kalk' if secenek == 'k' else 'kahvalti' if secenek == 'e' else 'son' if secenek == 's' else 'geriYat'


class GeriYatState(smach.State):
    def __init__(self, node):
        super().__init__(outcomes=['uyan', 'son'])
        self.node = node

    def execute(self, ud):
        self.node.get_logger().info("Uyudunuz")
        for i in [2, 1]:
            time.sleep(1)
            print(i)
        secenek = input("Programı sonlandırmak için s ,devam etmek için enter'a basınız...").lower()
        return 'son' if secenek == 's' else 'uyan'


class TimerState(smach.State):
    def __init__(self, node, duration=3):
        super().__init__(outcomes=['son'])
        self.node = node
        self.duration = duration

    def execute(self, ud):
        self.node.get_logger().info(f"Smach başladı. {self.duration} saniye sonra otomatik olarak sonlanacak.")
        time.sleep(self.duration)
        self.node.get_logger().info("Zamanlayıcı süresi doldu! Smach otomatik olarak sonlanıyor.")
        return 'son'


class SmachNode(Node):
    def __init__(self):
        super().__init__('smach_node')

        self.sm_top = smach.StateMachine(outcomes=['son'])

        with self.sm_top:
            concurrence_sm = smach.Concurrence(
                outcomes=['timeout_reached', 'main_flow_finished'],
                default_outcome='timeout_reached',
                outcome_map={
                    'timeout_reached': {'TIMER_STATE': 'son'},  # TIMER_STATE 'son' çıktısı verdiğinde timeout_reached olur
                    'main_flow_finished': {'MAIN_FLOW': 'son'} # MAIN_FLOW 'son' çıktısı verdiğinde main_flow_finished olur
                },
                child_termination_cb=lambda outcome_map: True
            )

            with concurrence_sm:
                sm_main_flow = smach.StateMachine(outcomes=['son'])
                with sm_main_flow:
                    smach.StateMachine.add('UYAN', UyanState(self),
                                           transitions={'kalk': 'KALK',
                                                        'geriYat': 'GERI_YAT',
                                                        'idle': 'IDLE'})

                    smach.StateMachine.add('KALK', KalkState(self),
                                           transitions={'kahvalti': 'KAHVALTI',
                                                        'geriYat': 'GERI_YAT',
                                                        'idle': 'IDLE'})

                    smach.StateMachine.add('KAHVALTI', KahvaltiState(self),
                                           transitions={'geriYat': 'GERI_YAT',
                                                        'idle': 'IDLE'})

                    smach.StateMachine.add('GERI_YAT', GeriYatState(self),
                                           transitions={'uyan': 'UYAN',
                                                        'son': 'son'})

                    smach.StateMachine.add('IDLE', IdleState(self),
                                           transitions={'kalk': 'KALK',
                                                        'geriYat': 'GERI_YAT',
                                                        'son': 'son',
                                                        'kahvalti': 'KAHVALTI'})

                smach.Concurrence.add('MAIN_FLOW', sm_main_flow)
                smach.Concurrence.add('TIMER_STATE', TimerState(self, duration=20)) # TimerState'i 20 saniye ile başlatıyoruz

            smach.StateMachine.add('CONCURRENT_MANAGER', concurrence_sm,
                                   transitions={'timeout_reached': 'son',
                                                'main_flow_finished': 'son'})
        
        # SIS başlatma ve yürütme döngüsünü dışarı taşıyoruz
        self.sis = smach_ros.IntrospectionServer('smach_server', self.sm_top, '/SMACH')
        self.sis.start()
        
        outcome = self.sm_top.execute()
        
        self.get_logger().info(f"Durum makinesi tamamlandı: {outcome}")
        self.sis.stop()
        


def main(args=None):
    rclpy.init(args=args)
    node = SmachNode()
    rclpy.shutdown()
    


if __name__ == '__main__':
    main()
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import time

class CleanAreaService(Node):
    def __init__(self):
        super().__init__('clean_area_service')
        self.srv = self.create_service(Trigger, 'clean_area', self.clean_callback)
        self.get_logger().info('🧹 CleanArea Service başlatıldı.')

    def clean_callback(self, request, response):
        self.get_logger().info('🧹 Temizlik görevi başlatıldı...')
        
        # Temizlik simülasyonu (40 saniye)
        for i in range(40):
            progress = int((i + 1) / 40 * 100)
            self.get_logger().info(f'🧹 Temizlik ilerlemesi: %{progress}')
            time.sleep(1)
        
        self.get_logger().info('✅ Temizlik tamamlandı!')
        response.success = True
        response.message = "Temizlik başarıyla tamamlandı"
        return response

def main(args=None):
    rclpy.init(args=args)
    service = CleanAreaService()
    rclpy.spin(service)
    service.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
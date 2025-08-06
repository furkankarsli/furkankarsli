ÇALIŞTIRMA KOMUTLARı

cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select smach_101 pytree_101 behaviortree_101
source ~/ros2_ws/install/setup.bash

SMACH
ros2 run smach_101 smach_example
Farklı terminalde: ros2 topic echo /smach_server/smach/container_status

PY_TREES
python3 src/pytree_101/pytree_101/main.py

BEHAVIOR TREE
ros2 run behaviortree_101 bt_node


IÇERIKLERI-ANLAM

Tüm bu paketlerin asıl amacı robotlar için Behavior Tree kullanmayı öğrenmektir. Behavior tree, bir robotun durumlar arası geçişini en sağlıklı şekilde yönetebilen bir kütüphanedir.
Ancak zaman yetersizliği sebebiyle Behavior Tree öğrenimi durdurulup py_trees üzerinde ilerlenmeye karar verilmiştir.
Py_tree, behavior tree'den programlama dili ve ağaç yapısı bakımından farklıdır. 




### pytree_101 Projenin Çalışma Mimarisi

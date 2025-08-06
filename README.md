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

Bu örnek, `py_trees` uygulamasını daha yönetilebilir ve okunabilir hale getirmek için üç ana dosyaya ayrılmıştır. Her dosyanın net bir sorumluluğu vardır:

* **`main.py` (Yönetici/Çalıştırıcı):**
    * Uygulamanın ana giriş noktasıdır ve ROS 2 düğümünü başlatır.
    * `tree_builder.py` dosyasını çağırarak davranış ağacının tamamını oluşturur.
    * Arka planda bir zamanlayıcı (`TimerThread`) çalıştırarak programın belirli bir süre sonunda kapanmasını sağlar.
    * Davranış ağacını "canlı" tutan ve sürekli çalışmasını sağlayan ana `tick()` döngüsünü yönetir.

* **`tree_builder.py` (Mimar):**
    * Davranış ağacının mantıksal yapısını ve akış şemasını tanımlar.
    * `Selector` ("VEYA" mantığı) ve `Sequence` ("VE" mantığı) gibi kompozit düğümleri kullanarak görevlerin hangi sırayla ve hangi koşullara göre çalışacağını belirler.
    * Örneğin, "Ana Akış" başarısız olursa "Boşta Kalma" (`Idle`) durumuna geçilmesini sağlayan `Selector` yapısı burada kurulur.

* **`behaviors.py` (İşçiler):**
    * Ağacın yapraklarını oluşturan ve asıl işi yapan temel davranış sınıflarını içerir.
    * `BaseBehaviour` sınıfı kullanıcıdan komut istemek, girdiyi işlemek ve görevin başarılı mı (`SUCCESS`) yoksa başarısız mı (`FAILURE`) olduğunu belirlemek gibi görevleri yerine getirir.
    * Buradan dönen sonuç, `tree_builder.py`'de tanımlanan mantıksal akışın hangi yöne devam edeceğini belirler.

#### Basitçe Çalışma Akışı:

1.  `main.py` çalışır, `tree_builder`'dan ağacın planını alır ve ağacı oluşturur.
2.  `main.py` sürekli olarak ağaca "tick" sinyali gönderir.
3.  Sinyal, `tree_builder`'da kurulan yollardan geçerek `behaviors.py` içindeki aktif bir davranışa ulaşır.
4.  Davranış, kullanıcıdan girdi ister ve bir sonuç (`SUCCESS` veya `FAILURE`) döndürür.
5.  Bu sonuç, ağaçta yukarı doğru ilerleyerek bir sonraki "tick"te hangi davranışın çalışması gerektiğine karar verilmesini sağlar.

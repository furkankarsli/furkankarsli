"""çift sinifli ---  Sequence, çocuklarını sırayla çalıştırır """


import py_trees 

class MySimpleBehavior(py_trees.behaviour.Behaviour):
    
    def __init__(self, name="BasitDavranis", ticks_to_success=3):
        super().__init__(name)
        self.ticks_to_success = ticks_to_success
        self.current_tick = 0 
        print(f"[{self.name}] Nesne oluşturuldu.")

    def initialise(self):
        self.current_tick = 0 
        print(f"[{self.name}] Başlatıldı (Initialise edildi). Hedef: {self.ticks_to_success} adım.")

    def update(self):
        self.current_tick += 1 
        
        if self.current_tick <= self.ticks_to_success:
            print(f"[{self.name}] Çalışıyor... (Adım: {self.current_tick}/{self.ticks_to_success})")
            return py_trees.common.Status.RUNNING 
        else:
            print(f"[{self.name}] Görev başarıyla tamamlandı!")
            return py_trees.common.Status.SUCCESS

    def terminate(self, new_status):
        print(f"[{self.name}] Sonlandırıldı.")

# --- İkinci Davranış Sınıfı: InstantSuccessBehavior ---
class InstantSuccessBehavior(py_trees.behaviour.Behaviour):
   
    def __init__(self, name="AnindaBasariliDavranis", message="Görev Tamamlandı!"):
        super().__init__(name)
        self.message = message
        print(f"[{self.name}] Nesne oluşturuldu.")

    def initialise(self):
        # Bu davranışın her başladığında bir kez çağrılır.
        print(f"[{self.name}] Başlatıldı (Initialise edildi).")

    def update(self):
        # Bu davranışın ana mantığı. Mesajı yazdır ve hemen başarılı ol.
        print(f"[{self.name}] Mesaj: '{self.message}' - Hemen başarılı oluyorum.")
        return py_trees.common.Status.SUCCESS # Anında başarı döndürüyoruz

    def terminate(self, new_status):
        # Bu davranış sonlandığında çağrılır.
        print(f"[{self.name}] Sonlandırıldı.")

# --- Ana Fonksiyon ---
def main():
    print("--- PyTree Uygulaması Başlıyor ---")
    
    # İki farklı davranış nesnesi oluşturuyoruz
    behavior1 = MySimpleBehavior(name="BirinciAdim", ticks_to_success=2) # 2 tick sürecek
    behavior2 = InstantSuccessBehavior(name="IkinciAdim", message="Kısa Görev Bitti!") # Hemen bitecek

    # Bir Sequence (Sıra) kompozit düğümü oluşturuyoruz.
    # Sequence, çocuklarını sırayla çalıştırır. Bir çocuk başarılı olursa, sıradakine geçer.
    # memory=True: Davranış, RUNNING durumunda kaldığında, bir sonraki tick'te kaldığı yerden devam eder.
    root_sequence = py_trees.composites.Sequence(name="AnaAkisSiralama", memory=True)
    
    # Davranışlarımızı Sequence düğümüne ekliyoruz.
    # Eklenme sırası önemlidir, çünkü Sequence onları bu sırayla çalıştırmaya çalışır.
    root_sequence.add_children([behavior1, behavior2])

    # Davranış ağacı nesnesini oluştur
    # Kök (root) düğümümüz artık oluşturduğumuz 'root_sequence' olacak.
    tree = py_trees.trees.BehaviourTree(root_sequence)
    

    tree.setup() 
    print(f"\n--- Ağaç Başarıyla Kuruldu. Kök Durum: {tree.root.status} ---") 
    
    print("\n--- Davranış Ağacı Çalışmaya Başlıyor ---")
    
    # İlk 'tick'i manuel olarak yapıyoruz
    # Bu, kök davranışın (Sequence) ve dolayısıyla ilk çocuğunun 'update()' metodunu ilk kez çalıştırır.
    tree.tick() 
    print(f"Ağaç ilk kez 'tick' edildi. Kök durum: {tree.root.status}")
    
    tick_count = 0
    # Kök davranışın durumu 'ÇALIŞIYOR' (RUNNING) olduğu sürece döngüyü devam ettir.
    while tree.root.status == py_trees.common.Status.RUNNING:
        tick_count += 1
        print(f"\n--- Yeni 'Tick' Başladı (Sıra: #{tick_count}) ---")
        # time.sleep(1) # Eğer her tick arasında bekleme istersen bu satırı ekleyebilirsin
        tree.tick() # Ağacı bir adım ileri götürürüz.
        print(f"Ağaç 'tick' edildi. Kök durum: {tree.root.status}")
     
    # Ağaç tamamlandığında (SUCCESS veya FAILURE olduğunda) kapatırız.
    tree.shutdown()
    print("\n--- PyTree Uygulaması Kapatıldı ---")
    print(f"Son Kök Durum: {tree.root.status}") # Son durumu bir kez daha yazdıralım

if __name__ == '__main__':
    main()
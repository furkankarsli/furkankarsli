"""tek sinifli"""


import py_trees 

class MySimpleBehavior(py_trees.behaviour.Behaviour):
    
    def __init__(self, name="BasitDavranis", ticks_to_success=3):
        super(MySimpleBehavior, self).__init__(name)
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

def main():
    print("--- PyTree Uygulaması Başlıyor ---")
    root_behavior = MySimpleBehavior(name="AnaDavranis", ticks_to_success=3)
    tree = py_trees.trees.BehaviourTree(root_behavior)
    tree.setup() 
    print(f"\n--- Ağaç Başarıyla Kuruldu. Kök Durum: {tree.root.status} ---") 
    print("\n--- Davranış Ağacı Çalışmaya Başlıyor ---")
    
    # İlk 'tick'i manuel olarak yapıyoruz
    tree.tick() 
    print(f"Ağaç ilk kez 'tick' edildi. Kök durum: {tree.root.status}")
    
    tick_count = 0
    while tree.root.status == py_trees.common.Status.RUNNING:
        tick_count += 1
        print(f"\n--- Yeni 'Tick' Başladı (Sıra: #{tick_count}) ---")
        # time.sleep(1) # Eğer her tick arasında bekleme istersen bu satırı ekleyebilirsin
        tree.tick() 
        print(f"Ağaç 'tick' edildi. Kök durum: {tree.root.status}")
     
    
    tree.shutdown()
    

if __name__ == '__main__':
    main()
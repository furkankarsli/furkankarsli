import threading
import time
import os
from queue import Queue

# Kullanıcı bilgilerini saklayan sınıf
class DogumBilgileri:
    def __init__(self):
        self.ay = None
        self.yil = None
    
    def bilgi_al(self):
        """Doğum ayı ve yılını kullanıcıdan alır."""
        while True:
            try:
                self.ay = input("Doğum ayınızı girin (1-12): ")
                self.ay = int(self.ay)
                if 1 <= self.ay <= 12:
                    break
                print("Lütfen 1-12 arasında bir sayı girin.")
            except ValueError:
                print("Geçerli bir sayı girin.")
        
        while True:
            try:
                self.yil = input("Doğum yılınızı girin (örn. 1990): ")
                self.yil = int(self.yil)
                if 1900 <= self.yil <= 2025:
                    break
                print("Lütfen 1900-2025 arasında bir yıl girin.")
            except ValueError:
                print("Geçerli bir sayı girin.")
        
        print(f"Doğum bilgileriniz: {self.ay}. ay, {self.yil}")

# Geri sayım için thread fonksiyonu
def geri_sayim(sure_saniye, kuyruk):
    """10 saniyelik geri sayım yapar ve programı kapatır."""
    print("Geri sayım başladı!")
    for i in range(sure_saniye, -1, -1):
        time.sleep(1)
    kuyruk.put("Süre doldu! Program kapanıyor...")
    time.sleep(0.5)
    os._exit(0)  # Programı zorla kapat

# Kullanıcı bilgilerini toplama (Davranış Ağacı Sequence benzeri)
def kullanici_bilgi_toplama(kuyruk):
    """Kullanıcıdan isim, yaş ve doğum bilgilerini alır."""
    # Adım 1: İsim al
    isim = input("İsminizi girin: ").strip()
    if not isim:
        isim = "Bilinmeyen"
    kuyruk.put(f"İsim: {isim}")
    
    # Adım 2: Yaş al
    while True:
        try:
            yas = input("Yaşınızı girin: ")
            yas = int(yas)
            if 0 <= yas <= 120:
                kuyruk.put(f"Yaş: {yas}")
                break
            print("Lütfen 0-120 arasında bir yaş girin.")
        except ValueError:
            print("Geçerli bir sayı girin.")
    
    # Adım 3: Doğum bilgilerini al (sınıf kullanımı)
    dogum = DogumBilgileri()
    dogum.bilgi_al()
    kuyruk.put(f"Doğum: {dogum.ay}. ay, {dogum.yil}")

# Çıktıları yazdırma thread'i (ROS benzeri loglama)
def cikti_yazdir(kuyruk):
    """Kuyruktan mesajları alır ve yazdırır."""
    while True:
        try:
            mesaj = kuyruk.get(timeout=12)  # 12 saniye bekle
            print(mesaj)
            kuyruk.task_done()
        except queue.Empty:
            print("Kuyruk boş, yazdırma thread'i kapanıyor.")
            break

# ROS ve PyTrees benzeri davranış ağacı simülasyonu
def davranis_agaci_simulasyonu(kuyruk):
    """Davranış ağacı benzeri sıralı görev simülasyonu."""
    kuyruk.put("Davranış ağacı simülasyonu başlıyor...")
    # Sequence: Adımlar sırayla çalışır
    kuyruk.put("Adım 1: Kullanıcı bilgileri toplanıyor")
    kullanici_bilgi_toplama(kuyruk)
    kuyruk.put("Adım 2: Bilgiler işlendi, ağaç tamamlandı!")

# Ana fonksiyon
def main():
    # Kuyruk oluştur (ROS benzeri mesajlaşma için)
    kuyruk = Queue()
    
    # Thread'leri oluştur
    geri_sayim_thread = threading.Thread(target=geri_sayim, args=(10, kuyruk))
    cikti_thread = threading.Thread(target=cikti_yazdir, args=(kuyruk,))
    davranis_thread = threading.Thread(target=davranis_agaci_simulasyonu, args=(kuyruk,))
    
    # Thread'leri başlat
    geri_sayim_thread.start()
    cikti_thread.start()
    davranis_thread.start()
    
    # Thread'lerin bitmesini bekle (geri sayım zaten programı kapatacak)
    cikti_thread.join()
    davranis_thread.join()
    geri_sayim_thread.join()

if __name__ == "__main__":
    print("ROS ve PyTrees Tabanlı Geri Sayım Programı")
    print("10 saniye içinde program otomatik kapanacak!")
    main()
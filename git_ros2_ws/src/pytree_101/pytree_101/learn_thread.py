import threading
import time
import queue
from concurrent.futures import ThreadPoolExecutor

# Ortak kaynak
sayac = 0
kilit = threading.Lock()
kuyruk = queue.Queue()

# 1. Basit Thread Oluşturma ve Çalıştırma
def basit_gorev(ad, sure):
    print(f"{ad} başladı (Thread ID: {threading.get_ident()})")
    time.sleep(sure)
    print(f"{ad} bitti")

# 2. Lock ile Senkronizasyon
def sayac_artir(ad, artis_miktari):
    global sayac
    for _ in range(artis_miktari):
        with kilit:
            global sayac
            temp = sayac
            time.sleep(0.01)  # Race condition simülasyonu
            sayac = temp + 1
    print(f"{ad} tamamlandı, sayac: {sayac}")

# 3. Semaphore ile Sınırlı Erişim
semaphore = threading.Semaphore(2)  # Aynı anda 2 thread erişebilir
def kaynak_erisimi(ad):
    with semaphore:
        print(f"{ad} kaynağa erişti")
        time.sleep(1)
        print(f"{ad} kaynağı serbest bıraktı")

# 4. Condition ile Thread'ler Arası İletişim
condition = threading.Condition()
urun_mevcut = False

def uretici():
    global urun_mevcut
    with condition:
        print("Üretici: Ürün üretiyor...")
        time.sleep(1)
        urun_mevcut = True
        print("Üretici: Ürün hazır!")
        condition.notify()  # Tüketiciyi uyandır

def tuketici():
    with condition:
        while not urun_mevcut:
            print("Tüketici: Ürün bekliyor...")
            condition.wait()  # Ürün hazır olana kadar bekle
        print("Tüketici: Ürün tüketildi!")

# 5. Event ile Thread Kontrolü
event = threading.Event()

def bekleyen_gorev(ad):
    print(f"{ad} olay bekliyor...")
    event.wait()  # Olay tetiklenene kadar bekle
    print(f"{ad} olay tetiklendi, devam ediyor!")

def tetikleyici():
    print("Tetikleyici: 2 saniye bekliyor...")
    time.sleep(2)
    print("Tetikleyici: Olayı tetikliyor!")
    event.set()  # Olayı tetikle

# 6. Queue ile Thread-safe Veri Paylaşımı
def uretici_kuyruk():
    for i in range(6,12):
        kuyruk.put(i)
        print(f"Üretici: {i} kuyruğa eklendi")
        time.sleep(0.5)

def tuketici_kuyruk(ad):
    while True:
        try:
            veri = kuyruk.get(timeout=2)  # 2 saniye bekle
            print(f"{ad}: {veri} kuyruktan alındı")
            kuyruk.task_done()
        except queue.Empty:
            print(f"{ad}: Kuyruk boş, çıkıyor!")
            break

# 7. ThreadPoolExecutor ile Thread Havuzu
def havuz_gorev(no):
    print(f"Havuz Görev {no} başladı")
    time.sleep(1)
    return f"Havuz Görev {no} bitti"

# Ana Fonksiyon
def main():
    print("=== 1. Basit Thread Oluşturma ===")
    t1 = threading.Thread(target=basit_gorev, args=("Thread-1", 2))
    t2 = threading.Thread(target=basit_gorev, args=("Thread-2", 1))
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("\n=== 2. Lock ile Senkronizasyon ===")
    t3 = threading.Thread(target=sayac_artir, args=("Thread-3", 100))
    t4 = threading.Thread(target=sayac_artir, args=("Thread-4", 100))
    t3.start()
    t4.start()
    t3.join()
    t4.join()

    print("\n=== 3. Semaphore ile Sınırlı Erişim ===")
    threads = [threading.Thread(target=kaynak_erisimi, args=(f"Thread-{i}",)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("\n=== 4. Condition ile İletişim ===")
    t5 = threading.Thread(target=uretici)
    t6 = threading.Thread(target=tuketici)
    t6.start()
    t5.start()
    t5.join()
    t6.join()

    print("\n=== 5. Event ile Kontrol ===")
    t7 = threading.Thread(target=bekleyen_gorev, args=("Thread-7",))
    t8 = threading.Thread(target=tetikleyici)
    t7.start()
    t8.start()
    t7.join()
    t8.join()

    print("\n=== 6. Queue ile Veri Paylaşımı ===")
    t9 = threading.Thread(target=uretici_kuyruk)
    t10 = threading.Thread(target=tuketici_kuyruk, args=("Tüketici-1",))
    t11 = threading.Thread(target=tuketici_kuyruk, args=("Tüketici-2",))
    t9.start()
    t10.start()
    t11.start()
    t9.join()
    t10.join()
    t11.join()

    print("\n=== 7. ThreadPoolExecutor ile Havuz ===")
    with ThreadPoolExecutor(max_workers=3) as executor:
        sonuclar = executor.map(havuz_gorev, [1, 2, 3, 4])
        for sonuc in sonuclar:
            print(sonuc)

if __name__ == "__main__":
    main()
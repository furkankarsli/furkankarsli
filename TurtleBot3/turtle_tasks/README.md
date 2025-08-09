Pytrees ros ile turtlebot waffle'ı terminalden girilen komutlara ve ağaç yapısına göre otonom hareket ettirme paketidir. 

Başlangıç noktasında "şarj" komutu gelirse robot şarj istasyonuna gider
şarj istasyonunda "task_1" komutu gelirse robot task_1 bölgesine gider
task_1  bölgesinde "idle" komutu gelirse robot idle bölgesine gider
idle bölgesinde "şarj" komutu gelirse robot şarj istasyonuna gider


bu döngü içerisinde uygun komutlar geldikçe robot hareket eder.

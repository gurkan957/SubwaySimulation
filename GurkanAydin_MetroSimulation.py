from collections import defaultdict, deque
import heapq
from typing import Dict, List, Tuple, Optional

# Istasyon sınıfı, her bir metro istasyonunu temsil eder
class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        # İstasyonun benzersiz ID'si, adı ve bağlı olduğu hat bilgisi
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular = [] # Bağlantıdaki komşu istasyonlar (başlangıçta boş)

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        # Bir istasyon ile komşu bağlantısı ekliyoruz
        self.komsular.append((istasyon, sure))

    def __lt__(self, other: 'Istasyon'):
        # İstasyonlar arasında karşılaştırma yapmak için (ID'ye göre)
        return self.idx < other.idx

class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {} # İstasyonların sözlüğü (ID -> Istasyon)
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list) # Hatlar ve onlara bağlı istasyonlar

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        # Yeni bir istasyon eklemek için
        if idx not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon) # İstasyonun bağlı olduğu hat bilgisi ekleniyor

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        # İki istasyon arasındaki bağlantıyı (komşuluğu) ekliyoruz
        istasyon1 = self.istasyonlar.get(istasyon1_id)
        istasyon2 = self.istasyonlar.get(istasyon2_id)
        if istasyon1 and istasyon2:
            istasyon1.komsu_ekle(istasyon2, sure) # Komşu ekleniyor
            istasyon2.komsu_ekle(istasyon1, sure) # Komşu ekleniyor (bağlantı iki yönlü)

    def heuristik(self, istasyon1: Istasyon, hedef_id: str) -> int:
        # A* algoritmasında kullanılacak heuristik (tahmin) fonksiyonu
        # Burada basitçe ID'lerin farkına bakarak bir tahmin değeri döndürüyoruz
        return abs(int(istasyon1.idx[1]) - int(hedef_id[1]))

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        # A* algoritması ile en hızlı rotayı (en kısa mesafeyi) bulma
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None # Başlangıç veya hedef istasyonu ağda yoksa None döner
        # Öncelikli kuyruk (f değeri, toplam süre, mevcut istasyon, rota) ile başlatıyoruz
        pq = [(0 + self.heuristik(self.istasyonlar[baslangic_id], hedef_id), 0, self.istasyonlar[baslangic_id], [self.istasyonlar[baslangic_id]])]
        ziyaret_edildi = {} # Ziyaret edilen istasyonları ve sürelerini tutacak sözlük
        while pq:
            f, toplam_sure, mevcut, rota = heapq.heappop(pq) # Öncelikli kuyruktan eleman çıkar
            if mevcut.idx == hedef_id:
                return (rota, toplam_sure) # Hedefe ulaşıldı, rota ve toplam süreyi döndür
            if mevcut.idx in ziyaret_edildi and ziyaret_edildi[mevcut.idx] <= toplam_sure:
                continue # Bu istasyonu daha hızlı bir şekilde ziyaret ettiysek, devam etme
            ziyaret_edildi[mevcut.idx] = toplam_sure # Bu istasyonu ziyaret ettik ve süreyi kaydettik
            # Komşu istasyonlara geçiyoruz
            for komsu, sure in mevcut.komsular:
                yeni_sure = toplam_sure + sure # Yeni toplam süre
                heapq.heappush(pq, (yeni_sure + self.heuristik(komsu, hedef_id), yeni_sure, komsu, rota + [komsu]))
        return None # Eğer hedefe ulaşılamazsa None döndür

    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        # BFS algoritması ile en az aktarmalı rotayı bulma
        if baslangic_id not in self.istasyonlar or hedef_id not in self.istasyonlar:
            return None # Başlangıç veya hedef istasyonu ağda yoksa None döner
        kuyruk = deque([(self.istasyonlar[baslangic_id], [self.istasyonlar[baslangic_id]])]) # Kuyruğu başlatıyoruz
        ziyaret_edildi = set() # Ziyaret edilen istasyonlar
        while kuyruk:
            mevcut, rota = kuyruk.popleft() # Kuyruğun önünden eleman al
            if mevcut.idx == hedef_id:
                return rota # Hedefe ulaşıldı, rota döndürülüyor
            ziyaret_edildi.add(mevcut.idx) # Bu istasyonu ziyaret ettik
            # Komşu istasyonlara geçiyoruz
            for komsu, _ in mevcut.komsular:
                if komsu.idx not in ziyaret_edildi:
                    kuyruk.append((komsu, rota + [komsu])) # Komşuyu kuyruğa ekle
        return None # Eğer hedefe ulaşılamazsa None döndür

if __name__ == "__main__":
    metro = MetroAgi()

    # İstanbul Metro Hatları
    
    # Kırmızı Hat Hat (Yenikapı - Levent)
    metro.istasyon_ekle("K1", "Yenikapı", "Mavi Hat")
    metro.istasyon_ekle("K2", "Haliç", "Mavi Hat")
    metro.istasyon_ekle("K3", "Taksim", "Mavi Hat")
    metro.istasyon_ekle("K4", "Levent", "Mavi Hat")
    
    # Mavi Hat (Merter - Söğütlüçeşme)
    metro.istasyon_ekle("T1", "Merter", "Turuncu Hat")
    metro.istasyon_ekle("T2", "Zincirlikuyu", "Turuncu Hat")
    metro.istasyon_ekle("T3", "Altunizade", "Turuncu Hat")
    metro.istasyon_ekle("T4", "Söğütlüçeşme", "Turuncu Hat")
    
    # Bağlantılar ekleme
    metro.baglanti_ekle("K1", "K2", 4)
    metro.baglanti_ekle("K2", "K3", 4)
    metro.baglanti_ekle("K3", "K4", 12)
    metro.baglanti_ekle("T1", "T2", 32)
    metro.baglanti_ekle("T2", "T3", 8)
    metro.baglanti_ekle("T3", "T4", 12)

    
    # Hat aktarma bağlantısı
    metro.baglanti_ekle("K1", "T1", 24)

    # Ankara Metro Hatları
    
    # Kırmızı Hat (Kızılay - OSB)
    metro.istasyon_ekle("A1", "Kızılay", "Kırmızı Hat")
    metro.istasyon_ekle("A2", "Ulus", "Kırmızı Hat")
    metro.istasyon_ekle("A3", "Demetevler", "Kırmızı Hat")
    metro.istasyon_ekle("A4", "OSB", "Kırmızı Hat")
    
    # Mavi Hat (AŞTİ - Gar)
    metro.istasyon_ekle("B1", "AŞTİ", "Mavi Hat")
    metro.istasyon_ekle("B2", "Kızılay", "Mavi Hat")
    metro.istasyon_ekle("B3", "Sıhhiye", "Mavi Hat")
    metro.istasyon_ekle("B4", "Gar", "Mavi Hat")
    
    # Turuncu Hat (Batıkent - Keçiören)
    metro.istasyon_ekle("C1", "Batıkent", "Turuncu Hat")
    metro.istasyon_ekle("C2", "Demetevler", "Turuncu Hat")
    metro.istasyon_ekle("C3", "Gar", "Turuncu Hat")
    metro.istasyon_ekle("C4", "Keçiören", "Turuncu Hat")
    
    # Bağlantılar ekleme
    metro.baglanti_ekle("A1", "A2", 4)
    metro.baglanti_ekle("A2", "A3", 6)
    metro.baglanti_ekle("A3", "A4", 8)
    metro.baglanti_ekle("B1", "B2", 5)
    metro.baglanti_ekle("B2", "B3", 3)
    metro.baglanti_ekle("B3", "B4", 4)
    metro.baglanti_ekle("C1", "C2", 7)
    metro.baglanti_ekle("C2", "C3", 9)
    metro.baglanti_ekle("C3", "C4", 5)
    
    # Hat aktarma bağlantıları
    metro.baglanti_ekle("A1", "B2", 2)
    metro.baglanti_ekle("A3", "C2", 3)
    metro.baglanti_ekle("B4", "C3", 2)

    # İstanbul Test Senaryoları
    
    print("\n=== İstanbul Metro Test Senaryoları ===")
    print("\n1. Haliç -> Levent")
    rota = metro.en_az_aktarma_bul("K2", "K4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    sonuc = metro.en_hizli_rota_bul("K2", "K4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n2. Yenikapı -> Söğütlüçeşme")
    rota = metro.en_az_aktarma_bul("K1", "T4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    sonuc = metro.en_hizli_rota_bul("K1", "T4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))
        
    print("\n2. Merter -> Altunizade")
    rota = metro.en_az_aktarma_bul("T1", "T3")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    sonuc = metro.en_hizli_rota_bul("T1", "T3")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    # Ankara Test Senaryoları
    
    print("\n=== Ankara Metro Test Senaryoları ===")
    print("\n3. AŞTİ -> OSB")
    rota = metro.en_az_aktarma_bul("B1", "A4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    sonuc = metro.en_hizli_rota_bul("B1", "A4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n4. Demetevler -> Keçiören")
    rota = metro.en_az_aktarma_bul("C2", "C4")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    sonuc = metro.en_hizli_rota_bul("C2", "C4")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

    print("\n5. Keçiören -> AŞTİ")
    rota = metro.en_az_aktarma_bul("C4", "B1")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(i.ad for i in rota))
    sonuc = metro.en_hizli_rota_bul("C4", "B1")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(i.ad for i in rota))

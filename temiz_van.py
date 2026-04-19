print("Temiz Van Projesi başlıyor!")

sehir = "Van"
sorun = "Çöp kirliliği"

print(f"Şehir: {sehir}")
print(f"Sorun: {sorun}")
print(f"{sehir}'da {sorun} problemini çözmeye çalışıyoruz!")
print("=== Temiz Van - Çöp Şikayet Sistemi ===")
print()

ad = input("Adın nedir? ")
mahalle = input("Hangi mahallede çöp var? ")
aciklama = input("Durumu kısaca anlat: ")

print()
print("--- Şikayetin Kaydedildi ---")
print(f"Bildiren: {ad}")
print(f"Mahalle: {mahalle}")
print(f"Açıklama: {aciklama}")
print("Teşekkürler! Belediyeye iletilecek.")

import datetime

print("=== Temiz Van - Çöp Şikayet Sistemi ===")
print()

ad = input("Adın nedir? ")
mahalle = input("Hangi mahallede çöp var? ")
aciklama = input("Durumu kısaca anlat: ")

zaman = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

sikayet = f"{zaman} | {ad} | {mahalle} | {aciklama}\n"

# Dosyaya kaydet
with open("sikayetler.txt", "a", encoding="utf-8") as dosya:
    dosya.write(sikayet)

print()
print("--- Şikayetin Kaydedildi ---")
print(f"Bildiren: {ad}")
print(f"Mahalle: {mahalle}")
print(f"Açıklama: {aciklama}")
print(f"Zaman: {zaman}")
print("Teşekkürler! Belediyeye iletilecek.")
while True:
    cevap = input("Devam et? (çıkış yaz durdurmak için): ")
    if cevap == "çıkış":
        break
    print("Devam ediyoruz!")
    
    import datetime

def sikayet_al():
    print("\n=== Yeni Şikayet ===")
    ad = input("Adın nedir? ")
    mahalle = input("Hangi mahallede çöp var? ")
    aciklama = input("Durumu kısaca anlat: ")
    zaman = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    sikayet = f"{zaman}|{ad}|{mahalle}|{aciklama}\n"
    
    with open("sikayetler.txt", "a", encoding="utf-8") as dosya:
        dosya.write(sikayet)
    
    print(f"\n✅ Şikayet kaydedildi! ({zaman})")

def sikayetleri_goster():
    print("\n=== Tüm Şikayetler ===")
    try:
        with open("sikayetler.txt", "r", encoding="utf-8") as dosya:
            satirlar = dosya.readlines()
        
        if len(satirlar) == 0:
            print("Henüz şikayet yok.")
            return
        
        print(f"Toplam {len(satirlar)} şikayet bulundu:\n")
        for i, satir in enumerate(satirlar, 1):
            parcalar = satir.strip().split("|")
            print(f"{i}. {parcalar[0]} - {parcalar[2]} ({parcalar[1]})")
            print(f"   📝 {parcalar[3]}")
    
    except FileNotFoundError:
        print("Henüz hiç şikayet kaydedilmemiş.")

def analiz():
    print("\n=== Mahalle Analizi ===")
    try:
        with open("sikayetler.txt", "r", encoding="utf-8") as dosya:
            satirlar = dosya.readlines()
        
        mahalleler = {}
        for satir in satirlar:
            parcalar = satir.strip().split("|")
            mahalle = parcalar[2]
            if mahalle in mahalleler:
                mahalleler[mahalle] += 1
            else:
                mahalleler[mahalle] = 1
        
        for mahalle, sayi in sorted(mahalleler.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mahalle}: {sayi} şikayet")
    
    except FileNotFoundError:
        print("Henüz veri yok.")

# Ana menü
while True:
    print("\n=== Temiz Van Sistemi ===")
    print("1 - Yeni şikayet ekle")
    print("2 - Şikayetleri gör")
    print("3 - Mahalle analizi")
    print("4 - Çıkış")
    
    secim = input("\nSeçimin: ")
    
    if secim == "1":
        sikayet_al()
    elif secim == "2":
        sikayetleri_goster()
    elif secim == "3":
        analiz()
    elif secim == "4":
        print("Görüşürüz!")
        break
    else:
        print("Geçersiz seçim!"),
        
        import datetime

def sikayet_al():
    print("\n=== Yeni Şikayet ===")
    ad = input("Adın nedir? ")
    mahalle = input("Hangi mahallede çöp var? ")
    aciklama = input("Durumu kısaca anlat: ")
    zaman = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    sikayet = f"{zaman}|{ad}|{mahalle}|{aciklama}\n"
    
    with open("sikayetler.txt", "a", encoding="utf-8") as dosya:
        dosya.write(sikayet)
    
    print(f"\n✅ Şikayet kaydedildi! ({zaman})")

def sikayetleri_goster():
    print("\n=== Tüm Şikayetler ===")
    try:
        with open("sikayetler.txt", "r", encoding="utf-8") as dosya:
            satirlar = dosya.readlines()
        
        if len(satirlar) == 0:
            print("Henüz şikayet yok.")
            return
        
        print(f"Toplam {len(satirlar)} şikayet bulundu:\n")
        for i, satir in enumerate(satirlar, 1):
            parcalar = satir.strip().split("|")
            print(f"{i}. {parcalar[0]} - {parcalar[2]} ({parcalar[1]})")
            print(f"   📝 {parcalar[3]}")
    
    except FileNotFoundError:
        print("Henüz hiç şikayet kaydedilmemiş.")

def analiz():
    print("\n=== Mahalle Analizi ===")
    try:
        with open("sikayetler.txt", "r", encoding="utf-8") as dosya:
            satirlar = dosya.readlines()
        
        mahalleler = {}
        for satir in satirlar:
            parcalar = satir.strip().split("|")
            mahalle = parcalar[2]
            if mahalle in mahalleler:
                mahalleler[mahalle] += 1
            else:
                mahalleler[mahalle] = 1
        
        for mahalle, sayi in sorted(mahalleler.items(), key=lambda x: x[1], reverse=True):
            print(f"  {mahalle}: {sayi} şikayet")
    
    except FileNotFoundError:
        print("Henüz veri yok.")

# Ana menü
while True:
    print("\n=== Temiz Van Sistemi ===")
    print("1 - Yeni şikayet ekle")
    print("2 - Şikayetleri gör")
    print("3 - Mahalle analizi")
    print("4 - Çıkış")
    
    secim = input("\nSeçimin: ")
    
    if secim == "1":
        sikayet_al()
    elif secim == "2":
        sikayetleri_goster()
    elif secim == "3":
        analiz()
    elif secim == "4":
        print("Görüşürüz!")
        break
    else:
        print("Geçersiz seçim!")
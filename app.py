from flask import Flask, request, redirect, render_template_string, send_file
import datetime
import folium
from collections import Counter
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)

MAHALLELER = {
    "iskele": (38.4942, 43.3800),
    "şemsibey": (38.5020, 43.3750),
    "alipaşa": (38.4960, 43.3820),
    "atina": (38.4900, 43.3900),
    "şerefiye": (38.5010, 43.3700),
    "cumhuriyet": (38.5030, 43.3780),
    "dedebayırı": (38.4980, 43.3850),
}

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Temiz Van</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial; background: #f0f4f0; }
        .header { background: #2d8a4e; color: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; }
        .header h1 { font-size: 24px; }
        .header p { opacity: 0.8; font-size: 14px; }
        .rapor-btn { background: white; color: #2d8a4e; padding: 10px 20px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 14px; }
        .rapor-btn:hover { background: #e8f5e9; }
        .container { max-width: 1100px; margin: 30px auto; padding: 0 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .card h2 { color: #2d8a4e; margin-bottom: 15px; font-size: 18px; }
        input, textarea, select { width: 100%; padding: 10px; margin: 6px 0 12px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
        button { background: #2d8a4e; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 15px; }
        button:hover { background: #236b3d; }
        .sikayet { background: #f9f9f9; padding: 12px; margin: 8px 0; border-left: 4px solid #2d8a4e; border-radius: 4px; }
        .sikayet strong { color: #2d8a4e; }
        .sikayet small { color: #888; }
        .istat { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; }
        .istat .sayi { background: #2d8a4e; color: white; border-radius: 20px; padding: 2px 12px; font-size: 13px; }
        .bar { height: 8px; background: #2d8a4e; border-radius: 4px; margin-top: 4px; }
        .map-container { grid-column: 1 / -1; }
        .map-container iframe { width: 100%; height: 400px; border: none; border-radius: 8px; }
        .foto { max-width: 100%; max-height: 150px; border-radius: 6px; margin-top: 8px; }
        .badge { display: inline-block; background: #e8f5e9; color: #2d8a4e; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-bottom: 4px; }
        .ozet { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
        .ozet-kart { background: white; border-radius: 10px; padding: 20px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .ozet-kart .sayi { font-size: 36px; font-weight: bold; color: #2d8a4e; }
        .ozet-kart .label { color: #888; font-size: 13px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>🗑️ Temiz Van - Şikayet Sistemi</h1>
            <p>Van'ı temiz tutmak için birlikte çalışıyoruz</p>
        </div>
        <a href="/rapor" class="rapor-btn">📄 PDF Rapor İndir</a>
    </div>
    <div class="container">

        <!-- Özet Kartlar -->
        <div class="ozet">
            <div class="ozet-kart">
                <div class="sayi">{{ toplam }}</div>
                <div class="label">Toplam Şikayet</div>
            </div>
            <div class="ozet-kart">
                <div class="sayi">{{ mahalle_sayisi }}</div>
                <div class="label">Etkilenen Mahalle</div>
            </div>
            <div class="ozet-kart">
                <div class="sayi">{{ bugun }}</div>
                <div class="label">Bugünkü Şikayet</div>
            </div>
        </div>

        <div class="grid">
            <!-- Şikayet Formu -->
            <div class="card">
                <h2>📝 Yeni Şikayet</h2>
                <form method="POST" action="/ekle" enctype="multipart/form-data">
                    <input type="text" name="ad" placeholder="Adınız" required>
                    <select name="mahalle" required>
                        <option value="">-- Mahalle Seçin --</option>
                        <option>iskele</option>
                        <option>şemsibey</option>
                        <option>alipaşa</option>
                        <option>atina</option>
                        <option>şerefiye</option>
                        <option>cumhuriyet</option>
                        <option>dedebayırı</option>
                    </select>
                    <textarea name="aciklama" placeholder="Durumu açıklayın..." rows="3" required></textarea>
                    <input type="file" name="fotograf" accept="image/*">
                    <button type="submit">📤 Şikayet Gönder</button>
                </form>
            </div>

            <!-- İstatistikler -->
            <div class="card">
                <h2>📊 Mahalle İstatistikleri</h2>
                <p style="color:#888; margin-bottom:12px;">Toplam {{ toplam }} şikayet</p>
                {% for mahalle, sayi in istatistik %}
                <div class="istat">
                    <span>{{ mahalle }}</span>
                    <span class="sayi">{{ sayi }}</span>
                </div>
                <div class="bar" style="width: {{ (sayi / toplam * 100) if toplam > 0 else 0 }}%"></div>
                {% endfor %}
            </div>

            <!-- Harita -->
            <div class="card map-container">
                <h2>🗺️ Şikayet Haritası</h2>
                {{ harita | safe }}
            </div>

            <!-- Şikayetler Listesi -->
            <div class="card" style="grid-column: 1 / -1;">
                <h2>📋 Kayıtlı Şikayetler ({{ toplam }} adet)</h2>
                {% for s in sikayetler %}
                <div class="sikayet">
                    <span class="badge">{{ s.mahalle }}</span>
                    <strong>{{ s.ad }}</strong><br>
                    📝 {{ s.aciklama }}<br>
                    {% if s.fotograf %}
                    <img src="/foto/{{ s.fotograf }}" class="foto"><br>
                    {% endif %}
                    <small>⏰ {{ s.zaman }}</small>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

def sikayetleri_oku():
    try:
        with open("sikayetler.txt", "r", encoding="utf-8") as f:
            satirlar = f.readlines()
        liste = []
        for satir in satirlar:
            p = satir.strip().split("|")
            if len(p) >= 4:
                liste.append({
                    "zaman": p[0], "ad": p[1], "mahalle": p[2],
                    "aciklama": p[3], "fotograf": p[4] if len(p) > 4 else None
                })
        return liste
    except FileNotFoundError:
        return []

def harita_olustur(sikayetler):
    m = folium.Map(location=[38.497, 43.380], zoom_start=14)
    mahalle_sayilari = Counter(s["mahalle"] for s in sikayetler)
    for mahalle, koordinat in MAHALLELER.items():
        sayi = mahalle_sayilari.get(mahalle, 0)
        if sayi > 0:
            renk = "red" if sayi >= 3 else "orange" if sayi >= 2 else "blue"
            folium.CircleMarker(
                location=koordinat,
                radius=10 + sayi * 5,
                color=renk, fill=True, fill_opacity=0.7,
                popup=f"{mahalle}: {sayi} şikayet"
            ).add_to(m)
        else:
            folium.Marker(
                location=koordinat,
                popup=mahalle,
                icon=folium.Icon(color="green", icon="info-sign")
            ).add_to(m)
    return m._repr_html_()

def pdf_rapor_olustur(sikayetler):
    import unicodedata

    def temizle(metin):
        metin = metin.replace('ş', 's').replace('Ş', 'S')
        metin = metin.replace('ç', 'c').replace('Ç', 'C')
        metin = metin.replace('ğ', 'g').replace('Ğ', 'G')
        metin = metin.replace('ı', 'i').replace('İ', 'I')
        metin = metin.replace('ö', 'o').replace('Ö', 'O')
        metin = metin.replace('ü', 'u').replace('Ü', 'U')
        return metin
    dosya = "raporlar/temiz_van_raporu.pdf"
    doc = SimpleDocTemplate(dosya, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    baslik_style = ParagraphStyle('baslik', fontSize=18, textColor=colors.HexColor('#2d8a4e'), spaceAfter=10, fontName='Helvetica-Bold')
    alt_baslik_style = ParagraphStyle('altbaslik', fontSize=12, textColor=colors.HexColor('#2d8a4e'), spaceAfter=8, fontName='Helvetica-Bold')
    normal_style = ParagraphStyle('normal', fontSize=10, spaceAfter=5, fontName='Helvetica')
    
    story = []
    
    # Başlık
    story.append(Paragraph("TEMIZ VAN - SIKAYET RAPORU", baslik_style))
    tarih = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"Rapor Tarihi: {tarih}", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Özet
    story.append(Paragraph("OZET", alt_baslik_style))
    mahalle_sayilari = Counter(s["mahalle"] for s in sikayetler)
    bugun = datetime.datetime.now().strftime("%d/%m/%Y")
    bugun_sayisi = sum(1 for s in sikayetler if s["zaman"].startswith(bugun))
    
    ozet_data = [
        ["Toplam Sikayet", "Etkilenen Mahalle", "Bugunku Sikayet"],
        [str(len(sikayetler)), str(len(mahalle_sayilari)), str(bugun_sayisi)]
    ]
    ozet_tablo = Table(ozet_data, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    ozet_tablo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d8a4e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#e8f5e9'), colors.white]),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2d8a4e')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#2d8a4e')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(ozet_tablo)
    story.append(Spacer(1, 0.5*cm))
    
    # Mahalle İstatistikleri
    story.append(Paragraph("MAHALLE ISTATISTIKLERI", alt_baslik_style))
    istat_data = [["Mahalle", "Sikayet Sayisi", "Durum"]]
    for mahalle, sayi in mahalle_sayilari.most_common():
        durum = "KRITIK" if sayi >= 3 else "YUKSEK" if sayi >= 2 else "NORMAL"
        istat_data.append([temizle(mahalle), str(sayi), durum])
    
    istat_tablo = Table(istat_data, colWidths=[6*cm, 5*cm, 5.5*cm])
    istat_tablo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d8a4e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2d8a4e')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(istat_tablo)
    story.append(Spacer(1, 0.5*cm))
    
    # Tüm Şikayetler
    story.append(Paragraph("TUM SIKAYETLER", alt_baslik_style))
    sikayet_data = [["Tarih", "Kisi", "Mahalle", "Aciklama"]]
    for s in reversed(sikayetler):
        aciklama = s["aciklama"][:50] + "..." if len(s["aciklama"]) > 50 else s["aciklama"]
        sikayet_data.append([s["zaman"], temizle(s["ad"]), temizle(s["mahalle"]), temizle(aciklama)])
    
    sikayet_tablo = Table(sikayet_data, colWidths=[3.5*cm, 3*cm, 3*cm, 7*cm])
    sikayet_tablo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2d8a4e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (2,-1), 'CENTER'),
        ('ALIGN', (3,0), (3,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f9f9f9'), colors.white]),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#2d8a4e')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(sikayet_tablo)
    
    doc.build(story)
    return dosya

@app.route("/")
def anasayfa():
    sikayetler = sikayetleri_oku()
    istatistik = Counter(s["mahalle"] for s in sikayetler).most_common()
    harita = harita_olustur(sikayetler)
    bugun = datetime.datetime.now().strftime("%d/%m/%Y")
    bugun_sayisi = sum(1 for s in sikayetler if s["zaman"].startswith(bugun))
    mahalle_sayisi = len(set(s["mahalle"] for s in sikayetler))
    return render_template_string(HTML, sikayetler=list(reversed(sikayetler)),
                                  toplam=len(sikayetler), istatistik=istatistik,
                                  harita=harita, bugun=bugun_sayisi,
                                  mahalle_sayisi=mahalle_sayisi)

@app.route("/ekle", methods=["POST"])
def ekle():
    ad = request.form["ad"]
    mahalle = request.form["mahalle"]
    aciklama = request.form["aciklama"]
    zaman = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    fotograf_adi = ""
    if "fotograf" in request.files:
        foto = request.files["fotograf"]
        if foto.filename != "":
            os.makedirs("fotolar", exist_ok=True)
            fotograf_adi = f"{zaman.replace('/', '-').replace(' ', '_').replace(':', '-')}_{foto.filename}"
            foto.save(f"fotolar/{fotograf_adi}")
    with open("sikayetler.txt", "a", encoding="utf-8") as f:
        f.write(f"{zaman}|{ad}|{mahalle}|{aciklama}|{fotograf_adi}\n")
    return redirect("/")

@app.route("/foto/<filename>")
def foto(filename):
    from flask import send_from_directory
    return send_from_directory("fotolar", filename)

@app.route("/rapor")
def rapor():
    sikayetler = sikayetleri_oku()
    dosya = pdf_rapor_olustur(sikayetler)
    return send_file(dosya, as_attachment=True, download_name="temiz_van_raporu.pdf")

if __name__ == "__main__":
    app.run(debug=True)
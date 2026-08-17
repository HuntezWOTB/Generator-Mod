# 🚀 HiddenTanks-Generator-Mod

**WOT BLITZ araştırma ağacındaki tüm araçları görüntülemek için otomasyon.**  
Tüm dosya biçimleriyle çalışır (orijinal `xml`/`yaml` ve sıkıştırılmış `dvpl`).

Program, oyun yapılandırma dosyalarını değiştirerek gizli, koleksiyonluk, premium ve ödül araçları dahil olmak üzere **tüm tankları hangarda tamamen açmanıza** olanak tanır. Tüm değişiklikler otomatik yedekleme sayesinde geri alınabilir.

---

## 📌 Bu nedir?

HiddenTanks-Generator-Mod, Python/Tkinter ile yazılmış bir masaüstü uygulamasıdır:

- World of Tanks Blitz oyununun teknoloji ağacı dosyalarını (`tree_*.yaml`) ve araç listesi dosyalarını (`list.xml`) okur.
- `list.xml`'den tüm tankları çıkarır, gereksiz etiketleri (`deprecated`, `secret`, `testTank` vb.) kaldırır ve `notInShop` bayrağını `false` olarak ayarlar.
- Orijinal `tree.yaml`'ye dayanarak, **daha önce gizlenmiş tüm tankları** (hem yorum satırındakiler hem de ağaçta eksik olanlar) doğru kategorilere (sıradan, koleksiyonluk, premium) ekleyen yeni bir ağaç oluşturur.
- Değiştirilmiş dosyaları formatlarını (DVPL/metin) ve kodlamalarını koruyarak geri yazar.
- Hem ana oyun dosyalarının hem de **DLC paketlerindeki** (`packs` klasörü) dosyaların değiştirilmesini destekler.
- Dil, tema, çalışma modu ayarları ve oluşturma, geri yükleme, istatistikler ve dışa aktarma düğmeleri ile kullanıcı dostu bir grafik arayüz sunar.

---

## ⚙️ Nasıl çalışır (teknik genel bakış)

### 1. Dosya algılama
Her ulus için (CN, EU, FR, DE, JP, HN, UK, US, SU), program `tree_*.yaml` ve `list.xml` dosyalarının oyunun `Data` klasöründeki yollarını belirler. **"DLC dosyalarını değiştir"** seçeneği etkinleştirilirse, bu dosyaları `%USERPROFILE%/AppData/Local/wotblitz/packs` klasöründe (`.dvpl` uzantılı) da arar. Varsa DLC dosyaları önceliklidir.

### 2. Okuma ve açma
Dosyalar şunlar olabilir:
- Düz metin (`xml`, `yaml`)
- **DVPL** formatında paketlenmiş (sonunda `DVPL` imzası, LZ4 sıkıştırması)

Program türü otomatik olarak algılar, içeriği açar ve daha sonra yazmak için sıkıştırma parametrelerini hatırlar.

### 3. XML işleme (`list.xml`)
Tüm `<vehicle>` etiketleri çıkarılır. Her tank için şunlar saklanır:
- `id`, `level`, `price` (altın varlığı), `notInShop`, `tags`.
- `deprecated`, `secret`, `testTank`, `lightTankArtefacts_User`, `grousers_user`, `event_battles` listesindeki etiketler kaldırılır.
- `notInShop` bayrağı zorla `false` olarak ayarlanır (tank kullanılabilir hale gelir).

### 4. YAML işleme (`tree_*.yaml`)
- Orijinal ağaç okunur, görünür tanklar ve konumları `[level, row]` hatırlanır.
- Yorum satırları belirlenir (gizli olarak kabul edilirler).
- XML'den görünür olmayan ve yorumlanmamış tüm tanklar **gizli** olarak işaretlenir.

### 5. Yeni ağaç oluşturma
Her `level` için gruplar oluşturulur:
- **Görünür tanklar** – orijinal yerlerinde kalır.
- **Gizli tanklar** – seviyenin sonuna yeni satır numaralarıyla eklenir, kategorilere göre gruplandırılır:
  - `ordinary` – sıradan (altın fiyatı yok, `deprecated` etiketli, mağazada değil)
  - `collectible` – koleksiyonluk (altın fiyatı ve `collectible` etiketi var)
  - `premium` – premium (altın fiyatı var ama `collectible` etiketi yok)

Kategoriler tank sınıfına (`lightTank`, `mediumTank`, `heavyTank`, `AT-SPG`) ve ardından isme göre sıralanır.

### 6. Dosyaları yazma
Değiştirilmiş dosyalar şunları koruyarak geri yazılır:
- Orijinal format (DVPL veya metin).
- Orijinal kodlama (genellikle BOM'lu veya BOM'suz UTF-8).
- Sıkıştırma türü (DVPL ise).

Dosya DLC'ye aitse, orijinaldeki gibi **"salt okunur"** özniteliği ayarlanır.

### 7. Yedekleme ve geri yükleme
Değişiklik yapmadan önce program, değiştirilen dosyaların tam bir kopyasını oyun klasörü içindeki `HiddenTanks_Backup` klasöründe `Game/` ve `DLC/` alt klasör yapısını koruyarak oluşturur. Geri yükleme, bu dosyaları geri kopyalar.

---

## 🎯 Özellikler

- **Üç çalışma modu**:
  - `NON-DVPL` – dosyaları her zaman düz metin olarak okur/yazar (sıkıştırma yok).
  - `DVPL` – her zaman LZ4 sıkıştırması kullanır (tip 2).
  - `UNIVERSAL` – her dosyanın biçimini otomatik olarak algılar ve aynı biçimde kaydeder.

- **DLC desteği** – varsa `packs` klasöründeki dosyaları değiştirir.

- **Mod dışa aktarma** – `result/HiddenTanks_Generated_<oyun_sürümü>/` dizinini iki alt klasörle oluşturur:
  - `Mod/` – dağıtım için hazır değiştirilmiş dosyalar.
  - `Backup/` – geri yükleme için orijinal dosyalar.

- **İstatistikler** – ulus başına görünür ve gizli tank sayısını gösterir ve DLC ile oyun listelerini karşılaştırır (DLC'de kaç yeni tank var).

- **Tam yerelleştirme** – arayüz ve tüm günlük mesajları **6 dile** çevrilmiştir: İngilizce, Rusça, Lehçe, Ukraynaca, Türkçe, Almanca. JSON dosyalarıyla kolayca yeni diller eklenebilir.

- **Ayarlar kaydedilir** – oyun yolu, dil, tema, mod ve DLC seçeneği `config.json` dosyasında saklanır.

- **Kullanışlı günlük** – tüm işlemler ve hatalar, kopyalama (`Ctrl+C`), tümünü seçme (`Ctrl+A`) ve temizleme özellikleriyle ayrı bir pencerede görüntülenir.

---

## 🖥️ Arayüz

Ana pencere şunları içerir:
- Oyun klasörünü seçmek için bir alan.
- Dil, tema ve mod için açılır listeler.
- "DLC dosyalarını değiştir" onay kutusu.
- Düğmeler: **"Mod Oluştur"**, **"Orijinali Geri Yükle"**, **"İstatistikler"**, **"Modu Dışa Aktar"**.
- Ek "Kopyala" ve "Temizle" düğmeleri olan bir günlük alanı.

---

## ⚠️ Önemli: Mikro güncellemeler ve DLC

Oyun **mikro güncellemeler** aldığında (yeni araçlar, küçük yamalar), oyun dosyaları değişebilir. **DLC paketleri** kullanıyorsanız ("DLC dosyalarını değiştir" seçeneği etkin), güncellemeden sonra modu yeniden oluştururken **bu seçeneği etkin tutmanız önerilir**.

Bu, DLC'ye eklenen yeni tankların da araştırma ağacında doğru şekilde görüntülenmesini sağlar. DLC dosyaları değiştirilmezse, DLC'deki yeni araçlar gizli kalabilir.

**Öneri:**  
- Her oyun güncellemesinden sonra önce **orijinalleri geri yükleyin** ("Orijinali Geri Yükle" düğmesi), ardından aynı ayarlarla (kullandıysanız DLC dahil) modu yeniden oluşturun.

---

## 📥 Kurulum ve başlatma

### Gereksinimler
- **Python 3.8+** (önerilen 3.10)

### Hızlı başlangıç
1. Python yoksa [python.org](https://python.org)'dan indirin ve kurun.
2. Programın arşivini istediğiniz bir klasöre çıkarın.
3. **`autoinstall_modules.bat`** dosyasını çalıştırın – bu, gerekli kütüphaneleri (`lz4`, `pyyaml`) `pip` aracılığıyla otomatik olarak kuracaktır.
4. Kurulum tamamlandıktan sonra **`start_program.bat`** dosyasını çalıştırın – grafik arayüz açılacaktır.

> 💡 **Not:** Eğer herhangi bir nedenle bu `.bat` dosyalarına sahip değilseniz, manuel olarak kurabilirsiniz:
> ```bash
> pip install -r requirements.txt
> python gui.py
> ```

### İlk çalıştırma
- Varsayılan ayarlarla `config.json` dosyası otomatik olarak oluşturulur.
- `locales/` klasörü çeviri dosyalarını içerir – metinleri değiştirmek için bunları düzenleyebilirsiniz.

---

## 🎮 Kullanım kılavuzu

1. **Oyun yolunu belirtin** – "Gözat..." düğmesine tıklayın ve WoT Blitz'in kök klasörünü seçin (ör. `C:/Games/World_of_Tanks_Blitz`).

2. **Ayarları yapın**:
   - Arayüz dilini seçin.
   - Temayı seçin (açık/koyu).
   - Modu seçin (önerilen: `UNIVERSAL`).
   - DLC paketlerini değiştirmek istiyorsanız "DLC dosyalarını değiştir" seçeneğini etkinleştirin.

3. **Bir işlem yapın**:
   - **"Mod Oluştur"** – değişiklikleri uygular, oyun klasöründe bir yedek oluşturur.
   - **"Orijinali Geri Yükle"** – yedekten dosyaları geri yükler (yedek kalır, manuel olarak silebilirsiniz).
   - **"İstatistikler"** – değişiklik yapmadan bilgileri gösterir.
   - **"Modu Dışa Aktar"** – dağıtım için `result/` klasöründe hazır bir mod oluşturur.

4. **Oyunu başlatın** – tüm tanklar araştırma ağacında görünür olmalıdır.

---

## 📂 Proje yapısı
Generator-Mod/
├── Documentation/ # Çok dilli tam dokümantasyon
├── core/
│ ├── config.py # Ayarları yükle/kaydet
│ ├── localization.py # Yerelleştirme işlevleri
│ ├── dvpl_utils.py # DVPL okuma/yazma (LZ4, imza)
│ ├── xml_processor.py # list.xml ayrıştırma ve değiştirme
│ ├── yaml_processor.py # Verilerden tree.yaml oluşturma
│ └── mod_generator.py # Ana mantık: arama, okuma, işleme, yazma, yedekleme, dışa aktarma
├── locales/ # Yerelleştirme dosyaları (en.json, ru.json, pl.json, uk.json, tr.json, de.json, template.json)
├── gui.py # Grafik arayüz (Tkinter)
├── autoinstall_modules.bat # Bağımlılıkları yükle
├── start_program.bat # Programı başlat
├── config.json # Kaydedilmiş ayarlar (otomatik oluşturulur)
├── requirements.txt # Bağımlılıklar
└── README.md # Bu dosya

---

## 🔧 Teknik detaylar

### Dosya biçimleri
- **DVPL** – WoT Blitz'e özel biçim: sıkıştırılmış veri bloğu (LZ4) + şunları içeren 20 baytlık altbilgi:
  - `original_size` (4 bayt)
  - `compressed_size` (4 bayt)
  - `crc32` (4 bayt)
  - `compression_type` (4 bayt: 0 – sıkıştırma yok, 1 – LZ4, 2 – LZ4 HC)
  - `DVPL` imzası (4 bayt)

- **tree_*.yaml** – `tanks` anahtarına sahip YAML dosyası, her tankın bir konumu vardır `[level, row]`.

- **list.xml** – Kök öğe `<root>` içeren XML belgesi, içinde `<vehicle>` öğeleri ve alt etiketler (`id`, `price`, `notInShop`, `tags`, `level`).

### Değiştirme algoritması (adım adım)
1. Her ulus için `tree` ve `list` dosyalarının yolları belirlenir (oyun veya DLC).
2. Dosyalar okunur (gerekirse DVPL açılır), kodlama ve sıkıştırma türü belirlenir.
3. `list.xml`'den tüm tanklar çıkarılır, gereksiz etiketler kaldırılır, `notInShop` `false` olarak ayarlanır.
4. `tree.yaml`'den görünür tanklar ve konumları çıkarılır. Ayrıca yorum satırları da belirlenir.
5. Yeni bir YAML oluşturulur:
   - Önce görünür tanklar (orijinaldeki gibi).
   - Ardından, her seviye için gizli tanklar, kategoriye göre gruplandırılarak yeni satır numaralarıyla eklenir.
6. Dosyalar orijinal format ve sıkıştırma korunarak geri yazılır.
7. Dosyalar DLC'den alınmışsa, `S_IREAD` özniteliği (salt okunur) ayarlanır.

### İşleme özellikleri
- **HN** (Other) ulusu için, görünür tank seviyeleri XML'deki gerçek değerlere göre düzeltilir (YAML'deki `level` konumu yok sayılır).
- Gizli tank kategorizasyonu:
  - `ordinary` – `notInShop` `true` ise, fiyatta altın yok ve `deprecated` etiketi varsa.
  - `collectible` – fiyatta altın varsa ve `collectible` etiketi varsa.
  - `premium` – fiyatta altın varsa ancak `collectible` etiketi yoksa.
- Gizli tanklar eklenirken, öngörülebilir bir sıralama için sınıf ve isme göre sıralanırlar.

---

## 🌍 Yerelleştirme

Arayüz ve günlük metinlerinin tümü `locales/` klasöründeki JSON dosyalarında saklanır.  
Dosyalar dil koduna göre adlandırılır (ör. `ru.json`) ve açılır listede görüntülenmek için bir `"lang_code"` alanı içerir.

**Yeni dil eklemek için:**
1. `template.json` dosyasını yeni kodla (ör. `fr.json`) kopyalayın.
2. `"lang_code"` değerini `"FR"` olarak değiştirin.
3. Tüm dizeleri çevirin.
4. Programı yeniden başlatın – dil listede görünecektir.

---

## ❓ Sık Sorulan Sorular

**S: Bu hesabım için güvenli mi?**  
C: Program yalnızca yerel yapılandırma dosyalarını değiştirir. Oyun akışını, dengeyi etkilemez veya herhangi bir avantaj sağlamaz. Arayüz modifikasyonları WoT Blitz kurallarına göre izin verilir. Ancak kendi riskinizle kullanın.

**S: Modu uyguladıktan sonra oyun başlamazsa ne yapmalıyım?**  
C: Dosyaları geri almak için **"Orijinali Geri Yükle"** düğmesine tıklayın. Sorun devam ederse, oyun dosyalarını başlatıcı aracılığıyla doğrulayın.

**S: Değişiklikler oyun güncellemesinden sonra kalır mı?**  
C: Hayır, güncellemeler dosyaların üzerine yazar. Her güncellemeden sonra modu yeniden oluşturmanız gerekir. Güncellemeden önce orijinalleri geri yüklemeniz önerilir.

**S: Yedekler nerede saklanır?**  
C: Oyun klasörü içindeki `HiddenTanks_Backup` klasöründe. Modun düzgün çalıştığından emin olana kadar silmeyin.

**S: Bunu diğer modlarla birlikte kullanabilir miyim?**  
C: Diğer modlar aynı dosyaları (`tree_*.yaml` ve `list.xml`) değiştiriyorsa çakışmalar olabilir. Temiz bir oyun kurulumuna uygulanması önerilir.

**S: `autoinstall_modules.bat` çalışmazsa ne yapmalıyım?**  
C: Python'un sistem `PATH` değişkeninde olduğundan emin olun. Değilse, bağımlılıkları manuel olarak `pip install -r requirements.txt` ile kurun.

---

## 📄 Lisans

Bu proje **Freeware** olarak dağıtılır – kişisel, ticari olmayan kullanım için ücretsizdir.  
Kaynak kodu açıktır; kendi ihtiyaçlarınız için değiştirebilirsiniz.

---

## ✉️ Geri bildirim

Sorular, öneriler veya hata raporları için lütfen depoda bir **Issue** oluşturun veya geliştiriciye e-posta gönderin.

---

**İyi oyunlar!** 🎮
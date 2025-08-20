# Bot Funksiyalarini Test Qilish Qo'llanmasi

## Muammolar to'g'irlandi ✅

### Hal qilingan muammolar:

1. **Bonus olgandan keyin yana /start so'ralish muammosi** - TO'G'IRLANDI
   - Endi har bir funksiyada user avtomatik ro'yxatdan o'tkaziladi
   - Yangi userlarga avtomatik 10 ta boshlang'ich spin beriladi

2. **Menu tugmalari to'g'ri ishlamasligi** - TO'G'IRLANDI
   - Barcha callback'larda user mavjudligi tekshiriladi
   - User mavjud bo'lmasa avtomatik yaratiladi

3. **Yangi userlar uchun boshlang'ich spinlar** - QO'SHILDI
   - INITIAL_SPINS=10 sozlamasi qo'shildi
   - Yangi userlar registratsiyada 10 ta spin oladi

## O'zgartirishlar:

### 1. `config.py` yangilandi:
- `initial_spins` sozlamasi qo'shildi
- Default qiymat: 10 spin

### 2. `db.py` yangilandi:
- `upsert_user` funksiyasiga `initial_spins` parametri qo'shildi
- Yangi userlar yaratilganda boshlang'ich spinlar beriladi

### 3. `handlers.py` to'liq qayta ishlandi:
- **Barcha flow funksiyalarida** (`_spin_flow`, `_profile_flow`, `_daily_flow`) user mavjud bo'lmasa avtomatik yaratiladi
- **Barcha callback'larda** user mavjudligi tekshiriladi va kerak bo'lsa yaratiladi:
  - `home_play` - O'ynash tugmasi
  - `home_stats` - Statistika tugmasi
  - `home_daily` - Kunlik bonus
  - `home_balance` - Balans ko'rish
  - `play_again` - Qayta o'ynash
  - `profile_btn` - Profil ko'rish

## Test qilish bosqichlari:

### 1. Muhitni sozlash:
```bash
# .env faylni yarating (agar yo'q bo'lsa)
# BOT_TOKEN ni o'z tokeningiz bilan almashtiring
```

### 2. Botni ishga tushirish:
```bash
python -m src.main
```

### 3. Testlar:

#### Test 1: Yangi user (start bosilmagan holda)
1. Botga kiring
2. Darhol "🎰 O'ynash" tugmasini bosing
3. **Kutilgan natija**: O'yin boshlanadi, 10 ta spin beriladi

#### Test 2: Kunlik bonus
1. "📆 Kundalik bonus" tugmasini bosing
2. **Kutilgan natija**: +5 spin beriladi

#### Test 3: Qayta o'ynash
1. O'yin tugagach "▶️ Yana o'ynash" tugmasini bosing
2. **Kutilgan natija**: O'yin davom etadi, /start so'ralmaydi

#### Test 4: Barcha menu tugmalari
1. "📊 Statistika" - profil ko'rsatiladi
2. "🏆 Reyting" - TOP o'yinchilar
3. "⭐ Stars hisobim" - balans ko'rsatiladi
4. "📜 O'yin qoidalari" - qoidalar ko'rsatiladi

#### Test 5: Reply keyboard tugmalari
1. "🎰 O'ynash" - o'yin boshlanadi
2. "👤 Profil" - profil ko'rsatiladi
3. "🏆 TOP" - reyting ko'rsatiladi
4. "❓ Yordam" - yordam ko'rsatiladi

## Muhim eslatmalar:

- Yangi userlar avtomatik 10 ta spin bilan boshlanadi
- User har qanday tugmani bosganda avtomatik ro'yxatdan o'tadi
- /start bosmasdan ham bot to'liq ishlaydi
- Kunlik bonus har kuni 1 marta olinadi
- Admin userlar cheksiz spin oladi

## Xatoliklar bo'lsa:

Agar xatolik yuz bersa:
1. `.env` faylda `INITIAL_SPINS=10` borligini tekshiring
2. Bot tokenni to'g'riligini tekshiring
3. Databaza faylini o'chirib qayta yarating (agar kerak bo'lsa)

## Qo'shimcha sozlamalar:

`.env` faylda:
```
INITIAL_SPINS=10  # Boshlang'ich spinlar (default: 10)
DAILY_BONUS_SPINS=5  # Kunlik bonus (default: 5)
REFERRAL_BONUS=5  # Referral bonusi (default: 5)
```

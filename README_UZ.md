# 🎰 Slot Game Bot — Yut, Yulduz, Qayta O'yna!

## 🆕 Yangi Xususiyatlar (2025)

### 🤖 Avtomatik Admin Bog'lanish
- **📞 Admin bilan bog'lanish tugmasi** - Profil menyusida
- **📨 Avtomatik xabar yuborish** - Adminlarga foydalanuvchi ma'lumotlari bilan
- **💬 To'g'ridan-to'g'ri bog'lanish** - Admin foydalanuvchi bilan xabar yozishi mumkin
- **🎁 Bonus berish** - Admin foydalanuvchiga yulduz berishi mumkin

### 🔒 Majburiy Kanal Obunasi
- **⚠️ Majburiy obuna** - Bot ishlashi uchun kanal obunasi talab qilinadi
- **🔄 Avtomatik tekshirish** - Har soatda barcha foydalanuvchilar tekshiriladi
- **📢 Ogohlantirish xabarlari** - Obuna bekor qilinganda avtomatik xabar
- **🚫 Funksiya bloklash** - Obuna bo'lmagan foydalanuvchilar botdan foydalana olmaydi

### 🛠️ Admin Buyruqlari
- **`/check_sub`** - O'zingizning obuna holatini tekshirish
- **`/check_all_subs`** - Barcha foydalanuvchilar obuna statistikasi
- **`/force_check_subs`** - Barcha obunalarni majburiy tekshirish va yangilash

## 🎯 Asosiy Xususiyatlar

### 🎰 Slot O'yini
- **3 ta belgi** tasodifiy tanlanadi
- **G'alaba kombinatsiyalari** - 100 yulduzgacha
- **Qo'shimcha mukofotlar** - 2 ta bir xil belgi uchun ham

### 👥 Referal Tizimi
- **Har bir do'st uchun 10 yulduz**
- **Cheksiz referal** taklif qilish mumkin
- **Maxsus linklar** har bir foydalanuvchi uchun

### 🎁 Bonuslar
- **Kunlik bonus** - Har 24 soatda 5 yulduz
- **Admin bonuslari** - Maxsus mukofotlar
- **O'yin bonuslari** - Yutganingizda qo'shimcha yulduzlar

### 💳 To'lov Tizimi
- **Telegram Stars** orqali yulduzlar sotib olish
- **Turli paketlar** - 1 dan 50 yulduzgacha
- **Xavfsiz to'lov** - Telegram tomonidan himoyalangan

## 🚀 O'rnatish va Ishga Tushirish

### 📋 Talablar
- Python 3.11+
- aiogram 3.x
- aiosqlite

### ⚙️ Sozlash
1. `config/settings.py` da bot tokenini o'rnating
2. `REQUIRED_CHANNEL` ni o'z kanalingizga o'zgartiring
3. `ADMIN_IDS` ga admin foydalanuvchilar ID sini qo'shing

### 🏃‍♂️ Ishga Tushirish
```bash
# Virtual environment yaratish
python -m venv venv

# Faollashtirish
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bog'liqliklarni o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish
python main_uz.py
```

## 🔧 Texnik Ma'lumotlar

### 🗄️ Ma'lumotlar Bazasi
- **SQLite** - Yengil va ishonchli
- **Connection pooling** - Yuqori ishlash
- **Avtomatik migratsiya** - Eski ma'lumotlar bilan moslik

### 🛡️ Xavfsizlik
- **Rate limiting** - Spam oldini olish
- **Admin middleware** - Faqat admin buyruqlari
- **Kanal obunasi** - Majburiy tasdiqlash

### 📊 Monitoring
- **Performance tracking** - Barcha operatsiyalar kuzatiladi
- **Error logging** - Xatolar avtomatik qayd etiladi
- **Health checks** - Tizim holati muntazam tekshiriladi

## 📞 Yordam va Qo'llab-quvvatlash

### 🤝 Admin bilan bog'lanish
- Profil menyusida "📞 Admin Bilan Bog'lanish" tugmasini bosing
- Savolingiz yoki muammongizni yozing
- Admin 24 soat ichida javob beradi

### 📚 Qo'llanma
- `/help` buyrug'i orqali barcha funksiyalar haqida ma'lumot
- O'yin qoidalari va g'alaba jadvali
- Bonuslar va referal tizimi haqida ma'lumot

### 🆘 Muammo hal qilish
- Kanal obunasi majburiy
- Obuna bekor qilinganda qaytadan obuna bo'ling
- Admin bilan bog'laning agar muammo davom etsa

## 🌟 Yangilanishlar

### v2.0 (2025)
- ✅ Avtomatik admin bog'lanish tizimi
- ✅ Majburiy kanal obunasi
- ✅ Kuchaytirilgan xavfsizlik
- ✅ Performance monitoring
- ✅ Avtomatik database migratsiya

### v1.0 (2024)
- 🎰 Slot o'yini
- 👥 Referal tizimi
- 🎁 Bonuslar
- 💳 To'lov tizimi

---

**🎯 Maqsad:** Foydalanuvchilar uchun qiziqarli va foydali slot o'yini yaratish, kanal obunasini rag'batlantirish va admin bilan samarali bog'lanish imkoniyatini ta'minlash.

**💡 Maslahat:** Kanal obunasini unutmang va do'stlaringizni taklif qiling!

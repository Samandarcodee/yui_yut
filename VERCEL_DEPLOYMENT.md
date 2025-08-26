# 🚀 Vercel Deployment Guide

## 📋 **Tayyorgarlik**

### 1. **Vercel Account**
- [Vercel.com](https://vercel.com) da ro'yxatdan o'ting
- GitHub, GitLab yoki Bitbucket bilan bog'laning

### 2. **Telegram Bot Token**
- [@BotFather](https://t.me/BotFather) dan bot token oling
- Bot webhook sozlamalarini yoqing

### 3. **Git Repository**
- Loyihani GitHub/GitLab ga push qiling
- Repository public yoki private bo'lishi mumkin

## 🔧 **Deployment Qadamlari**

### **1-qadam: Vercel Dashboard**
```
1. Vercel Dashboard ga kiring
2. "New Project" ni bosing
3. GitHub repository ni tanlang
4. "Import" ni bosing
```

### **2-qadam: Environment Variables**
```
BOT_TOKEN=your_actual_bot_token
WEBHOOK_URL=https://your-app-name.vercel.app
```

### **3-qadam: Build Settings**
```
Framework Preset: Other
Build Command: (bo'sh qoldiring)
Output Directory: (bo'sh qoldiring)
Install Command: pip install -r api/requirements.txt
```

### **4-qadam: Deploy**
```
"Deploy" ni bosing
Deployment tugaguncha kuting
```

## 🌐 **Webhook Sozlash**

### **1. Bot Webhook URL ni o'rnatish**
```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://your-app.vercel.app/api/webhook"}'
```

### **2. Webhook Status ni tekshirish**
```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo"
```

## 📁 **Fayl Strukturasi**

```
project/
├── api/
│   ├── __init__.py
│   ├── webhook.py
│   └── requirements.txt
├── handlers/
├── keyboards/
├── config/
├── db/
├── bot/
├── vercel.json
└── env.example
```

## ⚙️ **Configuration**

### **vercel.json**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/webhook.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/webhook",
      "dest": "api/webhook.py"
    }
  ]
}
```

### **Environment Variables**
- `BOT_TOKEN`: Telegram bot token
- `WEBHOOK_URL`: Vercel app URL

## 🧪 **Testing**

### **1. Health Check**
```
GET https://your-app.vercel.app/health
```

### **2. Bot Test**
```
1. Telegram da botga xabar yuboring
2. Bot javob berishini tekshiring
3. Vercel logs da xatolarni ko'ring
```

## 🔍 **Monitoring**

### **Vercel Dashboard**
- Function logs
- Performance metrics
- Error tracking

### **Bot Logs**
- Webhook requests
- Database operations
- Error handling

## 🚨 **Muammolar va Yechimlar**

### **Webhook Error 500**
```
1. Environment variables to'g'ri o'rnatilganini tekshiring
2. Bot token valid ekanligini tekshiring
3. Database connection ni tekshiring
```

### **Build Error**
```
1. requirements.txt faylini tekshiring
2. Python version compatibility ni tekshiring
3. Import paths ni tekshiring
```

### **Database Error**
```
1. SQLite file permissions ni tekshiring
2. Database path to'g'ri ekanligini tekshiring
3. Connection pooling ni tekshiring
```

## 📊 **Performance Optimization**

### **1. Cold Start Reduction**
- Minimal dependencies
- Efficient imports
- Connection pooling

### **2. Memory Management**
- Proper cleanup
- Resource limits
- Error handling

### **3. Database Optimization**
- Indexes
- Query optimization
- Connection management

## 🔐 **Security**

### **1. Environment Variables**
- Sensitive data ni environment variables da saqlang
- Vercel secrets dan foydalaning

### **2. Webhook Validation**
- Telegram signature verification
- Rate limiting
- Input validation

### **3. Database Security**
- SQL injection protection
- Access control
- Data encryption

## 📈 **Scaling**

### **1. Auto-scaling**
- Vercel serverless functions
- Automatic scaling
- Global CDN

### **2. Database Scaling**
- Connection pooling
- Query optimization
- Caching strategies

## 🎯 **Deployment Checklist**

- [ ] Vercel account yaratildi
- [ ] Repository GitHub ga push qilindi
- [ ] Environment variables o'rnatildi
- [ ] Build settings sozlandi
- [ ] Deployment amalga oshirildi
- [ ] Webhook URL o'rnatildi
- [ ] Bot test qilindi
- [ ] Health check ishlaydi
- [ ] Error handling ishlaydi
- [ ] Monitoring sozlandi

## 🎉 **Muvaffaqiyatli Deployment!**

Bot endi Vercel da ishlaydi va:
- 24/7 uptime
- Global CDN
- Auto-scaling
- Professional monitoring
- Easy deployment

## 📞 **Support**

Muammolar bo'lsa:
1. Vercel documentation
2. Telegram Bot API docs
3. Project logs
4. Community forums

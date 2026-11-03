# رودمپ سریع: Docker-ی کردن یک پروژه‌ی پایتون

قالب آماده برای وقتی که یک برنامه‌ی پایتون دارید و می‌خواهید **سریع** Docker-ی‌اش کنید.
برای هر پروژه‌ی جدید، فقط `app.py`، `requirements.txt` و خط `CMD` در Dockerfile عوض می‌شوند.

```
03-quick-start/
├── app.py              ← کد برنامه
├── requirements.txt    ← کتابخانه‌ها
├── Dockerfile          ← قالب ثابت
├── .dockerignore       ← چیزهایی که نباید داخل image بروند
└── compose.yaml        ← اجرا با یک دستور
```

## مراحل

| # | کار | دستور / فایل |
|---|---|---|
| ۱ | کد را بنویسید | `app.py` |
| ۲ | کتابخانه‌ها | `requirements.txt` |
| ۳ | **اول بدون Docker تست کنید** | `uvicorn app:app --port 8000` |
| ۴ | Dockerfile | از همین قالب کپی کنید؛ فقط `CMD` را تنظیم کنید |
| ۵ | `.dockerignore` | از همین قالب کپی کنید |
| ۶ | `compose.yaml` | اسم `image` را **یکتا** کنید |
| ۷ | اجرا | `docker compose up -d --build` |
| ۸ | بررسی | `docker compose ps` و http://localhost:8000 |

## دستورهای روزمره

| کار | دستور |
|---|---|
| روشن کردن / بعد از تغییر کد | `docker compose up -d --build` |
| دیدن لاگ | `docker compose logs -f` |
| خاموش کردن | `docker compose down` |

## ✅ چک‌لیست قبل از build

- [ ] همه‌ی فایل‌ها **ذخیره** شده‌اند (VS Code: File ← Auto Save)
- [ ] اسم فایل دقیقاً `requirements.txt` است (نه `requirments.txt`)
- [ ] در `CMD` نوشته `--host 0.0.0.0`
- [ ] اسم ماژول در `CMD` درست است: فایل `app.py` ← `app:app`، فایل `main.py` ← `main:app`
- [ ] پورت 8000 آزاد است
- [ ] اسم `image` در `compose.yaml` با پروژه‌های دیگر یکی نیست

## نکته‌ها

- **Mirror:** خط `PIP_INDEX_URL` در Dockerfile برای شبکه‌های ایران است. خارج از ایران حذفش کنید.
- **image‌ها از Docker Hub باز نمی‌شوند؟** Docker Desktop ← Settings ← Docker Engine ← `"registry-mirrors": ["https://docker.arvancloud.ir"]`
- **برای سرور واقعی:** کاربر غیر root و `HEALTHCHECK` اضافه کنید ← [درس ۱۰](../01-docker-lab/README.md)

# 🐳 یادگیری Docker به فارسی - قدم به قدم و عملی

آموزش عملی Docker برای برنامه‌نویس‌های پایتون: از اولین `docker run` تا یک سیستم کامل
**FastAPI + PostgreSQL + Redis** با Docker Compose، عیب‌یابی و image آماده‌ی production.

این آموزش روی **Windows + Docker Desktop** و در **شبکه‌ی ایران** نوشته و تست شده است؛
برای همین Mirror‌ها و خطاهای واقعی‌ای که در این شرایط پیش می‌آید (و راه حلشان) هم داخلش هست.

---

## 📂 ساختار ریپو

| پوشه | محتوا | برای چه کسی |
|---|---|---|
| [`01-docker-lab`](01-docker-lab) | **۱۳ درس** از صفر تا production، روی یک پروژه‌ی واقعی | یادگیری کامل |
| [`02-from-scratch`](02-from-scratch) | یک برنامه، سه روش Docker-ی کردن: دستی، `docker init`، افزونه‌ی VS Code | مقایسه‌ی ابزارها |
| [`03-quick-start`](03-quick-start) | قالب آماده + رودمپ ۸ مرحله‌ای | کار سریع در شرکت |

---

## 📚 فهرست درس‌ها ([01-docker-lab](01-docker-lab/README.md))

| درس | موضوع |
|---|---|
| ۰ | آماده‌سازی و Mirror برای ایران |
| ۱ | Image و Container |
| ۲ | پورت، اجرا در پس‌زمینه، لاگ، رفتن داخل container |
| ۳ | اولین Dockerfile، لایه‌ها و cache |
| ۴ | متغیرهای محیطی (`-e`، `--env-file`) |
| ۵ | شبکه: پیدا کردن container با اسم |
| ۶ | Volume: نگه داشتن داده |
| ۷ | Docker Compose: کل سیستم با یک دستور |
| ۷.۵ | شروع از پوشه‌ی خالی: مقایسه‌ی سه روش ([02-from-scratch](02-from-scratch)) |
| ۸ | حالت توسعه: bind mount و reload خودکار |
| ۹ | عیب‌یابی لایه‌به‌لایه + خرابکاری عمدی |
| ۱۰ | Image حرفه‌ای: کاربر غیر root، healthcheck، multi-stage |
| ۱۱ | Registry شخصی |
| ۱۲ | تمیزکاری و مدیریت فضا |

در انتهای درس‌ها: **Cheat Sheet** دستورها و جدول **مشکلات رایج** (همه از خطاهای واقعی حین یادگیری).

---

## ⚡ شروع سریع

پیش‌نیاز: [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) نصب و روشن باشد.

```powershell
git clone https://github.com/ahuraERFAN/docker-learning-fa.git
cd docker-learning-fa/01-docker-lab
copy .env.example .env
docker compose up -d --build
```
http://localhost:8000/health ← `{"app":"ok","database":"ok","redis":"ok"}`

---

## 🇮🇷 نکته‌های شبکه‌ی ایران

| مشکل | راه حل |
|---|---|
| Docker Hub (image‌ها) | Docker Desktop ← Settings ← Docker Engine ← `"registry-mirrors": ["https://docker.arvancloud.ir"]` |
| PyPI (`pip install`) کند یا `Read timed out` | `--build-arg PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple` (در compose از `.env` خوانده می‌شود) |
| Mirror با خطای `402 Payment Required` | Mirror پولی شده؛ یکی دیگر را امتحان کنید |
| ورود به Docker Desktop: `RBAC: access denied` | لازم نیست؛ **Skip** کنید |

آدرس Mirror‌ها ممکن است تغییر کند؛ قبل از استفاده بررسی کنید.

---

## 🧰 تکنولوژی‌ها

Docker · Docker Compose · Python 3.12 · FastAPI · Uvicorn · PostgreSQL 17 · Redis 7

---

## 📄 لایسنس

[MIT](LICENSE)

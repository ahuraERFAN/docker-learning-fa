# درس ۷.۵ - شروع از پوشه‌ی خالی: سه روش

یک برنامه‌ی ساده‌ی Todo (`main.py` + `requirements.txt`، **کاملاً یکسان** در هر سه پوشه) به سه روش Docker-ی شده است تا بتوانید نتیجه‌ها را کنار هم مقایسه کنید.

| پوشه | روش | پورت |
|---|---|---|
| [`todo-manual`](todo-manual) | ✋ دستی: همه را خودتان می‌نویسید | 8000 |
| [`todo-init`](todo-init) | 🐳 دستور `docker init` | 8001 |
| [`todo-vscode`](todo-vscode) | 🧩 افزونه‌ی **Container Tools** در VS Code ← `Ctrl+Shift+P` ← *Containers: Add Docker Files to Workspace* ← **Python: FastAPI** | 8002 |

اجرای هر کدام:
```powershell
cd todo-manual        # یا todo-init / todo-vscode
docker compose up -d --build
```
http://localhost:8000/docs (یا 8001 / 8002)

---

## مسیر درست شروع یک پروژه

1. کد را بنویسید و **اول بدون Docker** تست کنید: `uvicorn main:app --port 8000`
2. Dockerfile (دستی یا با ابزار) ← **خروجی ابزار را خط به خط بخوانید**
3. `.dockerignore`
4. `docker build` و `docker run`
5. `compose.yaml`

---

## مقایسه

| موضوع | ✋ دستی | 🐳 docker init | 🧩 افزونه‌ی VS Code |
|---|---|---|---|
| نسخه‌ی پایتون | `3.12-slim` ✅ | `3.12.9-slim` (قفل، ولی قدیمی) | `3-slim` ❌ بی‌صدا 3.15 شد |
| `WORKDIR` قبل از `COPY` | ✅ | ✅ | ❌ requirements در `/` رفت |
| `ENV PYTHON...` | ✅ | ✅ | ✅ |
| کاربر غیر root | ❌ | ✅ قبل از کپی کد | ✅ بعد از کپی (حجم اضافه با `chown`) |
| کش pip | `--no-cache-dir` | `--mount=type=cache` ⭐ | — |
| `CMD` | فرم exec ✅ | فرم shell ⚠ | exec، ولی gunicorn نصب نبود ❌ |
| Mirror | ✅ | ❌ (دستی اضافه شد) | ❌ (دستی اضافه شد) |
| مزیت خاص | کنترل کامل | نمونه‌ی دیتابیس با `secrets` | `compose.debug.yaml` برای دیباگ با breakpoint |
| بدون ویرایش کار کرد؟ | — | ✅ | ❌ (۵ اصلاح، با `FIX` در Dockerfile علامت خورده) |

> فایل‌های `todo-init` و `todo-vscode` همان خروجی ابزارها هستند؛ فقط تغییرهای ضروری (Mirror، پورت، و در todo-vscode اصلاح باگ‌ها) دستی اضافه شده و در کامنت‌ها مشخص است. `.dockerignore` این دو، قالب استاندارد همان ابزارهاست.

---

## درس‌های کلیدی

- `COPY . .` ← نقطه‌ی اول = پوشه‌ی پروژه روی **ویندوز** (build context)، نقطه‌ی دوم = `WORKDIR` **داخل container**. دو سیستم فایل جدا.
- `WORKDIR /app` یک قرارداد است (`/code` و `/src` هم درست است)، ولی **هرگز** کد را در `/` نریزید.
- `--host 0.0.0.0` در container الزامی است؛ `127.0.0.1` یعنی «فقط خود container».
- `.dockerignore` جلوی کپی شدن `__pycache__`، `.env`، `.git` و `venv` را می‌گیرد؛ `PYTHONDONTWRITEBYTECODE=1` جلوی ساخته شدن `__pycache__` **داخل** container را.
- هر `ENV`/`ARG` تازه بالای `RUN pip install`، cache آن لایه را باطل می‌کند.
- tag کلی (`3-slim`) = image بی‌خبر عوض می‌شود. همیشه نسخه را مشخص کنید.
- `executable file not found in $PATH` = برنامه‌ی `CMD` نصب نیست. Docker محتوای `CMD` را موقع build چک نمی‌کند.
- اسم image در `compose.yaml` باید **یکتا** باشد؛ دو پروژه با یک اسم image همدیگر را رونویسی می‌کنند.
- **ابزارهای خودکار نقطه‌ی شروع‌اند، نه پایان.**

---

## Dockerfile ترکیبی (بهترین‌های هر سه)

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

# کاربر محدود - قبل از کپی کد (از docker init)
ARG UID=10001
RUN adduser --disabled-password --gecos "" --no-create-home --uid ${UID} appuser

# Mirror + کش pip بین buildها (از docker init)
ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

USER appuser
EXPOSE 8000
# فرم exec (از نسخه‌ی دستی)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

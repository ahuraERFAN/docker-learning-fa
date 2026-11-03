# Docker Lab - یادگیری Docker قدم به قدم

یک پروژه‌ی کوچک برای تمرین همه‌ی کارهای اصلی Docker:
یک **API با FastAPI** + **PostgreSQL** + **Redis**.

هر درس: **هدف ← دستورها ← چه چیزی باید ببینید ← تمرین**.
دستورها را در **PowerShell** یا ترمینال VS Code، داخل پوشه‌ی همین پروژه اجرا کنید.

```
01-docker-lab/
├── app/main.py          # برنامه‌ی FastAPI
├── requirements.txt
├── Dockerfile           # درس ۳ - ساده
├── Dockerfile.prod      # درس ۱۰ - حرفه‌ای (multi-stage, non-root, healthcheck)
├── .dockerignore        # درس ۳
├── .env.example         # درس ۴ و ۷
├── compose.yaml         # درس ۷ - کل سیستم با یک دستور
└── compose.dev.yaml     # درس ۸ - حالت توسعه با reload خودکار
```

---

## مفاهیم در یک نگاه

| مفهوم | یعنی چه | مثال در زندگی |
|---|---|---|
| **Image** | قالب فقط‌خواندنی: سیستم‌عامل + برنامه + کتابخانه‌ها | فایل نصب / قالب کیک |
| **Container** | یک نسخه‌ی در حال اجرا از image | برنامه‌ی نصب‌شده و روشن / خود کیک |
| **Dockerfile** | دستور ساخت image | دستور پخت |
| **Volume** | جای دائمی داده، جدا از container | هارد اکسترنال |
| **Network** | شبکه‌ی خصوصی بین containerها | شبکه‌ی داخلی اداره |
| **Compose** | تعریف چند container با هم در یک فایل | نقشه‌ی کل ساختمان |
| **Registry** | انبار imageها (Docker Hub، یا انبار خودتان) | اپ‌استور |

---

## درس ۰ - آماده‌سازی

```powershell
docker version
docker info
cd 01-docker-lab
```
**باید ببینید:** هم `Client` و هم `Server` در `docker version`. اگر Server خطا داد، Docker Desktop را باز کنید.

> **در ایران:** Docker Hub و PyPI ممکن است بسته یا کند باشند.
> - برای image‌ها: Docker Desktop ← **Settings ← Docker Engine** ← `"registry-mirrors": ["https://docker.arvancloud.ir"]`
> - برای pip: در buildها `--build-arg PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple` (Compose آن را از `.env` می‌خواند)

---

## درس ۱ - Image و Container

```powershell
docker run hello-world                 # image را می‌گیرد، container می‌سازد، اجرا می‌کند
docker images                          # imageهای روی سیستم
docker ps                              # containerهای در حال اجرا
docker ps -a                           # همه، حتی خاموش‌ها
docker run -it --rm python:3.12-slim python
```
آخری شما را **داخل پایتونِ یک container** می‌برد. بنویسید `import platform; platform.platform()` - می‌بینید Linux است، نه Windows! با `exit()` خارج شوید.

- `-it` = محاوره‌ای (ترمینال)
- `--rm` = بعد از خروج، container را پاک کن

```powershell
docker ps -a                           # container خاموش hello-world هنوز هست
docker rm <CONTAINER_ID>               # پاکش کنید (۳-۴ حرف اول ID کافی است)
```
**تمرین:** `docker run -it --rm alpine sh` را اجرا کنید و `ls /` و `cat /etc/os-release` را بزنید.

---

## درس ۲ - پورت، پس‌زمینه، لاگ، رفتن داخل container

```powershell
docker run -d -p 8080:80 --name web nginx:alpine
```
- `-d` = در پس‌زمینه (detached)
- `-p 8080:80` = پورت **8080 ویندوز** ← پورت **80 container**
- `--name web` = اسم، به جای ID

مرورگر: **http://localhost:8080** ← صفحه‌ی Welcome to nginx.

```powershell
docker logs web                        # لاگ‌ها (صفحه را refresh کنید و دوباره ببینید)
docker logs -f web                     # دنبال کردن زنده (Ctrl+C برای خروج)
docker exec -it web sh                 # رفتن داخل container در حال اجرا
#   داخل: echo "<h1>Salam Docker</h1>" > /usr/share/nginx/html/index.html ; exit
docker stop web
docker start web
docker rm -f web                       # توقف + حذف با هم
```
**نکته‌ی مهم:** تغییری که داخل container دادید با `rm` **از بین رفت**. container موقتی است ← برای همین volume داریم (درس ۶).

---

## درس ۳ - اولین Dockerfile خودتان

`Dockerfile` را باز کنید و توضیح هر خط را بخوانید. بعد:

```powershell
docker build -t docker-lab:1.0 .       # نقطه‌ی آخر = همین پوشه
# با Mirror:  docker build --build-arg PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple -t docker-lab:1.0 .
docker images docker-lab
docker history docker-lab:1.0          # لایه‌های image
docker run -d -p 8000:8000 --name lab docker-lab:1.0
```
- http://localhost:8000 ← `container_hostname` همان ID container است (`docker ps` را مقایسه کنید)
- http://localhost:8000/docs ← Swagger
- http://localhost:8000/health ← database و redis «not configured» هستند (هنوز وصل نیستند)

**آزمایش cache:** یک کلمه در `message` داخل `app/main.py` عوض کنید و دوباره build کنید:
```powershell
docker build -t docker-lab:1.1 .
```
می‌بینید مرحله‌ی `pip install` نوشته `CACHED` و build چند ثانیه طول کشید. چون `requirements.txt` عوض نشده بود.

```powershell
docker rm -f lab
```
**`.dockerignore`:** مثل `.gitignore` است - چیزهایی که نباید داخل image بروند (مخصوصاً `.env` با رمزها).

---

## درس ۴ - متغیرهای محیطی (Environment Variables)

تنظیمات را **داخل image نمی‌گذاریم**؛ موقع اجرا می‌دهیم. یک image، چند محیط (dev/test/prod).

```powershell
docker run -d -p 8000:8000 --name lab -e APP_NAME="Mirzazadeh Lab" -e APP_VERSION=2.0 docker-lab:1.0
```
http://localhost:8000 ← اسم و نسخه عوض شد، بدون build دوباره.

```powershell
docker exec lab env                    # متغیرهای داخل container
docker rm -f lab
```

---

## درس ۵ - شبکه: دو container با هم حرف بزنند

```powershell
docker network create labnet
docker run -d --name redis --network labnet redis:7-alpine
docker run -d -p 8000:8000 --name lab --network labnet -e REDIS_URL=redis://redis:6379/0 docker-lab:1.0
```
- http://localhost:8000/visits ← چند بار refresh کنید، عدد زیاد می‌شود
- http://localhost:8000/health ← `"redis": "ok"`

**نکته‌ی کلیدی:** آدرس Redis شد `redis` (اسم container)، نه `localhost`.
داخل container، `localhost` یعنی **خود همان container**.

```powershell
docker exec -it redis redis-cli GET visits
docker network inspect labnet          # کدام containerها در این شبکه‌اند
```

---

## درس ۶ - Volume: داده‌ها نپرند

```powershell
docker rm -f redis
docker run -d --name redis --network labnet redis:7-alpine
```
http://localhost:8000/visits ← **شمارنده از ۱ شروع شد!** داده با container رفت.

حالا با volume:
```powershell
docker rm -f redis
docker volume create redisdata
docker run -d --name redis --network labnet -v redisdata:/data redis:7-alpine redis-server --appendonly yes
```
چند بار `/visits` را باز کنید، بعد:
```powershell
docker rm -f redis
docker run -d --name redis --network labnet -v redisdata:/data redis:7-alpine redis-server --appendonly yes
```
`/visits` ← **عدد ادامه پیدا کرد.** ✅

```powershell
docker volume ls
docker volume inspect redisdata
# تمیزکاری قبل از درس بعد:
docker rm -f lab redis
docker network rm labnet
docker volume rm redisdata
```

---

## درس ۷ - Docker Compose: همه با یک دستور

درس‌های ۴ تا ۶ را با چند دستور طولانی دستی انجام دادید. Compose همه را در یک فایل می‌نویسد.

```powershell
copy .env.example .env
docker compose up -d --build
docker compose ps                      # هر سه باید healthy / running باشند
```
- http://localhost:8000/health ← هر سه `ok` ✅
- http://localhost:8000/docs ← `POST /notes` را باز کنید، **Try it out**، یک یادداشت بفرستید، بعد `GET /notes`

```powershell
docker compose logs -f api             # لاگ‌های API (Ctrl+C)
docker compose logs db
docker compose exec db psql -U lab -d lab -c "SELECT * FROM notes;"
docker compose exec redis redis-cli GET visits
```

**ماندگاری داده:**
```powershell
docker compose down                    # containerها حذف، volumeها می‌مانند
docker compose up -d
```
`GET /notes` ← یادداشت‌ها هنوز هستند ✅

```powershell
docker compose down -v                 # -v = volumeها هم پاک شوند (همه‌ی داده!)
```

`compose.yaml` را بخوانید: `depends_on` + `healthcheck` باعث می‌شود API صبر کند تا دیتابیس واقعاً آماده شود.

---

## درس ۷.۵ - شروع پروژه از پوشه‌ی خالی (سه روش)

یک برنامه‌ی Todo ساده (`main.py` + `requirements.txt`) در سه پوشه‌ی جدا، به سه روش Docker-ی شد:

| پوشه | روش |
|---|---|
| [`../02-from-scratch/todo-manual`](../02-from-scratch/todo-manual) | دستی: Dockerfile و compose.yaml را خودتان می‌نویسید |
| [`../02-from-scratch/todo-init`](../02-from-scratch/todo-init) | `docker init` (سؤال می‌پرسد و ۴ فایل می‌سازد) |
| [`../02-from-scratch/todo-vscode`](../02-from-scratch/todo-vscode) | افزونه‌ی VS Code: `Ctrl+Shift+P` ← **Containers: Add Docker Files to Workspace** |

**مسیر درست شروع یک پروژه:**
1. کد را بنویسید و **اول بدون Docker** تست کنید (`uvicorn main:app`)
2. Dockerfile (دستی یا با ابزار) ← **خروجی ابزار را خط به خط بخوانید**
3. `.dockerignore`
4. build و run دستی
5. `compose.yaml`

**مقایسه:**

| موضوع | دستی | docker init | افزونه‌ی VS Code |
|---|---|---|---|
| نسخه‌ی پایتون | `3.12-slim` ✅ | `3.12.9-slim` (قفل ولی قدیمی) | `3-slim` ❌ (بی‌صدا 3.15 شد) |
| `WORKDIR` قبل از `COPY` | ✅ | ✅ | ❌ |
| کاربر غیر root | ❌ | ✅ قبل از کپی کد | ✅ بعد از کپی (حجم اضافه) |
| کش pip | `--no-cache-dir` | `--mount=type=cache` ⭐ | — |
| `CMD` | exec ✅ | shell ⚠ | exec، ولی gunicorn نصب نبود ❌ |
| Mirror | ✅ | ❌ | ❌ |
| مزیت خاص | کنترل کامل | نمونه‌ی دیتابیس با secrets | `compose.debug.yaml` برای دیباگ |

**درس‌های کلیدی:**
- `COPY . .` ← نقطه‌ی اول = پوشه‌ی پروژه روی **ویندوز**، نقطه‌ی دوم = `WORKDIR` **داخل container**. دو سیستم فایل جدا.
- `WORKDIR /app` یک قرارداد است (می‌تواند `/code` یا `/src` باشد)، ولی **هرگز** کد را در `/` نریزید.
- `--host 0.0.0.0` در container الزامی است؛ `127.0.0.1` یعنی «فقط خود container».
- `.dockerignore` جلوی کپی شدن `__pycache__`، `.env`، `.git` و `venv` را می‌گیرد؛ `PYTHONDONTWRITEBYTECODE=1` جلوی ساخته شدن `__pycache__` **داخل** container را.
- tag کلی (`3-slim`) = image بی‌خبر عوض می‌شود. همیشه نسخه را مشخص کنید.
- خطای `executable file not found in $PATH` = برنامه‌ی `CMD` نصب نیست. Docker محتوای `CMD` را موقع build چک نمی‌کند.
- اسم image در `compose.yaml` باید **یکتا** باشد؛ دو پروژه با یک اسم image همدیگر را رونویسی می‌کنند.
- ابزارهای خودکار نقطه‌ی شروع‌اند، نه پایان.

**Dockerfile ترکیبی (بهترین‌های هر سه):**
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120

WORKDIR /app

ARG UID=10001
RUN adduser --disabled-password --gecos "" --no-create-home --uid ${UID} appuser

ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## درس ۸ - حالت توسعه (کد را عوض کن، بلافاصله ببین)

```powershell
docker compose -f compose.yaml -f compose.dev.yaml up --build
```
حالا `app/main.py` را باز کنید، متن `message` را تغییر دهید و **Save** کنید.
در لاگ می‌بینید `Reloading...` ← http://localhost:8000 را refresh کنید. **بدون build دوباره!**

این کار **bind mount** است: پوشه‌ی `app` ویندوز مستقیم داخل container دیده می‌شود.
با `Ctrl+C` (**یک بار**، و صبر کنید تا دیتابیس تمیز بسته شود) متوقف کنید.

- `-f` دوم روی اولی می‌نشیند و فقط تغییرات را اضافه می‌کند.
- در ویندوز `WATCHFILES_FORCE_POLLING=true` لازم است، وگرنه تغییر فایل از `D:\` به لینوکس container نمی‌رسد.
- **تمرین:** یک endpoint جدید (مثل `/time` در `main.py`) را «زنده» اضافه کنید.

| چه چیزی عوض شد؟ | چه کار کنید؟ |
|---|---|
| کد داخل `app/` | هیچ کار! reload خودکار ✨ |
| `requirements.txt` یا `Dockerfile` | `up --build` (`pip install` در `RUN` است = موقع **build**) |
| `compose.yaml` یا `.env` | `up -d` |

| | named volume (درس ۶) | bind mount (درس ۸) |
|---|---|---|
| نوشتن | `redisdata:/data` | `./app:/app/app` |
| کجاست | داخل Docker | پوشه‌ی شما |
| کاربرد | **داده** | **کد** (فقط در توسعه) |

---

## درس ۹ - عیب‌یابی (Debugging)

```powershell
docker compose up -d
docker stats                           # مصرف CPU / RAM زنده (Ctrl+C)
docker compose top                     # پروسه‌های داخل containerها
docker inspect docker-lab-api-1        # همه‌ی جزئیات (IP، env، mountها ...)
docker compose logs --since 5m api     # لاگ ۵ دقیقه‌ی اخیر
docker compose exec api sh             # رفتن داخل API
#   داخل:  python -c "import socket; print(socket.gethostbyname('db'))"   ← IP دیتابیس
#          exit
```
**تمرین خرابکاری:** در `.env` رمز `DATABASE_URL` را اشتباه کنید ← `docker compose up -d` ←
`/health` و `docker compose logs api` را ببینید. بعد درستش کنید.

**روش عیب‌یابی (از بالا به پایین):**

| لایه | ابزار | سؤال |
|---|---|---|
| ۱. کاربر | مرورگر، `/health` | چه چیزی خراب به نظر می‌رسد؟ |
| ۲. وضعیت | `docker compose ps`، `inspect --format "{{.State.Status}} {{.RestartCount}}"` | روشن است؟ مدام restart می‌شود؟ |
| ۳. لاگ‌ها | `logs --tail 20`، `--since 5m`، `-t` | **هر دو طرف** چه می‌گویند؟ |
| ۴. تنظیمات | `inspect --format "{{json .Config.Env}}"` | container واقعاً چه چیزی گرفته؟ |
| ۵. منابع | `docker stats`، `docker compose top` | رم/CPU پر شده؟ چه processهایی اجرا می‌شوند؟ |
| ۶. داخل | `exec ... sh`، `getent hosts db` | از داخل container، دنیا چطور دیده می‌شود؟ |

**نکته‌ها:**
- اگر فقط سمت API خطا هست و سمت db چیزی نیست ← درخواست **نرسیده** (شبکه/اسم). اگر db هم `FATAL` دارد ← رسیده ولی **رد شده** (رمز/دسترسی).
- تلاش دوباره (retry) برای خطای **موقتی** است (دیتابیس هنوز آماده نیست)، نه **دائمی** (رمز غلط).
- `POSTGRES_PASSWORD` و مشابه‌ها تنظیمات «روز تولد» هستند: فقط روی volume خالی اعمال می‌شوند.
- `env_file: .env` **همه‌ی** متغیرها را به سرویس می‌دهد؛ هر سرویس فقط باید چیزی را بگیرد که لازم دارد.

---

## درس ۱۰ - Image حرفه‌ای برای Production

`Dockerfile.prod` را بخوانید: **multi-stage**، کاربر **غیر root**، و **HEALTHCHECK**.

| ضعف قبلی | راه حل |
|---|---|
| برنامه با **root** اجرا می‌شود (`compose top`) | `useradd` + `USER appuser` |
| Docker نمی‌فهمد برنامه سالم است | `HEALTHCHECK` + `/health` که در خرابی کد **503** برمی‌گرداند |
| ابزارهای build در image نهایی می‌مانند | **multi-stage** (`COPY --from=builder`) |

```powershell
docker compose up -d
docker build -f Dockerfile.prod --build-arg PIP_INDEX_URL=https://package-mirror.liara.ir/repository/pypi/simple -t docker-lab:prod .
docker images docker-lab               # اندازه‌ها را مقایسه کنید
docker run -d -p 8001:8000 --name labprod --network docker-lab_default --env-file .env docker-lab:prod
```
- http://localhost:8001 ← `running_as_user` حالا `appuser` است، نه `root` 🔒
- http://localhost:8000 (نسخه‌ی compose) ← `root`

**کاربر محدود در عمل:**
```powershell
docker exec docker-lab-api-1 sh -c "echo hacked > /etc/hacked.txt && echo SUCCESS"   # root: SUCCESS 😱
docker exec labprod sh -c "echo hacked > /etc/hacked.txt && echo SUCCESS"            # appuser: Permission denied 🔒
```

**healthcheck در عمل:**
```powershell
docker ps                              # بعد از ~۲۰ ثانیه: labprod (healthy)
docker rm -f labprod
docker run -d -p 8001:8000 --name labprod --network docker-lab_default --env-file .env -e DATABASE_URL=postgresql://lab:WRONG@db:5432/lab docker-lab:prod
docker ps --filter health=unhealthy    # بعد از ~۱ دقیقه: labprod (unhealthy)
docker inspect labprod --format "{{json .State.Health}}"
docker rm -f labprod
```

**آخر درس:** در `compose.yaml` خط `# dockerfile: Dockerfile.prod` را از کامنت دربیاورید ← `docker compose up -d --build` ← هر سه سرویس `(healthy)`.

**نکته‌ها:**
- برای این پروژه multi-stage حجم را **کم نکرد** (هیچ ابزار کامپایلی برای دور ریختن نبود). در پروژه‌های Go یا وقتی `gcc` لازم است، تفاوت بسیار بزرگ است. **اندازه بگیرید، کورکورانه به کار نبرید.**
- Docker خودش container ناسالم را **restart نمی‌کند**؛ `unhealthy` فقط برچسب است (برای `depends_on`، مانیتورینگ، Swarm/Kubernetes).

---

## درس ۱۱ - Registry: انبار image خودتان

Docker Hub از ایران محدود است؛ یک registry محلی می‌سازیم (شرکت‌ها هم همین کار را می‌کنند):

```powershell
docker run -d -p 5000:5000 --name registry registry:2
docker tag docker-lab:compose localhost:5000/docker-lab:1.0
docker push localhost:5000/docker-lab:1.0
docker rmi localhost:5000/docker-lab:1.0                    # از سیستم پاک کنید
docker pull localhost:5000/docker-lab:1.0                    # دوباره از انبار بگیرید
```
مرورگر: http://localhost:5000/v2/_catalog ← لیست imageهای انبار.

```powershell
docker rm -f registry
```

---

## درس ۱۲ - تمیزکاری

```powershell
docker compose down -v
docker system df                       # Docker چقدر فضا گرفته
docker container prune                 # containerهای خاموش
docker image prune                     # imageهای بی‌استفاده
docker image prune -a                  # همه‌ی imageهایی که container روشنی ندارند
docker builder prune                   # cache buildها (معمولاً بیشترین فضا)
docker system prune                    # همه‌ی موارد بالا (با تأیید)
```
پاک کردن image‌ها گاهی فضای کمی آزاد می‌کند، چون image‌ها **لایه‌های مشترک** دارند (مثلاً همه روی `python:3.12-slim`).
⚠ `docker system prune -a --volumes` **همه چیز** را پاک می‌کند - مراقب باشید.

---

## خلاصه‌ی دستورها (Cheat Sheet)

| کار | دستور |
|---|---|
| ساخت image | `docker build -t name:tag .` |
| اجرا | `docker run -d -p HOST:CONT --name x image` |
| لیست | `docker ps -a` / `docker images` |
| لاگ | `docker logs -f x` |
| رفتن داخل | `docker exec -it x sh` |
| توقف / حذف | `docker stop x` / `docker rm -f x` |
| متغیر محیطی | `-e KEY=value` / `--env-file .env` |
| volume | `-v name:/path` (named) / `-v C:\dir:/path` (bind) |
| شبکه | `docker network create n` + `--network n` |
| کل سیستم بالا | `docker compose up -d --build` |
| کل سیستم پایین | `docker compose down` (`-v` = با داده) |
| لاگ compose | `docker compose logs -f service` |
| داخل سرویس | `docker compose exec service sh` |
| فضا | `docker system df` / `docker system prune` |

---

## مشکلات رایج

| مشکل | راه حل |
|---|---|
| `port is already allocated` | پورت دیگری بدهید (`-p 8001:8000`) یا container قبلی را `rm -f` کنید |
| `Conflict. The container name "/x" is already in use` | `docker rm -f x` |
| خطای `403` / `denied` موقع pull | Docker Hub بسته است ← Mirror در Settings → Docker Engine |
| API می‌گوید database error | `docker compose logs db` - رمز `.env` را چک کنید |
| `pip install` داخل build کند است / خطا می‌دهد | اینترنت/پروکسی؛ دوباره build کنید (لایه‌های موفق cache شده‌اند) |
| تغییر کد دیده نمی‌شود | یا دوباره `build` کنید، یا از حالت dev (درس ۸) استفاده کنید. اگر در build مرحله‌ی `COPY` کد `CACHED` بود، فایل ذخیره نشده |
| `cannot find ... dockerDesktopLinuxEngine` | Docker Desktop خاموش است ← بازش کنید و منتظر **Engine running** بمانید |
| `Mirror` با خطای `402 Payment Required` | Mirror پولی شده ← Mirror دیگری (مثلاً لیارا) |
| `pip install` با `Read timed out` | `PIP_DEFAULT_TIMEOUT=120` + Mirror با `--build-arg PIP_INDEX_URL=...` |
| `the Dockerfile cannot be empty` | Dockerfile ذخیره نشده یا محتوا در فایل دیگری است (`dir` و `Get-Content Dockerfile`) |
| `executable file not found in $PATH` | برنامه‌ی `CMD` نصب نیست (مثلاً gunicorn در requirements نیست) |
| `Attribute "app" not found in module "main"` | `main.py` خالی است یا ذخیره نشده |
| `Conflict. The container name ... is already in use` | `docker rm -f <اسم>` |
| `--name` / `docker rm` با اسم image کار نمی‌کند | اسم **container** (ستون NAMES) را بدهید، نه اسم image |
| `password authentication failed` بعد از عوض کردن `POSTGRES_PASSWORD` | این متغیر فقط **بار اول** (volume خالی) اعمال می‌شود. رمز را داخل دیتابیس عوض کنید: `docker compose exec db psql -U lab -d lab -c "ALTER USER lab WITH PASSWORD '...';"` بعد `docker compose restart api` |
| برنامه `running` و `restarts: 0` است ولی کار نمی‌کند | «روشن ولی خراب». لاگ **هر دو طرف** را ببینید (`logs api` و `logs db`) |

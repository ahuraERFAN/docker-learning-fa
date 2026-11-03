# ---------------------------------------------------------------
# Lesson 3: the simplest useful Dockerfile
# Every line = one "layer". Docker caches layers, so the order matters:
# things that change rarely go first, your code (changes often) goes last.
# ---------------------------------------------------------------

# 1) Start from an official image that already has Python
FROM python:3.12-slim

# 2) All next commands run inside /app (created automatically)
WORKDIR /app

# 3) No .pyc files, and print() shows up immediately in `docker logs`.
#    PIP_*: be patient on slow networks (default timeout is only 15s).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ARG = a setting you can change at BUILD time (not saved in the running container).
# pip reads PIP_INDEX_URL automatically. To use a PyPI mirror:
#   docker build --build-arg PIP_INDEX_URL=https://your-mirror/simple -t docker-lab:1.0 .
ARG PIP_INDEX_URL=https://pypi.org/simple

# 4) Copy ONLY requirements first and install them.
#    This layer is cached until requirements.txt changes ->
#    editing your code does NOT reinstall all packages.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Now copy the code
COPY app/ ./app/

# 6) Documentation only: the app listens on 8000 (publishing is done with -p)
EXPOSE 8000

# 7) The command that runs when the container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

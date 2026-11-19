# Ultroid - UserBot
# Copyright (C) 2021-2026 TeamUltroid
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

# OWNER Assistant: builds THIS repo (your code + bundled addons).
FROM python:3.12-slim

ENV TZ=Asia/Kolkata \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git ffmpeg mediainfo curl gcc g++ libffi-dev tzdata \
    && (apt-get install -y --no-install-recommends neofetch || true) \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/OWNER-Assistant

# Install python packages first so code changes don't redo this layer.
COPY requirements.txt ./requirements.txt
COPY resources/startup/optional-requirements.txt ./optional-requirements.txt
COPY addons/addons.txt ./addons-requirements.txt
RUN pip install -r requirements.txt \
    && pip install redis hiredis "pymongo[srv]" psycopg2-binary \
    && for f in optional-requirements.txt addons-requirements.txt; do \
         tr -d '\r' < "$f" | grep -vE '^\s*(#|$)' | while read -r pkg; do \
           pip install "$pkg" || echo "skipped: $pkg"; \
         done; \
       done \
    && rm -f optional-requirements.txt addons-requirements.txt

COPY . .
# addons.txt is already installed above; tell the loader so it skips pip on start
RUN python -c "import hashlib;open('addons/.installed','w').write(hashlib.sha256(open('addons/addons.txt','rb').read()).hexdigest())"

CMD ["bash", "startup"]

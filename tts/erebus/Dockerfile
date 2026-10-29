# PIE pitch-patched Kokoro TTS (pie.speak backend "kokoro") as an HTTP service. CPU only.
# Build context: the staging directory made by tts/erebus/deploy.sh (on erebus: ~/pie-tts/), laid out as
#   Dockerfile requirements.txt server.py pie/{__init__,translit,phon,meter,ipa,speak}.py
#   tts/espeak/mapping.json tts/kokoro/vocab.json
# Docs: docs/pronunciation.md "Deployment on erebus".
FROM python:3.12.13-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HUB_DISABLE_TELEMETRY=1 PIE_KOKORO_CACHE=/opt/pie/cache/hf

RUN useradd --system --uid 10001 --home-dir /opt/pie --no-create-home pie

# torch from the CPU index (the PyPI wheel pulls the CUDA stack), then the exact tested freeze.
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.15.0+cpu
COPY requirements.txt /opt/pie/requirements.txt
RUN pip install --only-binary=:all: -r /opt/pie/requirements.txt

WORKDIR /opt/pie
COPY tts/ /opt/pie/tts/
COPY pie/ /opt/pie/pie/

# Weights: pinned revision, sha256-checked by pie.speak.kokoro_file (the same pins and check a local run uses).
RUN python -I -c "import sys; sys.path.insert(0, '/opt/pie'); from pie import speak as S; \
[print(f, S.kokoro_file(f)) for f in S.KOKORO_FILES]" \
 && chown -R pie:pie /opt/pie/cache

COPY server.py /opt/pie/server.py

USER pie
ENV HF_HUB_OFFLINE=1 PYTHONPATH=/opt/pie OMP_NUM_THREADS=6 PIE_TTS_THREADS=6 PIE_TTS_PORT=8881
EXPOSE 8881
HEALTHCHECK --interval=60s --timeout=5s --start-period=90s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(urllib.request.urlopen('http://127.0.0.1:8881/health', timeout=4).status != 200)"
CMD ["python", "/opt/pie/server.py"]

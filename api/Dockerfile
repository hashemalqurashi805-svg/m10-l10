# 1. اختيار نسخة بايثون خفيفة
FROM python:3.11-slim

# 2. ضبط مجلد العمل ليكون المجلد الرئيسي للمشروع (حتى يرى uvicorn حزمة api)
WORKDIR /app

# 3. نسخ ملف المتطلبات أولاً (لتحسين التخزين المؤقت - Cache)
COPY api/requirements.txt ./api/
RUN pip install --no-cache-dir -r api/requirements.txt

# 4. تحميل نموذج spaCy المطلوب
RUN python -m spacy download en_core_web_sm || pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl

# 5. نسخ باقي ملفات المشروع
COPY . .

# 6. تشغيل التطبيق من مجلد الجذر لضمان نجاح الاستيراد النسبي
# (المنفذ 8000 كما هو مطلوب)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

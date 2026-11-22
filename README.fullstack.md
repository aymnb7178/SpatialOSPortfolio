# تشغيل SpatialOS Portfolio Full-stack

## محلياً

أنشئ بيئة افتراضية ثم ثبّت الاعتمادات من `backend/requirements.txt`. انسخ `backend/.env.example` إلى `backend/.env` وعدّل `DATABASE_URL` و`JWT_SECRET`. عند عدم توفر PostgreSQL يمكن تشغيل التطوير على SQLite بتغيير الرابط إلى `sqlite:///./spatialos-dev.db`.

شغّل الخدمة من جذر المستودع عبر:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

طبّق الجداول قبل أول تشغيل باستخدام `PYTHONPATH=. alembic -c backend/alembic.ini upgrade head`.

افتح `http://127.0.0.1:8000` للواجهة، و`/docs` لتوثيق API، و`/health` للفحص.

## Render

اربط مستودع GitHub في Render واستخدم `render.yaml`. يستخدم الملف Build Command `pip install -r backend/requirements.txt`، ويطبق Alembic migrations قبل Start Command `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`. يجب أن تكون قاعدة PostgreSQL والخدمة في نفس المنطقة، وتستخدم الخدمة `internalConnectionString`.

بعد إنشاء الخدمة، أضف `ADMIN_EMAIL` و`GEMINI_API_KEY` و`MOYASAR_SECRET_KEY` و`MOYASAR_WEBHOOK_SECRET` من لوحة Render. لا تضع مفتاح Gemini أو مفاتيح Moyasar في GitHub أو داخل `.env.example`. اترك `MOYASAR_LIVE=false`؛ تكامل الدفع مجهز برمجيًا فقط وليس تفعيلًا للدفع الحقيقي.

## API مختصر

`POST /api/auth/register` و`POST /api/auth/login` للحسابات، `POST /api/messages` لحفظ رسائل العملاء، و`POST /api/orders` و`GET /api/orders` لطلبات المستخدم. المساعد المتقدم يعمل عبر `POST /api/assistant/chat` ويستدعي Gemini من Backend فقط، بينما تبقى الواجهة على مساعد محلي احتياطي عند الفشل أو انتهاء الحصة. يتطلب إنشاء الدفع تسجيل الدخول عبر `POST /api/payments/create`. لوحة التحكم متاحة للمستخدم ذي الدور `admin` على `/api/admin/*`.

## Gemini والمجانية

اضبط `GEMINI_API_KEY` كمتغير سري في Render فقط، ويمكن تغيير النموذج عبر `GEMINI_MODEL` (القيمة الحالية `gemini-2.5-flash`). لا يظهر المفتاح في `index.html` أو GitHub، ولا تحفظ المحادثات في قاعدة بيانات الموقع. يوجد حد مؤقت يقارب 20 طلبًا لكل عنوان IP خلال ساعة، وتعود الواجهة إلى المساعد المحلي إذا لم يتوفر المفتاح أو فشل الاتصال أو انتهت الحصة. استخدام Gemini يخضع لحصته المجانية لدى Google؛ عدم وجود بطاقة لا يعني مجانية غير محدودة، لذلك لا يفعّل المشروع Billing أو بطاقة أو ترقية Render.

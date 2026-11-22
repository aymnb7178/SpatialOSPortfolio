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

بعد إنشاء الخدمة، أضف `ADMIN_EMAIL` و`MOYASAR_SECRET_KEY` و`MOYASAR_WEBHOOK_SECRET` من لوحة Render عند الحاجة. لا تضع مفاتيح Moyasar في GitHub أو داخل `.env.example`. اترك `MOYASAR_LIVE=false`؛ تكامل الدفع مجهز برمجيًا فقط وليس تفعيلًا للدفع الحقيقي.

## API مختصر

`POST /api/auth/register` و`POST /api/auth/login` للحسابات، `POST /api/messages` لحفظ رسائل العملاء، و`POST /api/orders` و`GET /api/orders` لطلبات المستخدم. المساعد المحلي يعمل داخل `index.html` من قاعدة معرفة منظمة، مع تصنيف نوايا وفهم للمتابعة، ولا يحتاج API. يتطلب إنشاء الدفع تسجيل الدخول عبر `POST /api/payments/create`. لوحة التحكم متاحة للمستخدم ذي الدور `admin` على `/api/admin/*`.

## المساعد المحلي

المساعد يعمل داخل المتصفح بدون Gemini أو OpenAI أو أي API خارجي، لذلك لا يحتاج بطاقة أو Billing ولا يرسل محادثات الزوار إلى مزود خارجي. يعتمد على قاعدة معرفة عن أيمن والموقع، وتطبيع للعربية، ودرجات نوايا، وفهم لأسئلة المتابعة، ويفتح أقسام الأعمال والخدمات والتواصل عند الطلب. لا يدّعي معرفة ما ليس موجودًا في قاعدة المعرفة؛ وعند السؤال خارج نطاقه يطلب من الزائر إعادة صياغة السؤال أو التواصل مع أيمن.

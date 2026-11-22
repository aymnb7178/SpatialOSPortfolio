# خطة تحويل SpatialOS Portfolio إلى Full-stack

## القرار التنفيذي

سنحافظ على واجهة `index.html` الحالية ونضيف خدمة FastAPI واحدة تخدم الـ API والملفات الثابتة من نفس النطاق. ستستخدم الخدمة PostgreSQL عبر SQLAlchemy وAlembic، وتخزن جلسة JWT داخل HttpOnly cookie. ستبقى مفاتيح Moyasar وJWT وقاعدة البيانات خارج GitHub عبر متغيرات بيئية في Render.

## التصميم

الأسلوب المختار هو **الاستوديو التقني الداكن**: خلفية Obsidian، أزرق cobalt للروابط والحالات، ولمسات lime للإجراءات الناجحة. المبادئ هي الوضوح، الثقة، تقليل الحركة غير الضرورية، وإبراز حالات الطلب والدفع. لوحة التحكم ستكون عملية ومباشرة دون زخرفة إضافية.

الهوية الحالية للموقع هي Portfolio عربي/إنجليزي عملي لصاحب مشاريع Python والبيانات والأتمتة. نبرة النصوص مهنية ومباشرة مثل: «أرسل تفاصيل مشروعك» و«تابع حالة طلبك من حسابك».

## الهيكل

- `backend/app/main.py`: إنشاء FastAPI وخدمة الملفات والفحص الصحي.
- `backend/app/config.py`: إعدادات البيئة.
- `backend/app/database.py`: محرك PostgreSQL والجلسات.
- `backend/app/models.py`: المستخدمون والرسائل والطلبات والمدفوعات.
- `backend/app/auth.py`: تجزئة كلمات المرور وJWT والصلاحيات.
- `backend/app/moyasar.py`: عميل Moyasar مع Basic Auth.
- `backend/app/routers/`: auth/messages/orders/payments/admin.
- `backend/alembic/`: إعداد migrations.
- `render.yaml`: Web Service وPostgreSQL على Render.
- `backend/tests/`: اختبارات المسارات العامة.

## القيود

Moyasar يحتاج حساب تاجر ومفاتيح test/live. لن تُقبل بيانات البطاقة أو المفاتيح في المحادثة أو GitHub؛ تُرسل بيانات الدفع من واجهة دفع آمنة إلى Moyasar عند التشغيل، ويستقبل الخادم webhooks مع secret token. قبل التحويل إلى live يجب اختبار test mode ثم ضبط `MOYASAR_LIVE=false/true` بحسب المفتاح.

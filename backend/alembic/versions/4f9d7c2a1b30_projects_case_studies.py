"""add editable project case studies

Revision ID: 4f9d7c2a1b30
Revises: 8b7a6f2c1d90, 9c4d2e7f1a30
"""
from typing import Sequence, Union
import json
from alembic import op
import sqlalchemy as sa

revision: str = "4f9d7c2a1b30"
down_revision: Union[str, tuple[str, str], None] = ("8b7a6f2c1d90", "9c4d2e7f1a30")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("title_ar", sa.String(length=160), nullable=False, server_default=""),
        sa.Column("eyebrow", sa.String(length=120), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("summary_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("overview", sa.Text(), nullable=False, server_default=""),
        sa.Column("overview_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("problem", sa.Text(), nullable=False, server_default=""),
        sa.Column("problem_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("solution", sa.Text(), nullable=False, server_default=""),
        sa.Column("solution_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("features_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("technologies_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("architecture", sa.Text(), nullable=False, server_default=""),
        sa.Column("architecture_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("challenges", sa.Text(), nullable=False, server_default=""),
        sa.Column("challenges_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("results", sa.Text(), nullable=False, server_default=""),
        sa.Column("results_ar", sa.Text(), nullable=False, server_default=""),
        sa.Column("hero_media_url", sa.String(length=1000), nullable=False, server_default=""),
        sa.Column("media_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("github_url", sa.String(length=1000), nullable=False, server_default=""),
        sa.Column("demo_url", sa.String(length=1000), nullable=False, server_default=""),
        sa.Column("related_slugs_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_visible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=True)

    projects = sa.table(
        "projects",
        sa.column("slug", sa.String), sa.column("title", sa.String), sa.column("title_ar", sa.String),
        sa.column("eyebrow", sa.String), sa.column("category", sa.String), sa.column("summary", sa.Text), sa.column("summary_ar", sa.Text),
        sa.column("overview", sa.Text), sa.column("overview_ar", sa.Text), sa.column("problem", sa.Text), sa.column("problem_ar", sa.Text),
        sa.column("solution", sa.Text), sa.column("solution_ar", sa.Text), sa.column("features_json", sa.Text), sa.column("technologies_json", sa.Text),
        sa.column("architecture", sa.Text), sa.column("architecture_ar", sa.Text), sa.column("challenges", sa.Text), sa.column("challenges_ar", sa.Text),
        sa.column("results", sa.Text), sa.column("results_ar", sa.Text), sa.column("github_url", sa.String), sa.column("related_slugs_json", sa.Text),
        sa.column("is_featured", sa.Boolean), sa.column("is_visible", sa.Boolean), sa.column("sort_order", sa.Integer),
    )
    op.bulk_insert(projects, [
        dict(slug="jarvis", title="J.A.R.V.I.S / SpatialOS", title_ar="J.A.R.V.I.S / SpatialOS", eyebrow="01 // SPATIAL INTERACTION", category="spatial-computing", summary="A Python webcam-driven holographic 3D workspace with a rule-based bilingual J.A.R.V.I.S. core.", summary_ar="مساحة عمل ثلاثية الأبعاد تعتمد على كاميرا الويب، مع نواة J.A.R.V.I.S ثنائية اللغة قائمة على القواعد.", overview="The public repository describes hand gestures for grabbing, rotating, scaling, splitting and pinning 3D models rendered on a camera feed.", overview_ar="يصف المستودع العام إمساك المجسمات ثلاثية الأبعاد وتدويرها وتغيير حجمها وتقسيمها وتثبيتها عبر إيماءات اليد فوق بث الكاميرا.", problem="Exploring spatial interaction needs a clear bridge between camera input, gestures, rendering and command handling.", problem_ar="يحتاج استكشاف التفاعل المكاني إلى جسر واضح بين إدخال الكاميرا والإيماءات والعرض ومعالجة الأوامر.", solution="A modular Python workstation connects hand tracking, gesture state, physics, rendering, bilingual rule-based NLU, tools, agents and SQLite memory.", solution_ar="محطة عمل Python معيارية تربط تتبع اليد وحالة الإيماءات والفيزياء والعرض وفهم اللغة القائم على القواعد والأدوات والوكلاء وذاكرة SQLite.", features_json=json.dumps(["Hand tracking and gesture state", "Four XR workspaces", "Rule-based Arabic/English commands", "SQLite memory", "15-agent registry"], ensure_ascii=False), technologies_json=json.dumps(["Python", "OpenCV", "MediaPipe", "SQLite", "Computer Vision"], ensure_ascii=False), architecture="Webcam → hand tracking → gesture engine → physics → renderer. Microphone/text → bilingual dialog → rule-based NLU → tools and agents → SQLite memory.", architecture_ar="كاميرا الويب ← تتبع اليد ← محرك الإيماءات ← الفيزياء ← العارض. الميكروفون/النص ← حوار ثنائي اللغة ← فهم لغة قائم على القواعد ← أدوات ووكلاء ← ذاكرة SQLite.", challenges="The repository documents smoothing, prediction and gesture-state handling as separate modules. Live camera, voice and OCR behavior is author-reported rather than independently reproduced.", challenges_ar="يوثق المستودع فصل التنعيم والتنبؤ وحالة الإيماءات في وحدات مستقلة. أما سلوك الكاميرا والصوت وOCR المباشر فهو مذكور كتجربة للمؤلف ولم يُعاد التحقق منه مستقلاً.", results="The README reports 16 automated tests passing and explicitly makes no performance claim.", results_ar="يذكر README نجاح 16 اختباراً آلياً، ويؤكد صراحة عدم وجود رقم أداء مُعلن.", github_url="https://github.com/aymnb7178/SpatialOS-JARVIS-Workstation", related_slugs_json=json.dumps(["signbridge", "nira"]), is_featured=True, is_visible=True, sort_order=1),
        dict(slug="signbridge", title="SignBridge AI", title_ar="SignBridge AI", eyebrow="02 // ACCESSIBILITY & VISION", category="computer-vision", summary="A focused, rule-based hand-gesture recognition prototype using MediaPipe landmarks.", summary_ar="نموذج أولي محدود للتعرف القائم على القواعد على إيماءات اليد باستخدام نقاط MediaPipe.", overview="MediaPipe detects 21 hand landmarks, geometry decides which fingers are extended, and a debounced sentence builder turns held gestures into demo words.", overview_ar="يكتشف MediaPipe 21 نقطة لليد، وتحدد الهندسة الأصابع الممدودة، ثم يحول مُنشئ الجمل المؤجل الإيماءات الثابتة إلى كلمات تجريبية.", problem="A small educational prototype needs a transparent baseline before introducing trained models or broader language claims.", problem_ar="يحتاج النموذج التعليمي الصغير إلى أساس شفاف قبل إدخال نماذج مدربة أو ادعاءات لغوية أوسع.", solution="A pure-Python rule set classifies a documented ten-word demo vocabulary and exposes a webcam path that is clearly marked as not live-tested.", solution_ar="يصنف نظام قواعد مكتوب بـPython مفردات تجريبية من عشر كلمات، مع توضيح أن مسار الكاميرا لم يُختبر مباشرة.", features_json=json.dumps(["21-landmark hand features", "Geometry-based finger states", "Debounced sentence builder", "10-word demo vocabulary"], ensure_ascii=False), technologies_json=json.dumps(["Python", "MediaPipe", "OpenCV", "Rule-based Recognition"], ensure_ascii=False), architecture="Webcam → MediaPipe landmarks → finger-state features → rule classifier → debounced sentence builder.", architecture_ar="كاميرا الويب ← نقاط MediaPipe ← خصائص حالة الأصابع ← مصنف قواعد ← منشئ جمل مؤجل.", challenges="The README limits scope to static poses, one palm-facing hand and fixed thresholds; rotated hands, motion signs and accuracy are not covered.", challenges_ar="يحدد README النطاق في وضعيات ثابتة ويد واحدة مواجهة للكاميرا وعتبات ثابتة؛ ولا يغطي الأيدي المائلة أو الإشارات الحركية أو الدقة.", results="The repository reports 10 unit tests for pure-Python components. It claims no accuracy figure and says the webcam app was not tested live.", results_ar="يذكر المستودع 10 اختبارات وحدات للمكونات المكتوبة بـPython، ولا يعلن رقماً للدقة ويقول إن تطبيق الكاميرا لم يُختبر مباشرة.", github_url="https://github.com/aymnb7178/SignBridge-AI", related_slugs_json=json.dumps(["jarvis", "nira"]), is_featured=True, is_visible=True, sort_order=2),
        dict(slug="nira", title="Nira Personal AI Agent", title_ar="Nira Personal AI Agent", eyebrow="03 // AUTOMATION & AI AGENTS", category="automation", summary="A Telegram bot example that routes commands, optional Gemini questions and n8n webhooks.", summary_ar="مثال على بوت Telegram يوجه الأوامر وأسئلة Gemini الاختيارية وطلبات n8n.", overview="The public repository separates a small Python bot from sanitized n8n workflow exports and describes a human approval gate for outward actions.", overview_ar="يفصل المستودع العام بوت Python الصغير عن ملفات n8n المنقحة، ويصف بوابة موافقة بشرية للإجراءات الخارجية.", problem="Automation needs explicit routing, error handling and approval boundaries instead of silently executing outward actions.", problem_ar="تحتاج الأتمتة إلى توجيه واضح ومعالجة أخطاء وحدود موافقة بدلاً من تنفيذ الإجراءات الخارجية بصمت.", solution="A standard-library Python bot handles Telegram commands, optional Gemini REST requests and n8n webhook forwarding with redaction and mocked tests.", solution_ar="يعالج بوت Python من المكتبة القياسية أوامر Telegram وطلبات Gemini REST الاختيارية وتمرير Webhook إلى n8n مع إخفاء الأسرار واختبارات وهمية.", features_json=json.dumps(["Telegram command routing", "Optional Gemini REST path", "n8n webhook forwarding", "Long-message splitting", "Token redaction", "Approval-gated workflows"], ensure_ascii=False), technologies_json=json.dumps(["Python", "Telegram", "n8n", "Gemini", "Webhooks"], ensure_ascii=False), architecture="Telegram update → command router → Gemini or n8n adapter → response. Polling loop tracks offsets and uses back-off.", architecture_ar="تحديث Telegram ← موجه الأوامر ← محول Gemini أو n8n ← الاستجابة. يتتبع حلقة الاستطلاع الإزاحات وتستخدم التراجع التدريجي.", challenges="The README explicitly says real Telegram, n8n and Gemini services were not tested by the author; external integrations remain editable and unverified.", challenges_ar="يؤكد README أن خدمات Telegram وn8n وGemini الحقيقية لم يختبرها المؤلف؛ لذلك تبقى التكاملات الخارجية قابلة للتحرير وغير متحقق منها.", results="The repository reports 14 tests using mocked HTTP and makes no live-integration or production result claim.", results_ar="يذكر المستودع 14 اختباراً باستخدام HTTP وهمي، ولا يدعي نتيجة تكامل مباشر أو نتيجة إنتاجية.", github_url="https://github.com/aymnb7178/Telegram-AI-Automation", related_slugs_json=json.dumps(["jarvis", "signbridge"]), is_featured=True, is_visible=True, sort_order=3),
    ])


def downgrade() -> None:
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_table("projects")

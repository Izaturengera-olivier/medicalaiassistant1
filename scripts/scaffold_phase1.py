"""One-shot Phase 1 file generator. Safe to re-run; overwrites known scaffold files."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

APPS = [
    ("accounts", "User accounts, roles, JWT-facing identity."),
    ("patients", "Patient profiles and medical history."),
    ("doctors", "Doctor profiles and assigned-patient access."),
    ("pharmacists", "Pharmacist profiles and prescription access."),
    ("consultations", "Consultations, symptoms, follow-up questions."),
    ("medical", "Condition catalog and clinical reference entities."),
    ("medications", "Medication catalog, interactions, prescriptions."),
    ("ai", "LLM interfaces, structured assessment, triage."),
    ("knowledge", "Approved sources, documents, chunks, embeddings."),
    ("audit", "Immutable audit log for access and AI events."),
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    if not content.endswith("\n"):
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


def app_files(name: str, purpose: str) -> None:
    app = BACKEND / name
    class_name = "".join(part.title() for part in name.split("_")) + "Config"
    write(
        app / "__init__.py",
        "",
    )
    write(
        app / "apps.py",
        f'''from django.apps import AppConfig


class {class_name}(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "{name}"
    verbose_name = "{name.replace("_", " ").title()}"
''',
    )
    write(
        app / "models.py",
        f'''"""Domain models for {name}. Implemented in Phase 2.

{purpose}
"""

from django.db import models  # noqa: F401
''',
    )
    write(
        app / "admin.py",
        f'''"""Admin registrations for {name}. Populated in later phases."""
''',
    )
    write(
        app / "serializers.py",
        f'''"""DRF serializers for {name}. Implemented with APIs in later phases."""
''',
    )
    write(
        app / "permissions.py",
        f'''"""Object-level and role permissions for {name}. Phase 3+."""
''',
    )
    write(
        app / "views.py",
        f'''"""HTTP endpoints for {name}. Implemented in later phases."""
''',
    )
    write(
        app / "urls.py",
        f'''from django.urls import path

urlpatterns: list = []
''',
    )
    write(
        app / "validators.py",
        f'''"""Input validators for {name}."""
''',
    )
    write(app / "services" / "__init__.py", f'''"""Service layer for {name}. Keep business logic out of views."""\n''')
    write(app / "tests" / "__init__.py", "")
    write(
        app / "tests" / "test_app_loads.py",
        f'''from django.apps import apps


def test_{name}_app_is_installed():
    assert apps.is_installed("{name}")
''',
    )


def main() -> None:
    for name, purpose in APPS:
        app_files(name, purpose)

    write(
        BACKEND / "manage.py",
        '''#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Is the virtualenv active and requirements installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
''',
    )

    write(BACKEND / "config" / "__init__.py", "")
    write(
        BACKEND / "config" / "asgi.py",
        '''import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
application = get_asgi_application()
''',
    )
    write(
        BACKEND / "config" / "wsgi.py",
        '''import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
application = get_wsgi_application()
''',
    )
    write(
        BACKEND / "config" / "urls.py",
        '''from django.contrib import admin
from django.urls import include, path

from config.health import HealthView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthView.as_view(), name="health"),
    path("api/schema/", include("config.schema_urls")),
    path("api/auth/", include("accounts.urls")),
    path("api/patients/", include("patients.urls")),
    path("api/doctors/", include("doctors.urls")),
    path("api/pharmacists/", include("pharmacists.urls")),
    path("api/consultations/", include("consultations.urls")),
    path("api/medical/", include("medical.urls")),
    path("api/medications/", include("medications.urls")),
    path("api/ai/", include("ai.urls")),
    path("api/knowledge/", include("knowledge.urls")),
    path("api/audit/", include("audit.urls")),
]
''',
    )
    write(
        BACKEND / "config" / "schema_urls.py",
        '''from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
''',
    )
    write(
        BACKEND / "config" / "health.py",
        '''from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Unauthenticated liveness check. Does not query patient data."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "clinical-cds",
                "phase": 1,
                "disclaimer": (
                    "Decision-support system only. Not a substitute for professional "
                    "diagnosis, prescription, or treatment."
                ),
            }
        )
''',
    )
    write(BACKEND / "config" / "settings" / "__init__.py", "")
    write(
        BACKEND / "config" / "settings" / "base.py",
        '''import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BASE_DIR.parent

load_dotenv(REPO_ROOT / ".env")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "unsafe-dev-only-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "accounts",
    "patients",
    "doctors",
    "pharmacists",
    "consultations",
    "medical",
    "medications",
    "ai",
    "knowledge",
    "audit",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

_database_url = os.environ.get("DATABASE_URL", "")
if _database_url.startswith("postgres"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "cds"),
            "USER": os.environ.get("POSTGRES_USER", "cds_user"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "cds_password"),
            "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
    # Parse simple postgres://user:pass@host:port/db URLs without extra deps.
    try:
        from urllib.parse import urlparse

        parsed = urlparse(_database_url)
        if parsed.hostname:
            DATABASES["default"].update(
                {
                    "NAME": parsed.path.lstrip("/") or "cds",
                    "USER": parsed.username or "cds_user",
                    "PASSWORD": parsed.password or "",
                    "HOST": parsed.hostname,
                    "PORT": str(parsed.port or 5432),
                }
            )
    except ValueError:
        pass
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [("en", "English"), ("rw", "Kinyarwanda")]
TIME_ZONE = "Africa/Kigali"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "15"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", "7"))),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Clinical CDS API",
    "DESCRIPTION": (
        "Clinical decision-support API. Not a diagnostic or prescribing system. "
        "Healthcare professionals remain responsible for clinical decisions."
    ),
    "VERSION": "0.1.0",
}

AI_PROVIDER = os.environ.get("AI_PROVIDER", "mock")
AI_API_KEY = os.environ.get("AI_API_KEY", "")
AI_MODEL = os.environ.get("AI_MODEL", "gpt-4o-mini")
EMBEDDING_PROVIDER = os.environ.get("EMBEDDING_PROVIDER", "mock")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
VECTOR_BACKEND = os.environ.get("VECTOR_BACKEND", "pgvector")
''',
    )
    write(
        BACKEND / "config" / "settings" / "development.py",
        '''from .base import *  # noqa: F403

DEBUG = True
''',
    )
    write(
        BACKEND / "config" / "settings" / "production.py",
        '''from .base import *  # noqa: F403

DEBUG = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
''',
    )
    write(
        BACKEND / "config" / "settings" / "test.py",
        '''from .base import *  # noqa: F403

DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
''',
    )
    write(
        BACKEND / "ai" / "providers.py",
        '''"""Pluggable LLM provider interface. Real providers are wired in Phase 6."""

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Deterministic stub so later phases can develop without an API key."""

    def complete_structured(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "symptoms_identified": [],
            "follow_up_questions": [
                "How long have you had these symptoms?",
            ],
            "possible_conditions": [],
            "warning_signs": [],
            "urgency_level": "INFORMATIONAL",
            "general_information": (
                "This is a mock response used until an LLM provider is configured. "
                "It is not medical advice and is not a diagnosis."
            ),
            "medication_information": [],
            "recommended_next_step": "Consult a qualified healthcare professional.",
            "sources": [],
        }


def get_llm_provider(name: str) -> LLMProvider:
    if name == "mock":
        return MockLLMProvider()
    raise NotImplementedError(f"LLM provider {name!r} is not configured yet.")
''',
    )
    write(
        BACKEND / "knowledge" / "retrievers.py",
        '''"""Pluggable medical retrieval interface. Implementations land in Phase 7."""

from abc import ABC, abstractmethod
from typing import Any, Sequence


class MedicalRetriever(ABC):
    @abstractmethod
    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def get_sources(self) -> Sequence[dict[str, Any]]:
        raise NotImplementedError


class ApprovedSourceFilter:
    """Rejects evidence that is not on the admin-managed allow-list."""

    def __init__(self, allowed_source_ids: Sequence[str]):
        self.allowed_source_ids = set(allowed_source_ids)

    def filter(self, documents: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            document
            for document in documents
            if document.get("source_id") in self.allowed_source_ids
        ]


class MockMedicalRetriever(MedicalRetriever):
    def search(self, query: str, *, limit: int = 8) -> Sequence[dict[str, Any]]:
        return []

    def retrieve(self, source_ids: Sequence[str]) -> Sequence[dict[str, Any]]:
        return []

    def rank(self, query: str, documents: Sequence[dict[str, Any]]) -> Sequence[dict[str, Any]]:
        return list(documents)

    def get_sources(self) -> Sequence[dict[str, Any]]:
        return []
''',
    )
    write(
        BACKEND / "pytest.ini",
        '''[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
''',
    )
    write(
        BACKEND / "requirements.txt",
        '''Django>=5.1,<5.3
djangorestframework>=3.15,<3.17
djangorestframework-simplejwt>=5.3,<5.6
django-cors-headers>=4.6,<5
django-filter>=24.3,<26
drf-spectacular>=0.27,<0.29
psycopg[binary]>=3.2,<4
python-dotenv>=1.0,<2
''',
    )
    write(
        BACKEND / "requirements-dev.txt",
        '''-r requirements.txt
pytest>=8.3,<9
pytest-django>=4.9,<5
ruff>=0.8,<0.14
''',
    )
    write(
        BACKEND / "config" / "tests" / "__init__.py",
        "",
    )
    write(
        BACKEND / "config" / "tests" / "test_health.py",
        '''from django.urls import reverse
from rest_framework.test import APIClient


def test_health_endpoint_is_public():
    client = APIClient()
    response = client.get(reverse("health"))
    assert response.status_code == 200
    assert response.data["status"] == "ok"
    assert response.data["phase"] == 1
''',
    )

    # Frontend
    write(
        FRONTEND / "package.json",
        '''{
  "name": "clinical-cds-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run"
  },
  "dependencies": {
    "axios": "^1.7.9",
    "i18next": "^24.2.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-i18next": "^15.4.0",
    "react-router-dom": "^7.1.3"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.2.0",
    "@types/react": "^18.3.18",
    "@types/react-dom": "^18.3.5",
    "@vitejs/plugin-react": "^4.3.4",
    "jsdom": "^26.0.0",
    "typescript": "^5.7.3",
    "vite": "^6.0.11",
    "vitest": "^3.0.4"
  }
}
''',
    )
    write(
        FRONTEND / "tsconfig.json",
        '''{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src"]
}
''',
    )
    write(
        FRONTEND / "tsconfig.node.json",
        '''{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2023"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler"
  },
  "include": ["vite.config.ts"]
}
''',
    )
    write(
        FRONTEND / "vite.config.ts",
        '''import path from "node:path";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "src") },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
  },
});
''',
    )
    write(
        FRONTEND / "index.html",
        '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Clinical CDS</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
''',
    )
    write(FRONTEND / "src" / "vite-env.d.ts", '''/// <reference types="vite/client" />\n''')
    write(
        FRONTEND / "src" / "main.tsx",
        '''import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./i18n";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
''',
    )
    write(
        FRONTEND / "src" / "App.tsx",
        '''import { Navigate, Route, Routes } from "react-router-dom";
import { PublicLayout } from "./layouts/PublicLayout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
''',
    )
    write(
        FRONTEND / "src" / "App.test.tsx",
        '''import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";
import "./i18n";

test("renders landing disclaimer", () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>
  );
  expect(screen.getByRole("heading", { name: /clinical decision support/i })).toBeInTheDocument();
});
''',
    )
    write(
        FRONTEND / "src" / "styles.css",
        ''':root {
  color-scheme: light;
  --bg: #f4f7f8;
  --ink: #12323a;
  --muted: #4d646b;
  --card: #ffffff;
  --accent: #0f6c7a;
  --border: #d5e1e4;
  font-family: "Segoe UI", system-ui, sans-serif;
}

* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); }
a { color: var(--accent); }
.shell { max-width: 960px; margin: 0 auto; padding: 24px; }
.header, .footer { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
.muted { color: var(--muted); }
.banner { background: #fff6e8; border: 1px solid #ead7b0; padding: 12px 16px; border-radius: 8px; }
nav a { margin-left: 12px; }
''',
    )
    write(
        FRONTEND / "src" / "i18n" / "index.ts",
        '''import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./en.json";
import rw from "./rw.json";

void i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, rw: { translation: rw } },
  lng: "en",
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export default i18n;
''',
    )
    write(
        FRONTEND / "src" / "i18n" / "en.json",
        '''{
  "appName": "Clinical Decision Support",
  "tagline": "Health information and professional decision support. Not a replacement for a doctor or pharmacist.",
  "nav": { "home": "Home", "login": "Log in", "register": "Register" },
  "home": {
    "title": "Clinical Decision Support",
    "intro": "Describe symptoms in everyday language. The system organizes information, asks follow-up questions, and retrieves approved medical sources. Final diagnosis and prescribing stay with qualified professionals.",
    "disclaimer": "This application does not diagnose conditions or independently prescribe medication."
  },
  "auth": {
    "loginTitle": "Log in",
    "registerTitle": "Create a patient account",
    "comingSoon": "Authentication is implemented in Phase 3."
  }
}
''',
    )
    write(
        FRONTEND / "src" / "i18n" / "rw.json",
        '''{
  "appName": "Ubufasha mu Gufata Ibyemezo by'Ubuvuzi",
  "tagline": "Amakuru y'ubuzima n'ubufasha ku buzima. Ntabwo asimbura muganga cyangwa umuforomo w'imiti.",
  "nav": { "home": "Ahabanza", "login": "Injira", "register": "Iyandikishe" },
  "home": {
    "title": "Ubufasha mu Gufata Ibyemezo by'Ubuvuzi",
    "intro": "Sobanura ibimenyetso mu ndimi zisanzwe. Sisitemu itegura amakuru, ibaza ibibazo bikurikira, kandi ikurura amakuru ku nsoko zemewe. Diagnosis n'imiti biguma ku buzima bwa kinyamwuga.",
    "disclaimer": "Iyi porogaramu ntigira diagnosis kandi ntiyemeza imiti yonyine."
  },
  "auth": {
    "loginTitle": "Injira",
    "registerTitle": "Fungura konti y'umurwayi",
    "comingSoon": "Kwemeza umukoresha bikorwa mu gice cya 3."
  }
}
''',
    )
    write(
        FRONTEND / "src" / "layouts" / "PublicLayout.tsx",
        '''import { Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

export function PublicLayout() {
  const { t, i18n } = useTranslation();

  return (
    <div className="shell">
      <header className="header">
        <strong>{t("appName")}</strong>
        <nav>
          <Link to="/">{t("nav.home")}</Link>
          <Link to="/login">{t("nav.login")}</Link>
          <Link to="/register">{t("nav.register")}</Link>
          <button type="button" onClick={() => i18n.changeLanguage(i18n.language === "en" ? "rw" : "en")}>
            {i18n.language === "en" ? "Kinyarwanda" : "English"}
          </button>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="footer">
        <p className="muted">{t("tagline")}</p>
      </footer>
    </div>
  );
}
''',
    )
    write(
        FRONTEND / "src" / "pages" / "HomePage.tsx",
        '''import { useTranslation } from "react-i18next";

export function HomePage() {
  const { t } = useTranslation();
  return (
    <section className="card">
      <h1>{t("home.title")}</h1>
      <p>{t("home.intro")}</p>
      <p className="banner">{t("home.disclaimer")}</p>
    </section>
  );
}
''',
    )
    write(
        FRONTEND / "src" / "pages" / "auth" / "LoginPage.tsx",
        '''import { useTranslation } from "react-i18next";

export function LoginPage() {
  const { t } = useTranslation();
  return (
    <section className="card">
      <h1>{t("auth.loginTitle")}</h1>
      <p className="muted">{t("auth.comingSoon")}</p>
    </section>
  );
}
''',
    )
    write(
        FRONTEND / "src" / "pages" / "auth" / "RegisterPage.tsx",
        '''import { useTranslation } from "react-i18next";

export function RegisterPage() {
  const { t } = useTranslation();
  return (
    <section className="card">
      <h1>{t("auth.registerTitle")}</h1>
      <p className="muted">{t("auth.comingSoon")}</p>
    </section>
  );
}
''',
    )
    write(FRONTEND / "src" / "components" / ".gitkeep", "")
    write(FRONTEND / "src" / "hooks" / ".gitkeep", "")
    write(FRONTEND / "src" / "context" / ".gitkeep", "")
    write(FRONTEND / "src" / "types" / ".gitkeep", "")
    write(FRONTEND / "src" / "utils" / ".gitkeep", "")
    write(FRONTEND / "src" / "routes" / ".gitkeep", "")
    write(
        FRONTEND / "src" / "services" / "api.ts",
        '''import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
});
''',
    )
    write(
        FRONTEND / "src" / "test" / "setup.ts",
        '''import "@testing-library/jest-dom/vitest";
''',
    )
    write(FRONTEND / "src" / "pages" / "patient" / ".gitkeep", "")
    write(FRONTEND / "src" / "pages" / "doctor" / ".gitkeep", "")
    write(FRONTEND / "src" / "pages" / "pharmacist" / ".gitkeep", "")
    write(FRONTEND / "src" / "pages" / "admin" / ".gitkeep", "")

    print("Phase 1 scaffold written.")


if __name__ == "__main__":
    main()

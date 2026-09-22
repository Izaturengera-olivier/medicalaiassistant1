import { Link, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";

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

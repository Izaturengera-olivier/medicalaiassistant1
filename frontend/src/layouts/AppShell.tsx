import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { MobileDownloadButton } from "../components/common/MobileAppDownloadModal";

interface NavItem {
  to: string;
  labelKey: string;
  icon: JSX.Element;
  end?: boolean;
}

const icon = (path: string) => (
  <svg viewBox="0 0 24 24" width="17" height="17" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={path} />
  </svg>
);

const ICONS = {
  dashboard: icon("M3 3h7v9H3zM14 3h7v5h-7zM14 12h7v9h-7zM3 16h7v5H3z"),
  chat: icon("M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"),
  history: icon("M3 3v5h5M3.05 13A9 9 0 1 0 6 5.3L3 8M12 7v5l4 2"),
  profile: icon("M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"),
  patients: icon("M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"),
  prescriptions: icon("M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M9 15h6M9 11h2"),
  interactions: icon("M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01"),
  users: icon("M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"),
  meds: icon("M10.5 20.5 3.5 13.5a4.95 4.95 0 1 1 7-7l7 7a4.95 4.95 0 1 1-7 7zM8.5 8.5l7 7"),
  conditions: icon("M22 12h-4l-3 9L9 3l-3 9H2"),
  sources: icon("M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 19.5A2.5 2.5 0 0 0 6.5 22H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"),
  audit: icon("M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10zM9 12l2 2 4-4"),
  ai: icon("M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z"),
};

function navForRole(role: string): NavItem[] {
  switch (role) {
    case "DOCTOR":
      return [
        { to: "/app", labelKey: "nav.dashboard", icon: ICONS.dashboard, end: true },
        { to: "/app/patients", labelKey: "nav.patients", icon: ICONS.patients },
        { to: "/app/consultations", labelKey: "nav.consultations", icon: ICONS.chat },
        { to: "/app/ai-assistant", labelKey: "nav.aiAssistant", icon: ICONS.ai },
      ];
    case "PHARMACIST":
      return [
        { to: "/app", labelKey: "nav.dashboard", icon: ICONS.dashboard, end: true },
        { to: "/app/prescriptions", labelKey: "nav.prescriptions", icon: ICONS.prescriptions },
        { to: "/app/interactions", labelKey: "nav.interactions", icon: ICONS.interactions },
        { to: "/app/ai-assistant", labelKey: "nav.aiAssistant", icon: ICONS.ai },
      ];
    case "ADMIN":
      return [
        { to: "/app", labelKey: "nav.dashboard", icon: ICONS.dashboard, end: true },
        { to: "/app/users", labelKey: "nav.users", icon: ICONS.users },
        { to: "/app/system-consultations", labelKey: "Consultations", icon: ICONS.chat },
        { to: "/app/medications", labelKey: "nav.medications", icon: ICONS.meds },
        { to: "/app/conditions", labelKey: "nav.conditions", icon: ICONS.conditions },
        { to: "/app/sources", labelKey: "nav.sources", icon: ICONS.sources },
        { to: "/app/admin-settings", labelKey: "Settings", icon: ICONS.interactions },
        { to: "/app/audit", labelKey: "nav.audit", icon: ICONS.audit },
        { to: "/app/ai-assistant", labelKey: "nav.aiAssistant", icon: ICONS.ai },
      ];
    case "PATIENT":
    default:
      return [
        { to: "/app", labelKey: "nav.dashboard", icon: ICONS.dashboard, end: true },
        { to: "/app/assessment", labelKey: "nav.assessment", icon: ICONS.chat },
        { to: "/app/history", labelKey: "nav.history", icon: ICONS.history },
        { to: "/app/profile", labelKey: "nav.profile", icon: ICONS.profile },
      ];
  }
}

export function AppShell() {
  const { user, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const role = user?.role ?? "PATIENT";
  const currentLang = (i18n.language || "en").startsWith("rw") ? "rw" : "en";
  const nav = navForRole(role);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <NavLink to="/" className="app-sidebar-brand">
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10z" />
              <path d="M3 12h4l2-3 3 6 2-3h7" />
            </svg>
          </span>
          <span>{t("brand")}</span>
        </NavLink>

        <nav className="app-sidebar-nav" aria-label={t("nav.main")}>
          <div className="app-nav-section">{t("nav.workspace", { role: t(`status.role.${role}`) })}</div>
          {nav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? "app-nav-link is-active" : "app-nav-link")}
            >
              {item.icon}
              <span>{t(item.labelKey)}</span>
            </NavLink>
          ))}
        </nav>

        <div className="app-sidebar-foot">
          <div className="app-sidebar-user">
            <span className="app-sidebar-user-name">
              {user?.first_name} {user?.last_name}
            </span>
            <span className="app-sidebar-user-role">{t(`status.role.${role}`)}</span>
          </div>
          <button type="button" className="btn btn-outline btn-sm" onClick={handleLogout}>
            {t("nav.logout")}
          </button>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-topbar">
          <h1 className="app-topbar-title">{t("appName")}</h1>
          <div className="app-topbar-actions">
            <MobileDownloadButton />
            <div className="lang-switch" role="group" aria-label={t("nav.language")}>
              <button
                type="button"
                className={currentLang === "en" ? "lang-btn is-active" : "lang-btn"}
                onClick={() => void i18n.changeLanguage("en")}
                aria-pressed={currentLang === "en"}
              >
                EN
              </button>
              <button
                type="button"
                className={currentLang === "rw" ? "lang-btn is-active" : "lang-btn"}
                onClick={() => void i18n.changeLanguage("rw")}
                aria-pressed={currentLang === "rw"}
              >
                RW
              </button>
            </div>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { MobileDownloadButton } from "../components/common/MobileAppDownloadModal";

type LangCode = "en" | "rw";

export function HomePage() {
  const { t, i18n } = useTranslation();
  const currentLang = (i18n.language || "en").startsWith("rw") ? "rw" : "en";

  const switchLang = (next: LangCode) => {
    void i18n.changeLanguage(next);
  };

  const steps = [
    {
      key: "describe",
      title: t("home.steps.describe.title"),
      body: t("home.steps.describe.body"),
    },
    {
      key: "organize",
      title: t("home.steps.organize.title"),
      body: t("home.steps.organize.body"),
    },
    {
      key: "decide",
      title: t("home.steps.decide.title"),
      body: t("home.steps.decide.body"),
    },
  ];

  const roles = [
    {
      key: "patient",
      title: t("home.roles.patient.title"),
      body: t("home.roles.patient.body"),
      bullets: [
        t("home.roles.patient.bullet1"),
        t("home.roles.patient.bullet2"),
        t("home.roles.patient.bullet3"),
      ],
      to: "/register",
      cta: t("home.roles.patient.cta"),
    },
    {
      key: "doctor",
      title: t("home.roles.doctor.title"),
      body: t("home.roles.doctor.body"),
      bullets: [
        t("home.roles.doctor.bullet1"),
        t("home.roles.doctor.bullet2"),
        t("home.roles.doctor.bullet3"),
      ],
      to: "/login",
      cta: t("home.roles.doctor.cta"),
    },
    {
      key: "pharmacist",
      title: t("home.roles.pharmacist.title"),
      body: t("home.roles.pharmacist.body"),
      bullets: [
        t("home.roles.pharmacist.bullet1"),
        t("home.roles.pharmacist.bullet2"),
        t("home.roles.pharmacist.bullet3"),
      ],
      to: "/login",
      cta: t("home.roles.pharmacist.cta"),
    },
  ];

  return (
    <div className="home">
      <header className="home-header">
        <div className="home-container home-header-inner">
          <Link to="/" className="brand">
            <span className="brand-mark" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10z" />
                <path d="M3 12h4l2-3 3 6 2-3h7" />
              </svg>
            </span>
            <span className="brand-name">{t("appName")}</span>
          </Link>

          <div className="home-header-actions">
            <MobileDownloadButton />
            <div className="lang-switch" role="group" aria-label={t("nav.language")}>
              <button
                type="button"
                className={currentLang === "en" ? "lang-btn is-active" : "lang-btn"}
                onClick={() => switchLang("en")}
                aria-pressed={currentLang === "en"}
              >
                EN
              </button>
              <button
                type="button"
                className={currentLang === "rw" ? "lang-btn is-active" : "lang-btn"}
                onClick={() => switchLang("rw")}
                aria-pressed={currentLang === "rw"}
              >
                RW
              </button>
            </div>
            <Link to="/login" className="btn btn-ghost">{t("nav.login")}</Link>
            <Link to="/register" className="btn btn-primary">{t("nav.register")}</Link>
          </div>
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="home-container hero-inner">
            <p className="eyebrow">{t("home.eyebrow")}</p>
            <h1 className="hero-title">{t("home.title")}</h1>
            <p className="hero-sub">{t("home.intro")}</p>

            <div className="hero-ctas">
              <Link to="/chat" className="btn btn-primary btn-lg">
                {t("home.primaryCta")}
                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M5 12h14" />
                  <path d="m13 6 6 6-6 6" />
                </svg>
              </Link>
              <MobileDownloadButton style={{ padding: "12px 20px", fontSize: "1rem" }} />
              <Link to="/register" className="btn btn-outline btn-lg">
                {t("home.secondaryCta")}
              </Link>
            </div>

            <ul className="hero-trust">
              <li>{t("home.trust.sources")}</li>
              <li>{t("home.trust.professionals")}</li>
              <li>{t("home.trust.privacy")}</li>
            </ul>
          </div>
        </section>

        <section className="section">
          <div className="home-container">
            <h2 className="section-title">{t("home.howTitle")}</h2>
            <p className="section-sub">{t("home.howSub")}</p>
            <ol className="steps">
              {steps.map((s, i) => (
                <li key={s.key} className="step card">
                  <span className="step-num" aria-hidden="true">{i + 1}</span>
                  <h3 className="step-title">{s.title}</h3>
                  <p className="step-body">{s.body}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section className="section section-alt">
          <div className="home-container">
            <h2 className="section-title">{t("home.rolesTitle")}</h2>
            <p className="section-sub">{t("home.rolesSub")}</p>
            <div className="roles">
              {roles.map((r) => (
                <article key={r.key} className="role card">
                  <h3 className="role-title">{r.title}</h3>
                  <p className="role-body">{r.body}</p>
                  <ul className="role-bullets">
                    {r.bullets.map((b, i) => (
                      <li key={i}>{b}</li>
                    ))}
                  </ul>
                  <Link to={r.to} className="btn btn-outline btn-sm role-cta">
                    {r.cta}
                  </Link>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section">
          <div className="home-container">
            <div className="safety" role="note">
              <div className="safety-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                  <path d="M12 8v4" />
                  <path d="M12 16h.01" />
                </svg>
              </div>
              <div>
                <h2 className="safety-title">{t("home.safety.title")}</h2>
                <p className="safety-body">{t("home.disclaimer")}</p>
                <p className="safety-body">{t("home.safety.body")}</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <div className="home-container home-footer-inner">
          <p className="muted small">{t("home.disclaimer")}</p>
          <p className="muted small">© {new Date().getFullYear()} {t("appName")}</p>
        </div>
      </footer>
    </div>
  );
}

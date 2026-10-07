import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { errorMessage } from "../../hooks/useAsync";
import { Field } from "../../components/ui";
import { MobileDownloadButton } from "../../components/common/MobileAppDownloadModal";

export function LoginPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      navigate("/app");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card panel">
        <Link to="/" className="brand" style={{ justifyContent: "center", marginBottom: 8 }}>
          <span className="brand-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10z" />
              <path d="M3 12h4l2-3 3 6 2-3h7" />
            </svg>
          </span>
          <span className="brand-name">{t("appName")}</span>
        </Link>
        <h1 className="auth-title">{t("auth.loginTitle")}</h1>
        <p className="auth-sub">{t("auth.loginSub")}</p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="stack" style={{ gap: 14 }}>
            <Field label={t("auth.email")} htmlFor="email">
              <input
                id="email"
                type="email"
                required
                className="input"
                placeholder={t("auth.emailPlaceholder")}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </Field>
            <Field label={t("auth.password")} htmlFor="password">
              <input
                id="password"
                type="password"
                required
                className="input"
                placeholder={t("auth.passwordPlaceholder")}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </Field>
            <div className="row-between" style={{ marginTop: -4 }}>
              <span />
              <Link to="/forgot-password" className="small">
                {t("auth.forgotPassword")}
              </Link>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
              {loading ? t("auth.signingIn") : t("auth.signIn")}
            </button>
          </div>
        </form>

        <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid #e2e8f0", display: "flex", justifyContent: "center" }}>
          <MobileDownloadButton />
        </div>

        <p className="auth-foot">
          {t("auth.noAccount")} <Link to="/register">{t("auth.createOne")}</Link>
        </p>
      </div>
    </div>
  );
}


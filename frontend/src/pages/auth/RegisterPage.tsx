import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { errorMessage } from "../../hooks/useAsync";
import { Field } from "../../components/ui";
import { MobileDownloadButton } from "../../components/common/MobileAppDownloadModal";

export function RegisterPage() {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    email: "",
    first_name: "",
    last_name: "",
    role: "PATIENT",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(formData);
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
        <h1 className="auth-title">{t("auth.registerTitle")}</h1>
        <p className="auth-sub">{t("auth.registerSub")}</p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <Field label={t("auth.firstName")} htmlFor="first_name">
              <input id="first_name" name="first_name" type="text" required className="input" value={formData.first_name} onChange={handleChange} />
            </Field>
            <Field label={t("auth.lastName")} htmlFor="last_name">
              <input id="last_name" name="last_name" type="text" required className="input" value={formData.last_name} onChange={handleChange} />
            </Field>
            <Field label={t("auth.email")} htmlFor="email" span2>
              <input id="email" name="email" type="email" required className="input" placeholder={t("auth.emailPlaceholder")} value={formData.email} onChange={handleChange} />
            </Field>
            <Field label={t("auth.role")} htmlFor="role" span2>
              <select id="role" name="role" required className="select" value={formData.role} onChange={handleChange}>
                <option value="PATIENT">{t("status.role.PATIENT")}</option>
                <option value="DOCTOR">{t("status.role.DOCTOR")}</option>
                <option value="PHARMACIST">{t("status.role.PHARMACIST")}</option>
              </select>
            </Field>
            <Field label={t("auth.password")} htmlFor="password">
              <input id="password" name="password" type="password" required className="input" placeholder={t("auth.passwordPlaceholder")} value={formData.password} onChange={handleChange} />
            </Field>
            <Field label={t("auth.confirmPassword")} htmlFor="password_confirm">
              <input id="password_confirm" name="password_confirm" type="password" required className="input" placeholder={t("auth.passwordPlaceholder")} value={formData.password_confirm} onChange={handleChange} />
            </Field>
          </div>
          <div className="form-actions" style={{ marginTop: 16 }}>
            <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
              {loading ? t("auth.creatingAccount") : t("auth.createAccount")}
            </button>
          </div>
        </form>

        <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid #e2e8f0", display: "flex", justifyContent: "center" }}>
          <MobileDownloadButton />
        </div>

        <p className="auth-foot">
          {t("auth.haveAccount")} <Link to="/login">{t("auth.signIn")}</Link>
        </p>
      </div>
    </div>
  );
}


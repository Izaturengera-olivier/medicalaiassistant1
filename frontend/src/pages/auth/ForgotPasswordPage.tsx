import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { authAPI } from "../../services/api";
import { errorMessage } from "../../hooks/useAsync";
import { Field } from "../../components/ui";

type Step = "request" | "verify" | "done";

export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [step, setStep] = useState<Step>("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);

  const sendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authAPI.forgotPassword(email.trim());
      setNotice(t("auth.codeSent", { email: email.trim() }));
      setStep("verify");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const resendCode = async () => {
    setError("");
    setLoading(true);
    try {
      await authAPI.forgotPassword(email.trim());
      setNotice(t("auth.codeSent", { email: email.trim() }));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const submitReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authAPI.resetPassword({
        email: email.trim(),
        code: code.trim(),
        password,
        password_confirm: passwordConfirm,
      });
      setStep("done");
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
        <h1 className="auth-title">{t("auth.forgotTitle")}</h1>

        {step === "request" && (
          <>
            <p className="auth-sub">{t("auth.forgotSub")}</p>
            {error && <div className="error-box">{error}</div>}
            <form onSubmit={sendCode}>
              <div className="stack" style={{ gap: 14 }}>
                <Field label={t("auth.email")} htmlFor="forgot-email">
                  <input
                    id="forgot-email"
                    type="email"
                    required
                    className="input"
                    placeholder={t("auth.emailPlaceholder")}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </Field>
                <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
                  {loading ? t("auth.sendingCode") : t("auth.sendCode")}
                </button>
              </div>
            </form>
          </>
        )}

        {step === "verify" && (
          <>
            <p className="auth-sub">{notice}</p>
            {error && <div className="error-box">{error}</div>}
            <form onSubmit={submitReset}>
              <div className="stack" style={{ gap: 14 }}>
                <Field label={t("auth.verificationCode")} htmlFor="reset-code">
                  <input
                    id="reset-code"
                    required
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    pattern="[0-9]{6}"
                    maxLength={6}
                    className="input code-input"
                    placeholder={t("auth.codePlaceholder")}
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  />
                </Field>
                <Field label={t("auth.newPassword")} htmlFor="reset-password">
                  <input
                    id="reset-password"
                    type="password"
                    required
                    className="input"
                    placeholder={t("auth.passwordPlaceholder")}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </Field>
                <Field label={t("auth.confirmNewPassword")} htmlFor="reset-password-confirm">
                  <input
                    id="reset-password-confirm"
                    type="password"
                    required
                    className="input"
                    placeholder={t("auth.passwordPlaceholder")}
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                  />
                </Field>
                <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading || code.length !== 6}>
                  {loading ? t("auth.resetting") : t("auth.resetPassword")}
                </button>
                <div className="row-between" style={{ justifyContent: "center", gap: 18 }}>
                  <button type="button" className="btn btn-ghost btn-sm" onClick={() => void resendCode()} disabled={loading}>
                    {t("auth.resendCode")}
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => {
                      setStep("request");
                      setCode("");
                      setError("");
                    }}
                    disabled={loading}
                  >
                    {t("auth.changeEmail")}
                  </button>
                </div>
              </div>
            </form>
          </>
        )}

        {step === "done" && (
          <>
            <div className="success-box">{t("auth.resetSuccess")}</div>
            <button
              type="button"
              className="btn btn-primary"
              style={{ width: "100%" }}
              onClick={() => navigate("/login")}
            >
              {t("auth.backToLogin")}
            </button>
          </>
        )}

        <p className="auth-foot">
          <Link to="/login">{t("auth.backToLogin")}</Link>
        </p>
      </div>
    </div>
  );
}

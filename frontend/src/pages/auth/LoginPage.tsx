import { useTranslation } from "react-i18next";

export function LoginPage() {
  const { t } = useTranslation();
  return (
    <section className="card">
      <h1>{t("auth.loginTitle")}</h1>
      <p className="muted">{t("auth.comingSoon")}</p>
    </section>
  );
}

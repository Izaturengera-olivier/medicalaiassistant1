import { useTranslation } from "react-i18next";

export function RegisterPage() {
  const { t } = useTranslation();
  return (
    <section className="card">
      <h1>{t("auth.registerTitle")}</h1>
      <p className="muted">{t("auth.comingSoon")}</p>
    </section>
  );
}

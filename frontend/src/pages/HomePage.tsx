import { useTranslation } from "react-i18next";

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

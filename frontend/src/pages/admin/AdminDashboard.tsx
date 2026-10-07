import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { usersAPI, medicationsAPI, medicalAPI, knowledgeAPI, consultationsAPI } from "../../services/api";
import { ErrorState, Loading, PageHeader, Panel, StatCard, countOf } from "../../components/ui";

interface Counts {
  users: number;
  medications: number;
  conditions: number;
  sources: number;
  consultations: number;
}

export function AdminDashboard() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<Counts>(async () => {
    const [users, meds, conditions, sources, consultations] = await Promise.all([
      usersAPI.list(),
      medicationsAPI.list(),
      medicalAPI.conditions(),
      knowledgeAPI.sources(),
      consultationsAPI.list().catch(() => ({ data: [] })),
    ]);
    return {
      users: countOf(users.data),
      medications: countOf(meds.data),
      conditions: countOf(conditions.data),
      sources: sources.data?.sources?.length ?? 0,
      consultations: countOf(consultations.data),
    };
  });

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return null;

  return (
    <>
      <PageHeader title={t("admin.dashboard.title")} subtitle="Master administrative control & system status center" />

      <div className="stat-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))" }}>
        <StatCard label={t("admin.dashboard.users")} value={data.users} />
        <StatCard label="Consultations" value={data.consultations} tone="accent" />
        <StatCard label={t("admin.dashboard.medications")} value={data.medications} />
        <StatCard label={t("admin.dashboard.conditions")} value={data.conditions} />
        <StatCard label={t("admin.dashboard.approvedSources")} value={data.sources} tone="accent" />
      </div>

      <div style={{ height: 20 }} />

      <div className="grid-2">
        <Panel title={t("admin.dashboard.manageContent")}>
          <div className="stack">
            <Link to="/app/medications" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              💊 {t("admin.dashboard.medicationCatalog")}
            </Link>
            <Link to="/app/conditions" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              🩺 {t("admin.dashboard.conditionCatalog")}
            </Link>
            <Link to="/app/sources" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              📚 {t("admin.dashboard.knowledgeSources")}
            </Link>
          </div>
        </Panel>

        <Panel title="System Operations & Control">
          <div className="stack">
            <Link to="/app/users" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              👥 {t("admin.dashboard.usersRoles")} & Accounts
            </Link>
            <Link to="/app/system-consultations" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              🏥 Clinical Consultations Oversight
            </Link>
            <Link to="/app/admin-settings" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              ⚙️ AI & System Settings
            </Link>
            <Link to="/app/audit" className="btn btn-outline" style={{ justifyContent: "flex-start" }}>
              📋 {t("admin.dashboard.auditLogs")}
            </Link>
          </div>
        </Panel>
      </div>
    </>
  );
}

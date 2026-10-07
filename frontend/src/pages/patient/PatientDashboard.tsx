import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { consultationsAPI } from "../../services/api";
import {
  Badge,
  EmptyState,
  ErrorState,
  Loading,
  PageHeader,
  Panel,
  StatCard,
  consultationStatusLabel,
  consultationStatusTone,
  formatDateTime,
  unwrapList,
} from "../../components/ui";

interface Consultation {
  id: number;
  status: string;
  chief_complaint: string;
  created_at: string;
  completed_at?: string | null;
}

export function PatientDashboard() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<Consultation[]>(
    () => consultationsAPI.list().then((r) => unwrapList<Consultation>(r.data))
  );

  const consultations = data ?? [];
  const inProgress = consultations.filter((c) => c.status === "IN_PROGRESS").length;
  const completed = consultations.filter((c) => c.status === "COMPLETED").length;

  return (
    <>
      <PageHeader
        title={t("patient.dashboard.title")}
        subtitle={t("patient.dashboard.subtitle")}
        actions={
          <Link to="/app/assessment" className="btn btn-primary">
            {t("patient.dashboard.startAssessment")}
          </Link>
        }
      />

      <div className="stat-grid">
        <StatCard label={t("patient.dashboard.totalConsultations")} value={consultations.length} />
        <StatCard label={t("patient.dashboard.inProgress")} value={inProgress} tone="accent" />
        <StatCard label={t("patient.dashboard.completed")} value={completed} />
      </div>

      <Panel title={t("patient.dashboard.recentTitle")} subtitle={t("patient.dashboard.recentSub")} bodyless>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : consultations.length === 0 ? (
          <EmptyState
            title={t("patient.dashboard.emptyTitle")}
            message={t("patient.dashboard.emptyMessage")}
          />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.id")}</th>
                  <th>{t("patient.dashboard.chiefComplaint")}</th>
                  <th>{t("common.status")}</th>
                  <th>{t("common.started")}</th>
                </tr>
              </thead>
              <tbody>
                {consultations.slice(0, 8).map((c) => (
                  <tr key={c.id}>
                    <td className="cell-strong">{c.id}</td>
                    <td>{c.chief_complaint}</td>
                    <td>
                      <Badge tone={consultationStatusTone(c.status)}>{consultationStatusLabel(c.status)}</Badge>
                    </td>
                    <td>{formatDateTime(c.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
    </>
  );
}

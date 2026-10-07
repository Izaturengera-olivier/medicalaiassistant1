import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { pharmacistsAPI } from "../../services/api";
import {
  Badge,
  EmptyState,
  ErrorState,
  Loading,
  PageHeader,
  Panel,
  StatCard,
  formatDateTime,
  prescriptionStatusLabel,
  prescriptionStatusTone,
} from "../../components/ui";

interface Prescription {
  id: number;
  patient_name: string;
  medication_name: string;
  dosage: string;
  status: string;
  prescribed_at: string;
}

interface Dashboard {
  stats: {
    total_prescriptions: number;
    pending_reviews: number;
    approved_today: number;
    flagged_prescriptions: number;
  };
  recent_prescriptions: Prescription[];
}

export function PharmacistDashboard() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<Dashboard>(
    () => pharmacistsAPI.dashboard().then((r) => r.data as Dashboard)
  );

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return null;

  const s = data.stats;

  return (
    <>
      <PageHeader
        title={t("pharmacist.dashboard.title")}
        subtitle={t("pharmacist.dashboard.subtitle")}
        actions={
          <Link to="/app/prescriptions" className="btn btn-outline">
            {t("pharmacist.dashboard.allPrescriptions")}
          </Link>
        }
      />

      <div className="stat-grid">
        <StatCard label={t("pharmacist.dashboard.totalPrescriptions")} value={s.total_prescriptions} />
        <StatCard label={t("pharmacist.dashboard.pendingReview")} value={s.pending_reviews} tone="accent" />
        <StatCard label={t("pharmacist.dashboard.prescribedToday")} value={s.approved_today} />
        <StatCard label={t("pharmacist.dashboard.flagged")} value={s.flagged_prescriptions} tone="danger" />
      </div>

      <Panel title={t("pharmacist.dashboard.recentTitle")} bodyless>
        {data.recent_prescriptions.length === 0 ? (
          <EmptyState title={t("pharmacist.dashboard.emptyTitle")} message={t("pharmacist.dashboard.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.id")}</th>
                  <th>{t("common.patient")}</th>
                  <th>{t("pharmacist.dashboard.medication")}</th>
                  <th>{t("pharmacist.dashboard.dosage")}</th>
                  <th>{t("common.status")}</th>
                  <th>{t("pharmacist.dashboard.prescribed")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.recent_prescriptions.map((p) => (
                  <tr key={p.id}>
                    <td className="cell-strong">{p.id}</td>
                    <td>{p.patient_name}</td>
                    <td>{p.medication_name}</td>
                    <td>{p.dosage}</td>
                    <td>
                      <Badge tone={prescriptionStatusTone(p.status)}>{prescriptionStatusLabel(p.status)}</Badge>
                    </td>
                    <td>{formatDateTime(p.prescribed_at)}</td>
                    <td>
                      <Link to={`/app/prescriptions/${p.id}`} className="btn btn-outline btn-sm">
                        {t("common.review")}
                      </Link>
                    </td>
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

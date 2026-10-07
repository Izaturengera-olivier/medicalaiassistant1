import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { doctorsAPI } from "../../services/api";
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
  urgencyLabel,
  urgencyTone,
} from "../../components/ui";

interface AiAssessment {
  urgency_level?: string;
  warning_signs?: string[];
  possible_conditions?: { name?: string }[];
}

interface Consultation {
  id: number;
  patient_name: string;
  chief_complaint: string;
  status: string;
  created_at: string;
  ai_assessment?: AiAssessment | null;
}

interface Dashboard {
  stats: {
    total_patients: number;
    active_consultations: number;
    completed_consultations: number;
    pending_reviews: number;
    urgent_cases: number;
  };
  recent_consultations: Consultation[];
}

export function DoctorDashboard() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<Dashboard>(
    () => doctorsAPI.dashboard().then((r) => r.data as Dashboard)
  );

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return null;

  const s = data.stats;

  return (
    <>
      <PageHeader
        title={t("doctor.dashboard.title")}
        subtitle={t("doctor.dashboard.subtitle")}
        actions={
          <Link to="/app/consultations" className="btn btn-outline">
            {t("doctor.dashboard.allConsultations")}
          </Link>
        }
      />

      <div className="stat-grid">
        <StatCard label={t("doctor.dashboard.patientsSeen")} value={s.total_patients} />
        <StatCard label={t("doctor.dashboard.activeConsultations")} value={s.active_consultations} tone="accent" />
        <StatCard label={t("doctor.dashboard.pendingReviews")} value={s.pending_reviews} />
        <StatCard label={t("doctor.dashboard.completed")} value={s.completed_consultations} />
        <StatCard label={t("doctor.dashboard.urgentCases")} value={s.urgent_cases} tone="danger" />
      </div>

      <Panel title={t("doctor.dashboard.recentTitle")} bodyless>
        {data.recent_consultations.length === 0 ? (
          <EmptyState title={t("doctor.dashboard.emptyTitle")} message={t("doctor.dashboard.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.id")}</th>
                  <th>{t("common.patient")}</th>
                  <th>{t("common.chiefComplaint")}</th>
                  <th>{t("doctor.dashboard.aiUrgency")}</th>
                  <th>{t("common.status")}</th>
                  <th>{t("common.started")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.recent_consultations.map((c) => (
                  <tr key={c.id}>
                    <td className="cell-strong">{c.id}</td>
                    <td>{c.patient_name}</td>
                    <td>{c.chief_complaint}</td>
                    <td>
                      {c.ai_assessment?.urgency_level ? (
                        <Badge tone={urgencyTone(c.ai_assessment.urgency_level)}>
                          {urgencyLabel(c.ai_assessment.urgency_level)}
                        </Badge>
                      ) : (
                        <Badge>{t("common.none")}</Badge>
                      )}
                    </td>
                    <td>
                      <Badge tone={consultationStatusTone(c.status)}>{consultationStatusLabel(c.status)}</Badge>
                    </td>
                    <td>{formatDateTime(c.created_at)}</td>
                    <td>
                      <Link to={`/app/consultations/${c.id}`} className="btn btn-outline btn-sm">
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

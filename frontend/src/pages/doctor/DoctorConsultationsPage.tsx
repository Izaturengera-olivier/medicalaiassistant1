import { useState } from "react";
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
  consultationStatusLabel,
  consultationStatusTone,
  formatDateTime,
  urgencyLabel,
  urgencyTone,
} from "../../components/ui";

interface Consultation {
  id: number;
  patient_name: string;
  chief_complaint: string;
  status: string;
  created_at: string;
  ai_assessment?: { urgency_level?: string } | null;
}

interface ConsultationsResponse {
  consultations: Consultation[];
  total: number;
}

const FILTERS = ["", "IN_PROGRESS", "COMPLETED", "CANCELLED"];

export function DoctorConsultationsPage() {
  const { t } = useTranslation();
  const [filter, setFilter] = useState("");
  const { data, loading, error, reload } = useAsync<ConsultationsResponse>(
    () => doctorsAPI.consultations(filter || undefined).then((r) => r.data as ConsultationsResponse),
    [filter]
  );

  return (
    <>
      <PageHeader title={t("doctor.consultations.title")} subtitle={t("doctor.consultations.subtitle")} />

      <div className="tabs" role="tablist">
        {FILTERS.map((f) => (
          <button
            key={f}
            type="button"
            role="tab"
            aria-selected={filter === f}
            className={filter === f ? "tab is-active" : "tab"}
            onClick={() => setFilter(f)}
          >
            {f ? consultationStatusLabel(f) : t("common.all")}
          </button>
        ))}
      </div>

      <Panel bodyless>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !data || data.consultations.length === 0 ? (
          <EmptyState title={t("doctor.consultations.emptyTitle")} message={t("doctor.consultations.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.id")}</th>
                  <th>{t("common.patient")}</th>
                  <th>{t("common.chiefComplaint")}</th>
                  <th>{t("doctor.consultations.aiUrgency")}</th>
                  <th>{t("common.status")}</th>
                  <th>{t("common.started")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.consultations.map((c) => (
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
                        {t("common.open")}
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

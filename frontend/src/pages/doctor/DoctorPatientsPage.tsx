import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { doctorsAPI } from "../../services/api";
import { EmptyState, ErrorState, Loading, PageHeader, Panel, formatDate } from "../../components/ui";

interface PatientRow {
  id: number;
  name: string;
  email: string;
  last_consultation?: string | null;
  consultation_count: number;
}

interface PatientsResponse {
  patients: PatientRow[];
  total: number;
}

export function DoctorPatientsPage() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<PatientsResponse>(
    () => doctorsAPI.patients().then((r) => r.data as PatientsResponse)
  );

  return (
    <>
      <PageHeader title={t("doctor.patients.title")} subtitle={t("doctor.patients.subtitle")} />

      <Panel bodyless>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !data || data.patients.length === 0 ? (
          <EmptyState title={t("doctor.patients.emptyTitle")} message={t("doctor.patients.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.name")}</th>
                  <th>{t("common.email")}</th>
                  <th>{t("doctor.patients.consultations")}</th>
                  <th>{t("doctor.patients.lastConsultation")}</th>
                </tr>
              </thead>
              <tbody>
                {data.patients.map((p) => (
                  <tr key={p.id}>
                    <td className="cell-strong">{p.name}</td>
                    <td>{p.email}</td>
                    <td>{p.consultation_count}</td>
                    <td>{formatDate(p.last_consultation)}</td>
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

import { useState } from "react";
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
  prescriptionStatusLabel,
  prescriptionStatusTone,
} from "../../components/ui";

interface Prescription {
  id: number;
  patient_name: string;
  doctor_name: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  status: string;
  prescribed_at: string;
  interactions?: unknown[];
}

interface PrescriptionsResponse {
  prescriptions: Prescription[];
  total: number;
}

const FILTERS = ["", "ACTIVE", "COMPLETED", "DISCONTINUED"];

export function PrescriptionsPage() {
  const { t } = useTranslation();
  const [filter, setFilter] = useState("");
  const { data, loading, error, reload } = useAsync<PrescriptionsResponse>(
    () => pharmacistsAPI.prescriptions(filter || undefined).then((r) => r.data as PrescriptionsResponse),
    [filter]
  );

  return (
    <>
      <PageHeader title={t("pharmacist.prescriptions.title")} subtitle={t("pharmacist.prescriptions.subtitle")} />

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
            {f ? prescriptionStatusLabel(f) : t("common.all")}
          </button>
        ))}
      </div>

      <Panel bodyless>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !data || data.prescriptions.length === 0 ? (
          <EmptyState title={t("pharmacist.prescriptions.emptyTitle")} message={t("pharmacist.prescriptions.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("common.id")}</th>
                  <th>{t("common.patient")}</th>
                  <th>{t("pharmacist.prescriptions.medication")}</th>
                  <th>{t("pharmacist.prescriptions.dosage")}</th>
                  <th>{t("pharmacist.prescriptions.frequency")}</th>
                  <th>{t("pharmacist.prescriptions.prescriber")}</th>
                  <th>{t("pharmacist.prescriptions.interactions")}</th>
                  <th>{t("common.status")}</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {data.prescriptions.map((p) => (
                  <tr key={p.id}>
                    <td className="cell-strong">{p.id}</td>
                    <td>{p.patient_name}</td>
                    <td>{p.medication_name}</td>
                    <td>{p.dosage}</td>
                    <td>{p.frequency}</td>
                    <td>{p.doctor_name}</td>
                    <td>
                      {p.interactions && p.interactions.length > 0 ? (
                        <Badge tone="warn">{t("common.notedCount", { count: p.interactions.length })}</Badge>
                      ) : (
                        <Badge>{t("common.none")}</Badge>
                      )}
                    </td>
                    <td>
                      <Badge tone={prescriptionStatusTone(p.status)}>{prescriptionStatusLabel(p.status)}</Badge>
                    </td>
                    <td>
                      <Link to={`/app/prescriptions/${p.id}`} className="btn btn-outline btn-sm">
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

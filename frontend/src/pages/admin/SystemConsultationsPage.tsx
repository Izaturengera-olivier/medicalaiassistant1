import { useState } from "react";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { consultationsAPI, usersAPI } from "../../services/api";
import { EmptyState, ErrorState, Field, Loading, PageHeader, Panel, formatDate, unwrapList } from "../../components/ui";

interface Consultation {
  id: number;
  patient: { id: number; email: string; first_name: string; last_name: string };
  assigned_doctor?: { id: number; email: string; first_name: string; last_name: string } | null;
  chief_complaint: string;
  status: string;
  created_at: string;
}

interface DoctorUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
}

const STATUSES = ["PENDING", "IN_PROGRESS", "COMPLETED", "CANCELLED"];

export function SystemConsultationsPage() {
  const [statusFilter, setStatusFilter] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);

  const { data: consultations, loading, error, reload } = useAsync<Consultation[]>(
    () => consultationsAPI.list(statusFilter ? { status: statusFilter } : undefined).then((r) => unwrapList<Consultation>(r.data)),
    [statusFilter]
  );

  const { data: doctors } = useAsync<DoctorUser[]>(
    () => usersAPI.list({ role: "DOCTOR" }).then((r) => unwrapList<DoctorUser>(r.data))
  );

  const handleAssignDoctor = async (consultationId: number, doctorId: number) => {
    setActionError(null);
    try {
      await consultationsAPI.assignDoctor(consultationId, doctorId);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  const handleStatusOverride = async (consultationId: number, status: string) => {
    setActionError(null);
    try {
      await consultationsAPI.overrideStatus(consultationId, status);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  return (
    <>
      <PageHeader title="Clinical Consultations Oversight" subtitle="Master system view and administrative control of all patient consultations" />

      {actionError && <div className="error-box" style={{ marginBottom: 16 }}>{actionError}</div>}

      <Panel title="Filter Consultations" bodyless>
        <div className="panel-body form-grid">
          <Field label="Status Filter">
            <select className="select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </Field>
        </div>
      </Panel>

      <div style={{ height: 20 }} />

      <Panel bodyless>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !consultations || consultations.length === 0 ? (
          <EmptyState title="No Consultations Found" message="There are currently no patient consultations matching the query." />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Patient</th>
                  <th>Chief Complaint</th>
                  <th>Assigned Doctor</th>
                  <th>Status Override</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {consultations.map((c) => (
                  <tr key={c.id}>
                    <td>#{c.id}</td>
                    <td className="cell-strong">
                      {c.patient ? `${c.patient.first_name} ${c.patient.last_name}` : "Unknown"}
                    </td>
                    <td style={{ maxWidth: 300 }}>{c.chief_complaint}</td>
                    <td>
                      <select
                        className="select"
                        style={{ minWidth: 160, padding: "4px 8px", fontSize: "0.85rem" }}
                        value={c.assigned_doctor?.id || ""}
                        onChange={(e) => void handleAssignDoctor(c.id, Number(e.target.value))}
                      >
                        <option value="">Unassigned</option>
                        {(doctors ?? []).map((doc) => (
                          <option key={doc.id} value={doc.id}>
                            Dr. {doc.first_name} {doc.last_name}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <select
                        className="select"
                        style={{ minWidth: 130, padding: "4px 8px", fontSize: "0.85rem" }}
                        value={c.status}
                        onChange={(e) => void handleStatusOverride(c.id, e.target.value)}
                      >
                        {STATUSES.map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </td>
                    <td>{formatDate(c.created_at)}</td>
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

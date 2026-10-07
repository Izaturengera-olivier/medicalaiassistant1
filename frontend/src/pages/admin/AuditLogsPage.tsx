import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { auditAPI } from "../../services/api";
import { Badge, EmptyState, ErrorState, Field, Loading, PageHeader, Panel, actionLabel, formatDateTime } from "../../components/ui";

interface AuditRow {
  id: number;
  user_email?: string | null;
  action: string;
  entity_type?: string;
  entity_id?: string;
  ip_address?: string | null;
  timestamp: string;
}

interface AuditResponse {
  results?: AuditRow[];
  count?: number;
}

const ACTIONS = ["create", "read", "update", "delete", "login", "logout", "ai_assessment", "medical_record_access", "prescription_access", "other"];

export function AuditLogsPage() {
  const { t } = useTranslation();
  const [action, setAction] = useState("");

  const { data, loading, error, reload } = useAsync<AuditRow[] | AuditResponse>(
    () => auditAPI.logs(action ? { action } : undefined).then((r) => r.data),
    [action]
  );

  const rows: AuditRow[] = Array.isArray(data) ? data : (data?.results ?? []);

  return (
    <>
      <PageHeader title={t("admin.audit.title")} subtitle={t("admin.audit.subtitle")} />

      <Panel title={t("admin.audit.filter")} bodyless>
        <div className="panel-body form-grid">
          <Field label={t("admin.audit.action")} htmlFor="actionfilter">
            <select id="actionfilter" className="select" value={action} onChange={(e) => setAction(e.target.value)}>
              <option value="">{t("admin.audit.allActions")}</option>
              {ACTIONS.map((a) => (
                <option key={a} value={a}>{actionLabel(a)}</option>
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
        ) : rows.length === 0 ? (
          <EmptyState title={t("admin.audit.emptyTitle")} message={t("admin.audit.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("admin.audit.when")}</th>
                  <th>{t("admin.audit.user")}</th>
                  <th>{t("admin.audit.action")}</th>
                  <th>{t("admin.audit.entity")}</th>
                  <th>{t("admin.audit.ip")}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id}>
                    <td>{formatDateTime(r.timestamp)}</td>
                    <td className="cell-strong">{r.user_email ?? t("common.anonymous")}</td>
                    <td>
                      <Badge tone={r.action === "delete" ? "danger" : r.action === "login" ? "info" : "neutral"}>
                        {actionLabel(r.action)}
                      </Badge>
                    </td>
                    <td>
                      {r.entity_type ? `${r.entity_type}${r.entity_id ? ` #${r.entity_id}` : ""}` : "—"}
                    </td>
                    <td>{r.ip_address ?? "—"}</td>
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

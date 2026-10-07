import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { knowledgeAPI } from "../../services/api";
import { Badge, ErrorState, Field, Loading, PageHeader, Panel, approvalLabel, formatDate } from "../../components/ui";

interface Source {
  id: number;
  name: string;
  url: string;
  source_type: string;
  approval_status: string;
  last_verified_date?: string | null;
  notes?: string;
}

interface SourcesResponse {
  sources: Source[];
  total: number;
}

const SOURCE_TYPES = ["WHO", "MOH", "FDA", "HOSPITAL", "LITERATURE", "GUIDELINE"];

export function SourcesPage() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<SourcesResponse>(
    () => knowledgeAPI.sources().then((r) => r.data as SourcesResponse)
  );

  const [form, setForm] = useState({
    name: "",
    url: "",
    source_type: "WHO",
    approval_status: "pending",
    notes: "",
  });
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      await knowledgeAPI.addSource(form);
      setSaved(true);
      setForm({ name: "", url: "", source_type: "WHO", approval_status: "pending", notes: "" });
      reload();
    } catch (err) {
      setSaveError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (source: Source, newStatus: string) => {
    try {
      await knowledgeAPI.updateSource(source.id, { approval_status: newStatus });
      reload();
    } catch (err) {
      setSaveError(errorMessage(err));
    }
  };

  const handleDeleteSource = async (source: Source) => {
    if (!window.confirm(`Delete knowledge source ${source.name}?`)) return;
    try {
      await knowledgeAPI.deleteSource(source.id);
      reload();
    } catch (err) {
      setSaveError(errorMessage(err));
    }
  };

  const handleSyncIndex = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const res = await knowledgeAPI.syncIndex();
      setSyncMessage(res.data.message || "Vector index synchronized.");
    } catch (err) {
      setSaveError(errorMessage(err));
    } finally {
      setSyncing(false);
    }
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <PageHeader title={t("admin.sources.title")} subtitle={t("admin.sources.subtitle")} />
        <button
          type="button"
          className="btn btn-outline"
          disabled={syncing}
          onClick={() => void handleSyncIndex()}
        >
          {syncing ? "Syncing RAG Index..." : "⚡ Sync Knowledge Base"}
        </button>
      </div>

      {syncMessage && <div className="success-box" style={{ marginBottom: 16 }}>{syncMessage}</div>}
      {saveError && <div className="error-box" style={{ marginBottom: 16 }}>{saveError}</div>}

      <div className="stack">
        <Panel title={t("admin.sources.listTitle")} bodyless>
          {loading ? (
            <Loading />
          ) : error ? (
            <ErrorState message={error} onRetry={reload} />
          ) : !data || data.sources.length === 0 ? (
            <div className="state-box">{t("admin.sources.empty")}</div>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>{t("admin.sources.name")}</th>
                    <th>{t("admin.sources.type")}</th>
                    <th>{t("admin.sources.approval")}</th>
                    <th>{t("admin.sources.url")}</th>
                    <th>{t("admin.sources.lastVerified")}</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.sources.map((s) => (
                    <tr key={s.id}>
                      <td className="cell-strong">{s.name}</td>
                      <td>
                        <Badge>{s.source_type}</Badge>
                      </td>
                      <td>
                        <select
                          className="select"
                          style={{ minWidth: 110, padding: "4px 8px", fontSize: "0.85rem" }}
                          value={s.approval_status}
                          onChange={(e) => void handleStatusChange(s, e.target.value)}
                        >
                          <option value="pending">Pending</option>
                          <option value="approved">Approved</option>
                          <option value="rejected">Rejected</option>
                          <option value="deprecated">Deprecated</option>
                        </select>
                      </td>
                      <td>
                        <a href={s.url} target="_blank" rel="noopener noreferrer">
                          {s.url}
                        </a>
                      </td>
                      <td>{formatDate(s.last_verified_date)}</td>
                      <td>
                        <button
                          type="button"
                          className="btn btn-sm btn-outline"
                          style={{ color: "#d9534f", borderColor: "#d9534f" }}
                          onClick={() => void handleDeleteSource(s)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>

        <Panel title={t("admin.sources.addTitle")} subtitle={t("admin.sources.addSub")}>
          {saved && <div className="success-box">{t("admin.sources.submitted")}</div>}
          <form onSubmit={submit}>
            <div className="form-grid">
              <Field label={t("admin.sources.nameLabel")} htmlFor="srcname">
                <input id="srcname" className="input" value={form.name} required onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
              </Field>
              <Field label={t("admin.sources.urlLabel")} htmlFor="srcurl">
                <input id="srcurl" type="url" className="input" value={form.url} required onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))} />
              </Field>
              <Field label={t("admin.sources.sourceType")} htmlFor="srctype">
                <select id="srctype" className="select" value={form.source_type} onChange={(e) => setForm((f) => ({ ...f, source_type: e.target.value }))}>
                  {SOURCE_TYPES.map((st) => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </Field>
              <Field label={t("admin.sources.approvalStatus")} htmlFor="srcstatus">
                <select id="srcstatus" className="select" value={form.approval_status} onChange={(e) => setForm((f) => ({ ...f, approval_status: e.target.value }))}>
                  <option value="pending">{approvalLabel("pending")}</option>
                  <option value="approved">{approvalLabel("approved")}</option>
                  <option value="rejected">{approvalLabel("rejected")}</option>
                </select>
              </Field>
              <Field label={t("admin.sources.notes")} htmlFor="srcnotes" span2>
                <textarea id="srcnotes" className="textarea" value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} />
              </Field>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? t("admin.sources.adding") : t("admin.sources.addSource")}
              </button>
            </div>
          </form>
        </Panel>
      </div>
    </>
  );
}

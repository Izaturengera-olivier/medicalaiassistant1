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
  document_count?: number;
  last_verified_date?: string | null;
  notes?: string;
}

interface SourcesResponse {
  sources: Source[];
  total: number;
}

interface KnowledgeDoc {
  id: number;
  document_key: string;
  source: number;
  source_name: string;
  title: string;
  content: string;
  url?: string;
  is_active: boolean;
}

interface DocumentsResponse {
  documents: KnowledgeDoc[];
  total: number;
}

const SOURCE_TYPES = ["WHO", "MOH", "FDA", "HOSPITAL", "LITERATURE", "GUIDELINE"];

export function SourcesPage() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<SourcesResponse>(
    () => knowledgeAPI.sources().then((r) => r.data as SourcesResponse)
  );
  const {
    data: docsData,
    loading: docsLoading,
    reload: reloadDocs,
  } = useAsync<DocumentsResponse>(() => knowledgeAPI.documents().then((r) => r.data as DocumentsResponse));

  const [form, setForm] = useState({
    name: "",
    url: "",
    source_type: "WHO",
    approval_status: "pending",
    notes: "",
  });
  const [docForm, setDocForm] = useState({ source: "", title: "", content: "", url: "" });
  const [savingDoc, setSavingDoc] = useState(false);
  const [docError, setDocError] = useState<string | null>(null);
  const [docSaved, setDocSaved] = useState(false);
  const [expandedDoc, setExpandedDoc] = useState<number | null>(null);
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
      setSyncMessage(res.data.message || "Retrieval is live.");
      reload();
      reloadDocs();
    } catch (err) {
      setSaveError(errorMessage(err));
    } finally {
      setSyncing(false);
    }
  };

  const approvedSources = (data?.sources || []).filter((s) => s.approval_status === "approved");

  const submitDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingDoc(true);
    setDocError(null);
    setDocSaved(false);
    try {
      await knowledgeAPI.addDocument({
        source: Number(docForm.source),
        title: docForm.title,
        content: docForm.content,
        url: docForm.url,
        is_active: true,
      });
      setDocSaved(true);
      setDocForm({ source: docForm.source, title: "", content: "", url: "" });
      reloadDocs();
      reload();
    } catch (err) {
      setDocError(errorMessage(err));
    } finally {
      setSavingDoc(false);
    }
  };

  const toggleDocument = async (doc: KnowledgeDoc) => {
    try {
      await knowledgeAPI.updateDocument(doc.id, { is_active: !doc.is_active });
      reloadDocs();
    } catch (err) {
      setDocError(errorMessage(err));
    }
  };

  const handleDeleteDocument = async (doc: KnowledgeDoc) => {
    if (!window.confirm(`Delete knowledge document "${doc.title}"?`)) return;
    try {
      await knowledgeAPI.deleteDocument(doc.id);
      reloadDocs();
    } catch (err) {
      setDocError(errorMessage(err));
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
                    <th>{t("admin.documents.countHeader")}</th>
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
                        <span title={t("admin.documents.countHint")}>{s.document_count ?? 0}</span>
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

        <Panel
          title={t("admin.documents.listTitle")}
          subtitle={t("admin.documents.listSub")}
          bodyless
        >
          {docsLoading ? (
            <Loading />
          ) : docError ? (
            <div className="error-box">{docError}</div>
          ) : !docsData || docsData.documents.length === 0 ? (
            <div className="state-box">{t("admin.documents.empty")}</div>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>{t("admin.documents.title")}</th>
                    <th>{t("admin.documents.source")}</th>
                    <th>{t("admin.documents.available")}</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {docsData.documents.map((doc) => (
                    <tr key={doc.id}>
                      <td className="cell-strong">
                        <button
                          type="button"
                          className="btn btn-sm btn-ghost"
                          onClick={() => setExpandedDoc((open) => (open === doc.id ? null : doc.id))}
                        >
                          {expandedDoc === doc.id ? "▾" : "▸"} {doc.title}
                        </button>
                        {expandedDoc === doc.id && (
                          <p style={{ margin: "8px 0 0", whiteSpace: "pre-wrap", fontWeight: 400 }}>
                            {doc.content}
                            {doc.url && (
                              <>
                                {" — "}
                                <a href={doc.url} target="_blank" rel="noopener noreferrer">
                                  {doc.url}
                                </a>
                              </>
                            )}
                          </p>
                        )}
                      </td>
                      <td>{doc.source_name}</td>
                      <td>
                        <Badge tone={doc.is_active ? "success" : "neutral"}>
                          {doc.is_active ? t("admin.documents.searchable") : t("admin.documents.retired")}
                        </Badge>
                      </td>
                      <td>
                        <div style={{ display: "flex", gap: 8 }}>
                          <button type="button" className="btn btn-sm btn-outline" onClick={() => void toggleDocument(doc)}>
                            {doc.is_active ? t("admin.documents.retire") : t("admin.documents.reinstate")}
                          </button>
                          <button
                            type="button"
                            className="btn btn-sm btn-outline"
                            style={{ color: "#d9534f", borderColor: "#d9534f" }}
                            onClick={() => void handleDeleteDocument(doc)}
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>

        <Panel title={t("admin.documents.addTitle")} subtitle={t("admin.documents.addSub")}>
          {docSaved && <div className="success-box">{t("admin.documents.added")}</div>}
          {approvedSources.length === 0 ? (
            <div className="state-box">{t("admin.documents.needApprovedSource")}</div>
          ) : (
            <form onSubmit={submitDocument}>
              <div className="form-grid">
                <Field label={t("admin.documents.sourceLabel")} htmlFor="docsource">
                  <select
                    id="docsource"
                    className="select"
                    value={docForm.source}
                    required
                    onChange={(e) => setDocForm((f) => ({ ...f, source: e.target.value }))}
                  >
                    <option value="">{t("admin.documents.chooseSource")}</option>
                    {approvedSources.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name}
                      </option>
                    ))}
                  </select>
                </Field>
                <Field label={t("admin.documents.titleLabel")} htmlFor="doctitle">
                  <input
                    id="doctitle"
                    className="input"
                    value={docForm.title}
                    required
                    onChange={(e) => setDocForm((f) => ({ ...f, title: e.target.value }))}
                  />
                </Field>
                <Field label={t("admin.documents.urlLabel")} htmlFor="docurl" span2>
                  <input
                    id="docurl"
                    type="url"
                    className="input"
                    value={docForm.url}
                    required
                    onChange={(e) => setDocForm((f) => ({ ...f, url: e.target.value }))}
                  />
                </Field>
                <Field label={t("admin.documents.contentLabel")} htmlFor="doccontent" span2>
                  <textarea
                    id="doccontent"
                    className="textarea"
                    rows={5}
                    value={docForm.content}
                    required
                    onChange={(e) => setDocForm((f) => ({ ...f, content: e.target.value }))}
                  />
                </Field>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={savingDoc}>
                  {savingDoc ? t("admin.documents.adding") : t("admin.documents.add")}
                </button>
              </div>
            </form>
          )}
        </Panel>
      </div>
    </>
  );
}

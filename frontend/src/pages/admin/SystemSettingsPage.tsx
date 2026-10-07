import { useState, useEffect } from "react";
import { adminSettingsAPI } from "../../services/api";
import { ErrorState, Field, Loading, PageHeader, Panel } from "../../components/ui";

interface SystemSettings {
  ai_provider: string;
  ai_triage_mode: string;
  web_search_enabled: boolean;
  maintenance_mode: boolean;
  system_notice: string;
  allow_registration: boolean;
  last_updated?: string;
}

export function SystemSettingsPage() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await adminSettingsAPI.get();
      setSettings(res.data);
    } catch (err: any) {
      setError(err.message || "Failed to load system settings.");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settings) return;
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const res = await adminSettingsAPI.update(settings);
      setSettings(res.data.settings);
      setSuccess("System configuration updated successfully!");
    } catch (err: any) {
      setError(err.message || "Failed to update settings.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loading />;
  if (error && !settings) return <ErrorState message={error} onRetry={loadSettings} />;

  return (
    <>
      <PageHeader title="System & AI Control Settings" subtitle="Configure AI models, clinical safety triage guardrails, and system mode" />

      {success && <div className="success-box" style={{ marginBottom: 16 }}>{success}</div>}
      {error && <div className="error-box" style={{ marginBottom: 16 }}>{error}</div>}

      {settings && (
        <form onSubmit={handleSave} className="stack">
          <Panel title="AI & Intelligence Configuration">
            <div className="form-grid">
              <Field label="Primary AI Engine / Provider">
                <select
                  className="select"
                  value={settings.ai_provider}
                  onChange={(e) => setSettings({ ...settings, ai_provider: e.target.value })}
                >
                  <option value="mock">Mock Clinical Service (Local Rules Engine)</option>
                  <option value="openai">OpenAI GPT-4o Clinical Model</option>
                  <option value="gemini">Google Gemini 1.5 Pro Medical</option>
                </select>
              </Field>

              <Field label="Clinical Triage Safety Mode">
                <select
                  className="select"
                  value={settings.ai_triage_mode}
                  onChange={(e) => setSettings({ ...settings, ai_triage_mode: e.target.value })}
                >
                  <option value="STRICT">STRICT — Maximize red flag alerts & urgent referral</option>
                  <option value="BALANCED">BALANCED — Standard clinical decision guidelines</option>
                  <option value="RELAXED">RELAXED — Educational & informational emphasis</option>
                </select>
              </Field>

              <Field label="Web Search RAG Integration (Tavily Medical)">
                <label style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={settings.web_search_enabled}
                    onChange={(e) => setSettings({ ...settings, web_search_enabled: e.target.checked })}
                  />
                  <span>Enable live external retrieval from approved domains (CDC, WHO, NIH)</span>
                </label>
              </Field>
            </div>
          </Panel>

          <Panel title="System Governance & Operations">
            <div className="form-grid">
              <Field label="System Maintenance Mode">
                <label style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={settings.maintenance_mode}
                    onChange={(e) => setSettings({ ...settings, maintenance_mode: e.target.checked })}
                  />
                  <span style={{ color: settings.maintenance_mode ? "#d9534f" : "inherit", fontWeight: settings.maintenance_mode ? "bold" : "normal" }}>
                    Enable Maintenance Mode (Restricts non-admin user logins)
                  </span>
                </label>
              </Field>

              <Field label="Patient Self-Registration">
                <label style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8, cursor: "pointer" }}>
                  <input
                    type="checkbox"
                    checked={settings.allow_registration}
                    onChange={(e) => setSettings({ ...settings, allow_registration: e.target.checked })}
                  />
                  <span>Allow public patient account registration</span>
                </label>
              </Field>

              <Field label="System Broadcast Notice" span2>
                <textarea
                  className="input"
                  rows={2}
                  value={settings.system_notice}
                  onChange={(e) => setSettings({ ...settings, system_notice: e.target.value })}
                  placeholder="System wide banner notification shown to all users..."
                />
              </Field>
            </div>

            <div style={{ marginTop: 20, display: "flex", justifyContent: "flex-end" }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Saving Settings..." : "Save System Settings"}
              </button>
            </div>
          </Panel>
        </form>
      )}
    </>
  );
}

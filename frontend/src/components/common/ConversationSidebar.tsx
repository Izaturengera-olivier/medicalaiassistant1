import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { aiAPI } from "../../services/api";

export interface ConversationSummary {
  id: number;
  title: string;
  kind: "patient" | "professional";
  created_at: string;
  updated_at: string;
}

interface Props {
  kind: "patient" | "professional";
  activeId: number | null;
  refreshSignal: number;
  onOpen: (id: number) => void;
  onNew: () => void;
  footer?: ReactNode;
}

export function ConversationSidebar({ kind, activeId, refreshSignal, onOpen, onNew, footer }: Props) {
  const { t } = useTranslation();
  const [items, setItems] = useState<ConversationSummary[]>([]);

  useEffect(() => {
    let cancelled = false;
    aiAPI
      .conversations(kind)
      .then((res) => {
        if (!cancelled) setItems((res.data ?? []) as ConversationSummary[]);
      })
      .catch(() => {
        /* sidebar stays empty on failure */
      });
    return () => {
      cancelled = true;
    };
  }, [kind, refreshSignal]);

  const remove = async (id: number) => {
    if (!window.confirm(t("chat.deleteConfirm"))) return;
    try {
      await aiAPI.deleteConversation(id);
      setItems((prev) => prev.filter((c) => c.id !== id));
      if (id === activeId) onNew();
    } catch {
      /* keep list as-is */
    }
  };

  return (
    <aside className="convo-sidebar">
      <button type="button" className="convo-new" onClick={onNew}>
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <path d="M12 5v14M5 12h14" />
        </svg>
        {t("chat.newChat")}
      </button>

      <div className="convo-section-label">{t("chat.conversations")}</div>
      <div className="convo-list">
        {items.length === 0 && <p className="convo-empty">{t("chat.noConversations")}</p>}
        {items.map((c) => (
          <div key={c.id} className={c.id === activeId ? "convo-item is-active" : "convo-item"}>
            <button type="button" className="convo-open" onClick={() => onOpen(c.id)} title={c.title}>
              <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <span className="convo-title">{c.title}</span>
            </button>
            <button
              type="button"
              className="convo-delete"
              aria-label={t("chat.deleteConversation")}
              title={t("chat.deleteConversation")}
              onClick={() => void remove(c.id)}
            >
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
              </svg>
            </button>
          </div>
        ))}
      </div>

      {footer && <div className="convo-foot">{footer}</div>}
    </aside>
  );
}

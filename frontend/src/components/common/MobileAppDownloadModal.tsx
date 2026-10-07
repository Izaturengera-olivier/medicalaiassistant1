import { useState } from "react";

export function MobileAppDownloadModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.6)",
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 16,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: "#ffffff",
          borderRadius: 16,
          padding: 28,
          maxWidth: 500,
          width: "100%",
          boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.35rem", color: "#0f766e", fontWeight: "bold", display: "flex", alignItems: "center", gap: 8 }}>
              📱 Mobile AI Assistant
            </h3>
            <p style={{ margin: "4px 0 0", color: "#64748b", fontSize: "0.9rem" }}>
              Install on Android & iOS devices
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              fontSize: "1.5rem",
              cursor: "pointer",
              color: "#94a3b8",
            }}
          >
            &times;
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div
            style={{
              background: "#f0fdf4",
              border: "1px solid #bbf7d0",
              borderRadius: 12,
              padding: 16,
              display: "flex",
              alignItems: "center",
              gap: 16,
            }}
          >
            <div style={{ fontSize: "2.5rem" }}>📲</div>
            <div>
              <h4 style={{ margin: 0, color: "#166534", fontSize: "1rem" }}>Cross-Platform Mobile App (Expo / React Native)</h4>
              <p style={{ margin: "4px 0 0", color: "#15803d", fontSize: "0.85rem", lineHeight: "1.3" }}>
                Full patient symptom assessment, triage urgency badging, history logs, and doctor decision assistant.
              </p>
            </div>
          </div>

          <div style={{ background: "#f8fafc", padding: 16, borderRadius: 12, border: "1px solid #e2e8f0" }}>
            <h5 style={{ margin: "0 0 8px", fontSize: "0.9rem", color: "#334155" }}>⚡ How to run on your phone:</h5>
            <ol style={{ margin: 0, paddingLeft: 20, color: "#475569", fontSize: "0.85rem", lineHeight: "1.6" }}>
              <li>Open terminal in the project directory.</li>
              <li>Navigate to <code style={{ background: "#e2e8f0", padding: "2px 6px", borderRadius: 4 }}>cd mobile</code></li>
              <li>Run <code style={{ background: "#e2e8f0", padding: "2px 6px", borderRadius: 4 }}>npx expo start</code></li>
              <li>Scan the displayed QR code with Expo Go app (Android/iOS).</li>
            </ol>
          </div>

          <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
            <button
              type="button"
              className="btn btn-primary"
              style={{ flex: 1, justifyContent: "center" }}
              onClick={() => {
                alert("Mobile application directory: /mobile. To build standalone Android APK: Run 'eas build -p android --profile preview' inside /mobile.");
              }}
            >
              📥 Download / Build Mobile App
            </button>
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function MobileDownloadButton({ className, style }: { className?: string; style?: React.CSSProperties }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        type="button"
        className={className || "btn btn-outline btn-sm"}
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 6,
          borderColor: "#0d9488",
          color: "#0d9488",
          fontWeight: 600,
          ...style,
        }}
        onClick={() => setOpen(true)}
      >
        <span>📱</span>
        <span>Get Mobile App</span>
      </button>
      <MobileAppDownloadModal isOpen={open} onClose={() => setOpen(false)} />
    </>
  );
}

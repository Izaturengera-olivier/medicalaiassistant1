import React, { useState, useEffect } from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
} from "react-native";
import { adminAPI } from "../../services/api";

export const AdminOverviewScreen = () => {
  const [stats, setStats] = useState({
    users: 0,
    sources: 0,
    provider: "unknown",
    triageMode: "unknown",
    notice: "",
  });
  const [busy, setBusy] = useState(true);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setBusy(true);
    try {
      const [usersRes, sourcesRes, settingsRes] = await Promise.all([
        adminAPI.users().catch(() => null),
        adminAPI.sources().catch(() => null),
        adminAPI.settings().catch(() => null),
      ]);

      // The user list is paginated (PAGE_SIZE 20), so `results.length` would
      // silently cap the headline number; `count` is the real total.
      const users = usersRes?.data;
      const userTotal = Array.isArray(users) ? users.length : users?.count ?? 0;

      setStats({
        users: userTotal,
        sources: sourcesRes?.data?.total ?? sourcesRes?.data?.sources?.length ?? 0,
        provider: settingsRes?.data?.ai_provider || "unknown",
        triageMode: settingsRes?.data?.ai_triage_mode || "unknown",
        notice: settingsRes?.data?.system_notice || "",
      });
    } catch (err) {
      console.log("Admin metrics error:", err);
    } finally {
      setBusy(false);
      setLoaded(true);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>⚙️ Admin Control Center</Text>
        <Text style={styles.headerSub}>Mobile System Overview & Governance</Text>
      </View>

      {!loaded ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color="#0d9488" />
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={styles.content}
          refreshControl={
            <RefreshControl refreshing={busy} onRefresh={loadDashboard} tintColor="#0d9488" />
          }
        >
          {!!stats.notice && (
            <View style={styles.noticeBox}>
              <Text style={styles.noticeText}>{stats.notice}</Text>
            </View>
          )}

          <View style={styles.grid}>
            <View style={styles.card}>
              <Text style={styles.cardLabel}>Registered Users</Text>
              <Text style={styles.cardValue}>{stats.users}</Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardLabel}>Knowledge Sources</Text>
              <Text style={styles.cardValue}>{stats.sources}</Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardLabel}>Active AI Engine</Text>
              <Text style={styles.cardValueSmall}>{stats.provider.toUpperCase()}</Text>
            </View>

            <View style={styles.card}>
              <Text style={styles.cardLabel}>Triage Guardrails</Text>
              <Text style={styles.cardValueSmall}>{stats.triageMode}</Text>
            </View>
          </View>

          <TouchableOpacity style={styles.refreshButton} onPress={loadDashboard}>
            <Text style={styles.refreshText}>🔄 Refresh System Status</Text>
          </TouchableOpacity>
        </ScrollView>
      )}
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  header: { padding: 16, backgroundColor: "#ffffff", borderBottomWidth: 1, borderBottomColor: "#e2e8f0" },
  headerTitle: { fontSize: 20, fontWeight: "bold", color: "#0f766e" },
  headerSub: { fontSize: 13, color: "#64748b" },
  loadingBox: { flex: 1, justifyContent: "center", alignItems: "center" },
  content: { padding: 16 },
  noticeBox: { backgroundColor: "#ecfeff", borderWidth: 1, borderColor: "#a5f3fc", padding: 12, borderRadius: 10, marginBottom: 16 },
  noticeText: { fontSize: 13, color: "#155e75" },
  grid: { flexDirection: "row", flexWrap: "wrap", gap: 12, marginBottom: 20 },
  card: { flex: 1, minWidth: "45%", backgroundColor: "#ffffff", padding: 16, borderRadius: 12, borderWidth: 1, borderColor: "#cbd5e1" },
  cardLabel: { fontSize: 13, color: "#64748b", marginBottom: 6 },
  cardValue: { fontSize: 28, fontWeight: "bold", color: "#0d9488" },
  cardValueSmall: { fontSize: 18, fontWeight: "bold", color: "#1e293b" },
  refreshButton: { backgroundColor: "#0d9488", padding: 14, borderRadius: 10, alignItems: "center" },
  refreshText: { color: "#ffffff", fontSize: 15, fontWeight: "600" },
});

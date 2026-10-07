import React, { useCallback, useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  FlatList,
  RefreshControl,
  ActivityIndicator,
  SafeAreaView,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { consultationsAPI, Consultation } from "../../services/api";

export const HistoryScreen = () => {
  const [items, setItems] = useState<Consultation[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadHistory = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);
    try {
      const res = await consultationsAPI.list();
      setItems(res.data.results ?? []);
      setTotal(res.data.count ?? res.data.results?.length ?? 0);
    } catch (err: any) {
      setError(
        err?.response
          ? `Could not load history (${err.response.status}).`
          : "Cannot reach the server. Pull down to retry."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Assessments created in the Assessment tab only appear after a refetch.
  useFocusEffect(
    useCallback(() => {
      loadHistory();
    }, [loadHistory])
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return "#16a34a";
      case "IN_PROGRESS":
        return "#0284c7";
      case "PENDING":
      default:
        return "#ea580c";
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>📋 Consultation History</Text>
        <Text style={styles.headerSub}>
          {total > 0 ? `${total} record${total === 1 ? "" : "s"}` : "Past Symptom Assessments & Records"}
        </Text>
      </View>

      {loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator size="large" color="#0d9488" />
        </View>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id.toString()}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={() => loadHistory(true)}
              tintColor="#0d9488"
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyBox}>
              {error ? (
                <Text style={styles.emptyTitle}>{error}</Text>
              ) : (
                <>
                  <Text style={styles.emptyTitle}>No Past Consultations</Text>
                  <Text style={styles.emptySub}>
                    Perform a symptom assessment to log your first consultation.
                  </Text>
                </>
              )}
            </View>
          }
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardId}>Consultation #{item.id}</Text>
                <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                  <Text style={styles.statusText}>{item.status}</Text>
                </View>
              </View>
              <Text style={styles.complaint}>{item.chief_complaint}</Text>
              <Text style={styles.date}>{new Date(item.created_at).toLocaleString()}</Text>
            </View>
          )}
        />
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
  listContent: { padding: 16, flexGrow: 1 },
  emptyBox: { flex: 1, justifyContent: "center", alignItems: "center", padding: 32 },
  emptyTitle: { fontSize: 18, fontWeight: "600", color: "#334155", marginBottom: 6, textAlign: "center" },
  emptySub: { fontSize: 14, color: "#64748b", textAlign: "center" },
  card: { backgroundColor: "#ffffff", padding: 16, borderRadius: 12, marginBottom: 12, borderWidth: 1, borderColor: "#e2e8f0" },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 8 },
  cardId: { fontSize: 14, fontWeight: "bold", color: "#0f766e" },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 2, borderRadius: 10 },
  statusText: { color: "#ffffff", fontSize: 11, fontWeight: "bold" },
  complaint: { fontSize: 15, color: "#1e293b", marginBottom: 8 },
  date: { fontSize: 12, color: "#94a3b8" },
});

import React from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  SafeAreaView,
} from "react-native";
import { useAuth } from "../../context/AuthContext";

export const ProfileScreen = () => {
  const { user, logout } = useAuth();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>👤 Profile & Account</Text>
        <Text style={styles.headerSub}>Manage user information and settings</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.card}>
          <Text style={styles.name}>{user?.first_name} {user?.last_name}</Text>
          <Text style={styles.email}>{user?.email}</Text>

          <View style={styles.roleTag}>
            <Text style={styles.roleText}>{user?.role || "PATIENT"}</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  header: { padding: 16, backgroundColor: "#ffffff", borderBottomWidth: 1, borderBottomColor: "#e2e8f0" },
  headerTitle: { fontSize: 20, fontWeight: "bold", color: "#0f766e" },
  headerSub: { fontSize: 13, color: "#64748b" },
  content: { padding: 16 },
  card: { backgroundColor: "#ffffff", padding: 20, borderRadius: 12, borderWidth: 1, borderColor: "#cbd5e1", alignItems: "center", marginBottom: 24 },
  name: { fontSize: 20, fontWeight: "bold", color: "#1e293b", marginBottom: 4 },
  email: { fontSize: 14, color: "#64748b", marginBottom: 12 },
  roleTag: { backgroundColor: "#ccfbf1", paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  roleText: { color: "#0f766e", fontSize: 12, fontWeight: "bold" },
  logoutButton: { backgroundColor: "#ef4444", padding: 14, borderRadius: 10, alignItems: "center" },
  logoutText: { color: "#ffffff", fontSize: 15, fontWeight: "600" },
});

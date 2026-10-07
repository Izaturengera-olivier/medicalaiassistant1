import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { useAuth } from "../../context/AuthContext";

// Django's MinimumLengthValidator rejects anything shorter, and the API returns
// one error list per field, so every field has to be surfaced, not just email.
const describeError = (err: any): string => {
  const data = err?.response?.data;
  if (data && typeof data === "object") {
    const messages = Object.entries(data).flatMap(([field, value]) => {
      const parts = Array.isArray(value) ? value : [value];
      const label = field.replace(/_/g, " ");
      return parts.map((part) => {
        const text = typeof part === "string" ? part : JSON.stringify(part);
        return field === "non_field_errors"
          ? text
          : `${label.charAt(0).toUpperCase()}${label.slice(1)}: ${text}`;
      });
    });
    if (messages.length) return messages.join("\n");
  }
  if (!err?.response) {
    return "Cannot reach the server. Check your connection and try again.";
  }
  return "Registration failed.";
};

export const RegisterScreen = ({ navigation }: any) => {
  const { register } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("PATIENT");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async () => {
    if (!firstName.trim() || !lastName.trim() || !email.trim() || !password) {
      setError("Please fill in all fields.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      setError("Enter a valid email address.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await register({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password,
        password_confirm: password,
        role,
      });
      Alert.alert("Account created", "You can now sign in.", [
        { text: "OK", onPress: () => navigation.navigate("Login") },
      ]);
    } catch (err: any) {
      setError(describeError(err));
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
      <ScrollView contentContainerStyle={styles.inner} keyboardShouldPersistTaps="handled">
        <Text style={styles.brand}>🏥 Create Account</Text>
        <Text style={styles.subtitle}>Join Clinical Decision Support</Text>

        <View style={styles.form}>
          {error && (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          )}

          <Text style={styles.label}>First Name</Text>
          <TextInput style={styles.input} value={firstName} onChangeText={setFirstName} />

          <Text style={styles.label}>Last Name</Text>
          <TextInput style={styles.input} value={lastName} onChangeText={setLastName} />

          <Text style={styles.label}>Email Address</Text>
          <TextInput style={styles.input} value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />

          <Text style={styles.label}>Password</Text>
          <TextInput style={styles.input} value={password} onChangeText={setPassword} secureTextEntry />
          <Text style={styles.hint}>At least 8 characters.</Text>

          <Text style={styles.label}>Account Role</Text>
          <View style={styles.roleRow}>
            {["PATIENT", "DOCTOR", "PHARMACIST"].map((r) => (
              <TouchableOpacity
                key={r}
                style={[styles.roleChip, role === r && styles.roleChipActive]}
                onPress={() => setRole(r)}
              >
                <Text style={[styles.roleText, role === r && styles.roleTextActive]}>{r}</Text>
              </TouchableOpacity>
            ))}
          </View>

          <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={loading}>
            {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Register</Text>}
          </TouchableOpacity>

          <TouchableOpacity style={styles.linkButton} onPress={() => navigation.navigate("Login")}>
            <Text style={styles.linkText}>Already have an account? Sign In</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f7fafc" },
  inner: { padding: 24 },
  brand: { fontSize: 24, fontWeight: "bold", color: "#0f766e", textAlign: "center" },
  subtitle: { fontSize: 14, color: "#64748b", textAlign: "center", marginBottom: 20 },
  form: { backgroundColor: "#ffffff", padding: 20, borderRadius: 12, elevation: 2 },
  errorBox: { backgroundColor: "#fef2f2", padding: 10, borderRadius: 6, marginBottom: 12 },
  errorText: { color: "#991b1b", fontSize: 13 },
  label: { fontSize: 14, fontWeight: "500", color: "#475569", marginBottom: 4 },
  input: { backgroundColor: "#f8fafc", borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 8, padding: 10, marginBottom: 12 },
  hint: { fontSize: 12, color: "#64748b", marginTop: -8, marginBottom: 12 },
  roleRow: { flexDirection: "row", gap: 8, marginBottom: 16 },
  roleChip: { flex: 1, padding: 10, borderRadius: 6, borderWidth: 1, borderColor: "#cbd5e1", alignItems: "center" },
  roleChipActive: { backgroundColor: "#0d9488", borderColor: "#0d9488" },
  roleText: { fontSize: 12, fontWeight: "600", color: "#475569" },
  roleTextActive: { color: "#ffffff" },
  button: { backgroundColor: "#0d9488", padding: 14, borderRadius: 8, alignItems: "center", marginTop: 8 },
  buttonText: { color: "#ffffff", fontSize: 16, fontWeight: "600" },
  linkButton: { marginTop: 16, alignItems: "center" },
  linkText: { color: "#0d9488", fontSize: 14, fontWeight: "500" },
});

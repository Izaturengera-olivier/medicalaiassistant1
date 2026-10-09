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
import { authAPI } from "../../services/api";

// The backend returns {"message": ...} for throttling/send failures but one
// error list per field for validation failures, so both shapes need handling.
const describeError = (err: any): string => {
  const data = err?.response?.data;
  if (data && typeof data === "object") {
    if (typeof data.message === "string") return data.message;
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
  return "Something went wrong. Please try again.";
};

type Step = "request" | "verify";

export const ForgotPasswordScreen = ({ navigation }: any) => {
  const [step, setStep] = useState<Step>("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const sendCode = async () => {
    const address = email.trim();
    if (!address) {
      setError("Please enter your email address.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(address)) {
      setError("Enter a valid email address.");
      return;
    }
    setLoading(true);
    setError(null);
    setNotice(null);
    try {
      await authAPI.forgotPassword(address);
      setNotice(
        `If an account exists for ${address}, a 6-digit code is on its way. It expires in 15 minutes.`
      );
      setStep("verify");
    } catch (err: any) {
      setError(describeError(err));
    } finally {
      setLoading(false);
    }
  };

  const submitReset = async () => {
    if (code.trim().length !== 6) {
      setError("Enter the 6-digit code from your email.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== passwordConfirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await authAPI.resetPassword({
        email: email.trim(),
        code: code.trim(),
        password,
        password_confirm: passwordConfirm,
      });
      Alert.alert("Password reset", "You can now sign in with your new password.", [
        { text: "OK", onPress: () => navigation.navigate("Login") },
      ]);
    } catch (err: any) {
      setError(describeError(err));
    } finally {
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
          <Text style={styles.brand}>🔑 Reset Password</Text>
          <Text style={styles.subtitle}>
            {step === "request"
              ? "We'll email you a verification code"
              : "Enter the code we emailed you"}
          </Text>

          <View style={styles.form}>
            {error && (
              <View style={styles.errorBox}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            )}
            {notice && !error && (
              <View style={styles.noticeBox}>
                <Text style={styles.noticeText}>{notice}</Text>
              </View>
            )}

            {step === "request" ? (
              <>
                <Text style={styles.label}>Email Address</Text>
                <TextInput
                  style={styles.input}
                  placeholder="you@example.com"
                  value={email}
                  onChangeText={setEmail}
                  autoCapitalize="none"
                  keyboardType="email-address"
                />

                <TouchableOpacity style={styles.button} onPress={sendCode} disabled={loading}>
                  {loading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.buttonText}>Send Code</Text>
                  )}
                </TouchableOpacity>
              </>
            ) : (
              <>
                <Text style={styles.label}>Verification Code</Text>
                <TextInput
                  style={[styles.input, styles.codeInput]}
                  placeholder="000000"
                  value={code}
                  onChangeText={(text) => setCode(text.replace(/\D/g, "").slice(0, 6))}
                  keyboardType="number-pad"
                  maxLength={6}
                />

                <Text style={styles.label}>New Password</Text>
                <TextInput
                  style={styles.input}
                  placeholder="••••••••"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                />
                <Text style={styles.hint}>At least 8 characters.</Text>

                <Text style={styles.label}>Confirm New Password</Text>
                <TextInput
                  style={styles.input}
                  placeholder="••••••••"
                  value={passwordConfirm}
                  onChangeText={setPasswordConfirm}
                  secureTextEntry
                />

                <TouchableOpacity
                  style={styles.button}
                  onPress={submitReset}
                  disabled={loading || code.length !== 6}
                >
                  {loading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <Text style={styles.buttonText}>Reset Password</Text>
                  )}
                </TouchableOpacity>

                <View style={styles.linkRow}>
                  <TouchableOpacity style={styles.linkButton} onPress={sendCode} disabled={loading}>
                    <Text style={styles.linkText}>Resend Code</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    style={styles.linkButton}
                    onPress={() => {
                      setStep("request");
                      setCode("");
                      setError(null);
                      setNotice(null);
                    }}
                    disabled={loading}
                  >
                    <Text style={styles.linkText}>Change Email</Text>
                  </TouchableOpacity>
                </View>
              </>
            )}

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => navigation.navigate("Login")}
            >
              <Text style={styles.linkText}>Back to Sign In</Text>
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
  noticeBox: { backgroundColor: "#ecfeff", padding: 10, borderRadius: 6, marginBottom: 12 },
  noticeText: { color: "#155e75", fontSize: 13 },
  label: { fontSize: 14, fontWeight: "500", color: "#475569", marginBottom: 4 },
  input: { backgroundColor: "#f8fafc", borderWidth: 1, borderColor: "#cbd5e1", borderRadius: 8, padding: 10, marginBottom: 12 },
  codeInput: { fontSize: 22, letterSpacing: 8, textAlign: "center", fontWeight: "600", color: "#0f172a" },
  hint: { fontSize: 12, color: "#64748b", marginTop: -8, marginBottom: 12 },
  button: { backgroundColor: "#0d9488", padding: 14, borderRadius: 8, alignItems: "center", marginTop: 8 },
  buttonText: { color: "#ffffff", fontSize: 16, fontWeight: "600" },
  linkRow: { flexDirection: "row", justifyContent: "space-between", marginTop: 8 },
  linkButton: { marginTop: 16, alignItems: "center" },
  linkText: { color: "#0d9488", fontSize: 14, fontWeight: "500" },
});

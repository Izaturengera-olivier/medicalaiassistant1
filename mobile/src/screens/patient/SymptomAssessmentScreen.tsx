import React, { useRef, useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
} from "react-native";
import { aiAPI, consultationsAPI } from "../../services/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  // The opening greeting is local-only and must never be replayed to the model.
  local?: boolean;
  urgency?: string;
  recommended_next_step?: string;
  warning_signs?: string[];
  follow_up_questions?: string[];
}

const GREETING: Message = {
  role: "assistant",
  local: true,
  content:
    "Hello! I am your AI Clinical Assistant. Describe your symptoms (e.g., fever, headache, stomach pain) and I will evaluate them and provide guidance.",
};

const NETWORK_ERROR =
  "Cannot reach the server. Check that the backend is running and that your device can reach it.";

export const SymptomAssessmentScreen = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([GREETING]);
  const [loading, setLoading] = useState(false);
  // Threaded so the backend continues one conversation instead of creating a
  // new ChatConversation (and orphaned assessment) for every message.
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [consultationId, setConsultationId] = useState<number | null>(null);
  const scrollRef = useRef<ScrollView>(null);

  const send = async (text: string) => {
    const userMsg = text.trim();
    if (!userMsg || loading) return;
    setInput("");

    const prior = [...messages, { role: "user" as const, content: userMsg }];
    setMessages(prior);
    setLoading(true);

    // The backend takes `message` separately, so history must exclude it.
    const history = messages
      .filter((m) => !m.local)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      let cid = consultationId;
      if (cid === null) {
        const created = await consultationsAPI.create(userMsg);
        cid = created.data.id;
        setConsultationId(cid);
      }

      const res = await aiAPI.analyzeSymptoms({
        patient_input: userMsg,
        history,
        consultation_id: cid ?? undefined,
        conversation_id: conversationId ?? undefined,
      });

      const data = res.data;
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      setMessages([
        ...prior,
        {
          role: "assistant",
          content:
            data.reply ||
            data.general_information ||
            "Based on your description, here is the assessment.",
          urgency: data.urgency_level,
          recommended_next_step: data.recommended_next_step,
          warning_signs: data.warning_signs,
          follow_up_questions: data.follow_up_questions,
        },
      ]);
    } catch (err: any) {
      setMessages([
        ...prior,
        {
          role: "assistant",
          content: err?.response
            ? `Sorry, that assessment failed: ${
                err.response.data?.error || err.response.data?.detail || "server error"
              }`
            : NETWORK_ERROR,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const startOver = () => {
    setMessages([GREETING]);
    setConversationId(null);
    setConsultationId(null);
    setInput("");
  };

  const getUrgencyColor = (level?: string) => {
    switch (level?.toUpperCase()) {
      case "EMERGENCY":
        return "#dc2626";
      case "URGENT":
        return "#ea580c";
      case "NON_URGENT":
        return "#0284c7";
      case "ROUTINE":
      default:
        return "#16a34a";
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>🩺 Symptom Assessment</Text>
          <Text style={styles.headerSub}>AI Triage & Decision Support</Text>
        </View>
        <TouchableOpacity onPress={startOver} disabled={loading}>
          <Text style={styles.newChat}>New</Text>
        </TouchableOpacity>
      </View>

      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        keyboardVerticalOffset={0}
      >
        <ScrollView
          ref={scrollRef}
          contentContainerStyle={styles.chatContainer}
          onContentSizeChange={() => scrollRef.current?.scrollToEnd({ animated: true })}
        >
          {messages.map((msg, index) => (
            <View
              key={index}
              style={[
                styles.bubble,
                msg.role === "user" ? styles.userBubble : styles.assistantBubble,
              ]}
            >
              <Text
                style={[
                  styles.bubbleText,
                  msg.role === "user" ? styles.userText : styles.assistantText,
                ]}
              >
                {msg.content}
              </Text>

              {msg.urgency && (
                <View
                  style={[
                    styles.badge,
                    { backgroundColor: getUrgencyColor(msg.urgency) },
                  ]}
                >
                  <Text style={styles.badgeText}>
                    Urgency: {msg.urgency.replace(/_/g, " ")}
                  </Text>
                </View>
              )}

              {!!msg.warning_signs?.length && (
                <View style={styles.warningBox}>
                  <Text style={styles.warningTitle}>Seek care now if:</Text>
                  {msg.warning_signs.map((sign, sIdx) => (
                    <Text key={sIdx} style={styles.warningText}>
                      • {sign}
                    </Text>
                  ))}
                </View>
              )}

              {msg.recommended_next_step && (
                <View style={styles.recBox}>
                  <Text style={styles.recTitle}>Recommended Action:</Text>
                  <Text style={styles.recText}>{msg.recommended_next_step}</Text>
                </View>
              )}

              {!!msg.follow_up_questions?.length && (
                <View style={styles.followUpBox}>
                  <Text style={styles.followUpTitle}>Please also tell me:</Text>
                  {msg.follow_up_questions.map((q, qIdx) => (
                    <View key={qIdx} style={styles.questionChip}>
                      <Text style={styles.questionChipText}>👉 {q}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>
          ))}

          {loading && (
            <View style={styles.loadingBubble}>
              <ActivityIndicator size="small" color="#0d9488" />
              <Text style={styles.loadingText}>Evaluating symptoms & evidence...</Text>
            </View>
          )}
        </ScrollView>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="Describe symptoms (e.g. fever, headache)..."
            placeholderTextColor="#94a3b8"
            value={input}
            onChangeText={setInput}
            onSubmitEditing={() => send(input)}
            blurOnSubmit={false}
            multiline
          />
          <TouchableOpacity
            style={[styles.sendButton, loading && styles.sendButtonDisabled]}
            onPress={() => send(input)}
            disabled={loading}
          >
            <Text style={styles.sendText}>Send</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  flex: { flex: 1 },
  header: {
    padding: 16,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e2e8f0",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  headerTitle: { fontSize: 20, fontWeight: "bold", color: "#0f766e" },
  headerSub: { fontSize: 13, color: "#64748b" },
  newChat: { fontSize: 14, fontWeight: "600", color: "#0d9488" },
  chatContainer: { padding: 16, gap: 12, paddingBottom: 24 },
  bubble: { maxWidth: "85%", padding: 14, borderRadius: 16, marginBottom: 8 },
  userBubble: { alignSelf: "flex-end", backgroundColor: "#0d9488", borderBottomRightRadius: 2 },
  assistantBubble: { alignSelf: "flex-start", backgroundColor: "#ffffff", borderWidth: 1, borderColor: "#cbd5e1", borderBottomLeftRadius: 2 },
  bubbleText: { fontSize: 15, lineHeight: 22 },
  userText: { color: "#ffffff" },
  assistantText: { color: "#1e293b" },
  badge: { alignSelf: "flex-start", paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12, marginTop: 8 },
  badgeText: { color: "#ffffff", fontSize: 12, fontWeight: "bold" },
  warningBox: { marginTop: 8, padding: 8, backgroundColor: "#fef2f2", borderRadius: 8, borderWidth: 1, borderColor: "#fecaca" },
  warningTitle: { fontSize: 12, fontWeight: "bold", color: "#991b1b" },
  warningText: { fontSize: 13, color: "#b91c1c", marginTop: 2 },
  recBox: { marginTop: 8, padding: 8, backgroundColor: "#f0fdf4", borderRadius: 8, borderWidth: 1, borderColor: "#bbf7d0" },
  recTitle: { fontSize: 12, fontWeight: "bold", color: "#166534" },
  recText: { fontSize: 13, color: "#15803d", marginTop: 2 },
  followUpBox: { marginTop: 10 },
  followUpTitle: { fontSize: 12, fontWeight: "600", color: "#475569", marginBottom: 4 },
  questionChip: { backgroundColor: "#f1f5f9", padding: 8, borderRadius: 8, marginBottom: 4 },
  questionChipText: { fontSize: 13, color: "#0f766e" },
  loadingBubble: { flexDirection: "row", alignItems: "center", gap: 8, padding: 12, backgroundColor: "#ffffff", borderRadius: 12, alignSelf: "flex-start" },
  loadingText: { fontSize: 13, color: "#64748b" },
  inputContainer: { flexDirection: "row", padding: 12, backgroundColor: "#ffffff", borderTopWidth: 1, borderTopColor: "#e2e8f0", alignItems: "flex-end", gap: 8 },
  input: { flex: 1, backgroundColor: "#f1f5f9", borderRadius: 20, paddingHorizontal: 16, paddingVertical: 8, fontSize: 15, maxHeight: 100, color: "#0f172a" },
  sendButton: { backgroundColor: "#0d9488", paddingHorizontal: 18, paddingVertical: 10, borderRadius: 20 },
  sendButtonDisabled: { opacity: 0.5 },
  sendText: { color: "#ffffff", fontWeight: "bold", fontSize: 14 },
});

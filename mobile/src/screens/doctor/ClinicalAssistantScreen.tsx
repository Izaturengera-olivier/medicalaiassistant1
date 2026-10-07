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
import { aiAPI } from "../../services/api";

interface ChatTurn {
  role: "user" | "assistant";
  content: string;
  local?: boolean;
  recommended_next_step?: string;
}

const GREETING: ChatTurn = {
  role: "assistant",
  local: true,
  content:
    "Welcome Doctor / Pharmacist. Ask any professional clinical decision query (differential diagnoses, medication dosages, drug-drug interactions, guideline lookups).",
};

export const ClinicalAssistantScreen = () => {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<ChatTurn[]>([GREETING]);
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const scrollRef = useRef<ScrollView>(null);

  const send = async (text: string) => {
    const userQuery = text.trim();
    if (!userQuery || loading) return;
    setQuery("");

    const updated = [...messages, { role: "user" as const, content: userQuery }];
    setMessages(updated);
    setLoading(true);

    const history = messages
      .filter((m) => !m.local)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      const res = await aiAPI.professionalChat({
        message: userQuery,
        history,
        conversation_id: conversationId ?? undefined,
      });

      if (res.data.conversation_id) {
        setConversationId(res.data.conversation_id);
      }

      setMessages([
        ...updated,
        {
          role: "assistant",
          content:
            res.data.reply ||
            res.data.general_information ||
            "Clinical decision support response ready.",
          recommended_next_step: res.data.recommended_next_step,
        },
      ]);
    } catch (err: any) {
      const status = err?.response?.status;
      let content: string;
      if (status === 403) {
        content =
          "This tool is restricted to doctors, pharmacists, and administrators.";
      } else if (status) {
        content = `Clinical query failed: ${
          err.response.data?.error || err.response.data?.detail || "server error"
        }`;
      } else {
        content =
          "Cannot reach the server. Check that the backend is running and that your device can reach it.";
      }
      setMessages([...updated, { role: "assistant", content }]);
    } finally {
      setLoading(false);
    }
  };

  const startOver = () => {
    setMessages([GREETING]);
    setConversationId(null);
    setQuery("");
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>👨‍⚕️ Clinical Decision Assistant</Text>
          <Text style={styles.headerSub}>Physician & Pharmacist Query Tool</Text>
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
          {messages.map((m, idx) => (
            <View
              key={idx}
              style={[
                styles.bubble,
                m.role === "user" ? styles.userBubble : styles.assistantBubble,
              ]}
            >
              <Text style={[styles.bubbleText, m.role === "user" ? styles.userText : styles.assistantText]}>
                {m.content}
              </Text>

              {m.recommended_next_step && (
                <View style={styles.recBox}>
                  <Text style={styles.recTitle}>Next step:</Text>
                  <Text style={styles.recText}>{m.recommended_next_step}</Text>
                </View>
              )}
            </View>
          ))}

          {loading && (
            <View style={styles.loadingBubble}>
              <ActivityIndicator size="small" color="#0284c7" />
              <Text style={styles.loadingText}>Searching medical corpus & guidelines...</Text>
            </View>
          )}
        </ScrollView>

        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            placeholder="Ask clinical question (e.g. Amoxicillin dosage for pediatric otitis media)..."
            placeholderTextColor="#94a3b8"
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={() => send(query)}
            blurOnSubmit={false}
            multiline
          />
          <TouchableOpacity
            style={[styles.sendButton, loading && styles.sendButtonDisabled]}
            onPress={() => send(query)}
            disabled={loading}
          >
            <Text style={styles.sendText}>Query</Text>
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
  headerTitle: { fontSize: 20, fontWeight: "bold", color: "#0369a1" },
  headerSub: { fontSize: 13, color: "#64748b" },
  newChat: { fontSize: 14, fontWeight: "600", color: "#0284c7" },
  chatContainer: { padding: 16, gap: 12, paddingBottom: 24 },
  bubble: { maxWidth: "85%", padding: 14, borderRadius: 16, marginBottom: 8 },
  userBubble: { alignSelf: "flex-end", backgroundColor: "#0284c7", borderBottomRightRadius: 2 },
  assistantBubble: { alignSelf: "flex-start", backgroundColor: "#ffffff", borderWidth: 1, borderColor: "#cbd5e1", borderBottomLeftRadius: 2 },
  bubbleText: { fontSize: 15, lineHeight: 22 },
  userText: { color: "#ffffff" },
  assistantText: { color: "#1e293b" },
  recBox: { marginTop: 8, padding: 8, backgroundColor: "#eff6ff", borderRadius: 8, borderWidth: 1, borderColor: "#bfdbfe" },
  recTitle: { fontSize: 12, fontWeight: "bold", color: "#1e40af" },
  recText: { fontSize: 13, color: "#1d4ed8", marginTop: 2 },
  loadingBubble: { flexDirection: "row", alignItems: "center", gap: 8, padding: 12, backgroundColor: "#ffffff", borderRadius: 12, alignSelf: "flex-start" },
  loadingText: { fontSize: 13, color: "#64748b" },
  inputContainer: { flexDirection: "row", padding: 12, backgroundColor: "#ffffff", borderTopWidth: 1, borderTopColor: "#e2e8f0", alignItems: "flex-end", gap: 8 },
  input: { flex: 1, backgroundColor: "#f1f5f9", borderRadius: 20, paddingHorizontal: 16, paddingVertical: 8, fontSize: 15, maxHeight: 100, color: "#0f172a" },
  sendButton: { backgroundColor: "#0284c7", paddingHorizontal: 18, paddingVertical: 10, borderRadius: 20 },
  sendButtonDisabled: { opacity: 0.5 },
  sendText: { color: "#ffffff", fontWeight: "bold", fontSize: 14 },
});

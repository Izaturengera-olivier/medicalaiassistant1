import { useState } from "react";
import { useAuth } from "../context/AuthContext";

interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface AIResponse {
  symptoms_identified: string[];
  follow_up_questions: string[];
  possible_conditions: Array<{
    name: string;
    likelihood: string;
    description: string;
  }>;
  warning_signs: string[];
  urgency_level: string;
  general_information: string;
  recommended_next_step: string;
  sources: Array<{
    name: string;
    url: string;
  }>;
}

export function ChatInterface() {
  const { user, isAuthenticated } = useAuth();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      role: "assistant",
      content: "Hello! I'm your clinical decision support assistant. Please describe your symptoms, and I'll help you understand what might be going on. Remember, this is for information only - always consult a healthcare professional for diagnosis and treatment.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState<AIResponse | null>(null);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput("");
    setLoading(true);
    setAiResponse(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/ai/analyze-symptoms/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ patient_input: input }),
      });

      if (response.ok) {
        const data = await response.json();
        setAiResponse(data);

        const assistantMessage: Message = {
          id: messages.length + 2,
          role: "assistant",
          content: formatAIResponse(data),
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        const errorMessage: Message = {
          id: messages.length + 2,
          role: "assistant",
          content: "I'm sorry, I encountered an error processing your request. Please try again.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: messages.length + 2,
        role: "assistant",
        content: "I'm sorry, I encountered an error connecting to the server. Please make sure the backend is running.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const formatAIResponse = (data: AIResponse): string => {
    let response = "";
    
    if (data.symptoms_identified && data.symptoms_identified.length > 0) {
      response += `I've identified these symptoms: ${data.symptoms_identified.join(", ")}.\n\n`;
    }
    
    if (data.possible_conditions && data.possible_conditions.length > 0) {
      response += "Possible conditions to consider:\n";
      data.possible_conditions.forEach((condition, index) => {
        response += `${index + 1}. ${condition.name} (${condition.likelihood} likelihood)\n`;
        response += `   ${condition.description}\n`;
      });
      response += "\n";
    }
    
    if (data.warning_signs && data.warning_signs.length > 0) {
      response += `⚠️ Warning signs detected: ${data.warning_signs.join(", ")}\n\n`;
    }
    
    if (data.urgency_level) {
      response += `Urgency Level: ${data.urgency_level}\n\n`;
    }
    
    if (data.general_information) {
      response += `Information: ${data.general_information}\n\n`;
    }
    
    if (data.recommended_next_step) {
      response += `Recommendation: ${data.recommended_next_step}\n\n`;
    }
    
    if (data.follow_up_questions && data.follow_up_questions.length > 0) {
      response += "I have some follow-up questions:\n";
      data.follow_up_questions.forEach((question, index) => {
        response += `${index + 1}. ${question}\n`;
      });
    }
    
    return response;
  };

  const getUrgencyColor = (level: string) => {
    switch (level) {
      case "URGENT_MEDICAL_ATTENTION":
        return "bg-red-100 text-red-800 border-red-300";
      case "PROMPT_MEDICAL_REVIEW":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "ROUTINE_CONSULTATION":
        return "bg-blue-100 text-blue-800 border-blue-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Please login to use the AI assistant</h2>
          <a href="/login" className="text-blue-600 hover:text-blue-500">Go to Login</a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-gray-900">Clinical AI Assistant</h1>
            <p className="text-sm text-gray-600">Decision Support System</p>
          </div>
          <div className="text-sm text-gray-600">
            {user?.first_name} {user?.last_name}
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 max-w-4xl mx-auto w-full">
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-white border border-gray-200 text-gray-900"
                }`}
              >
                <div className="text-sm font-medium mb-1">
                  {message.role === "user" ? "You" : "AI Assistant"}
                </div>
                <div className="whitespace-pre-wrap">{message.content}</div>
                <div className="text-xs mt-2 opacity-70">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* AI Response Details */}
      {aiResponse && (
        <div className="max-w-4xl mx-auto w-full px-4 pb-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <h3 className="font-bold text-gray-900 mb-3">Assessment Details</h3>
            
            {aiResponse.urgency_level && (
              <div className={`mb-3 p-3 rounded border ${getUrgencyColor(aiResponse.urgency_level)}`}>
                <div className="font-medium">Urgency Level: {aiResponse.urgency_level}</div>
              </div>
            )}
            
            {aiResponse.warning_signs && aiResponse.warning_signs.length > 0 && (
              <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded">
                <div className="font-medium text-red-900 mb-1">⚠️ Warning Signs:</div>
                <ul className="list-disc list-inside text-red-800">
                  {aiResponse.warning_signs.map((sign, index) => (
                    <li key={index}>{sign}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {aiResponse.follow_up_questions && aiResponse.follow_up_questions.length > 0 && (
              <div className="mb-3">
                <div className="font-medium text-gray-900 mb-1">Follow-up Questions:</div>
                <ul className="list-disc list-inside text-gray-700">
                  {aiResponse.follow_up_questions.map((question, index) => (
                    <li key={index}>{question}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {aiResponse.sources && aiResponse.sources.length > 0 && (
              <div className="mb-3">
                <div className="font-medium text-gray-900 mb-1">Sources:</div>
                <ul className="list-disc list-inside text-gray-700">
                  {aiResponse.sources.map((source, index) => (
                    <li key={index}>
                      <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                        {source.name}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-900">
              <strong>Disclaimer:</strong> This system provides decision-support information only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns.
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="bg-white border-t p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Describe your symptoms..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            This AI assistant provides information only. It does not provide medical advice, diagnosis, or treatment.
          </p>
        </div>
      </div>
    </div>
  );
}
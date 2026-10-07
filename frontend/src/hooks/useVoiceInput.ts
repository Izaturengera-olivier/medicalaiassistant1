import { useEffect, useRef, useState } from "react";
import { getRecognitionConstructor, type SpeechRecognitionLike } from "../utils/voice";

interface Options {
  lang: string;
  onTranscript: (text: string) => void;
  onError?: (code: string) => void;
}

export function useVoiceInput(options: Options) {
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const optionsRef = useRef(options);
  optionsRef.current = options;

  useEffect(() => {
    const Ctor = getRecognitionConstructor();
    setSupported(Boolean(Ctor));
    if (!Ctor) return;

    const recognition = new Ctor();
    recognition.lang = optionsRef.current.lang;
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0]?.transcript ?? "")
        .join(" ")
        .trim();
      if (transcript) optionsRef.current.onTranscript(transcript);
    };
    recognition.onerror = (event: any) => {
      optionsRef.current.onError?.(event?.error ?? "voice_input_failed");
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;

    return () => {
      recognition.stop();
      recognitionRef.current = null;
    };
  }, []);

  const toggle = () => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      optionsRef.current.onError?.("unsupported");
      return;
    }
    if (listening) {
      recognition.stop();
      setListening(false);
      return;
    }
    recognition.lang = optionsRef.current.lang;
    recognition.start();
    setListening(true);
  };

  return { supported, listening, toggle };
}

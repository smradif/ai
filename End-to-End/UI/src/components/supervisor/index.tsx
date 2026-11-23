import React, { useState, useRef, useEffect } from "react";
import { v4 as uuid } from "uuid";
import {
  getSuervisorResponse,
  isAuthenticated,
  redirectToLogin,
} from "../../service";

interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: Date;
}

interface User {
  name: string;
  age: number;
}
const userId = Date.now().toString();

export const Supervisor = (): JSX.Element => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [sessionId, setSessionId] = useState<string>(uuid());

  const sendRequuest = async (query: string) => {

    setError("");

    // Add user message to chat
    if (query.trim()) {
      const userMessage: Message = {
        id: userId,
        type: "user",
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
    }

    // Clear input
    setInput("");
    setIsLoading(true);

    try {
      const reader = await getSuervisorResponse({
        id: userId,
        name: "",
        query,
        session_id: sessionId,
      });

      const decoder = new TextDecoder();
      let agentContent = "";
      let agentMessageId = Date.now().toString();

      // Add initial agent message
      setMessages((prev) => [
        ...prev,
        {
          id: agentMessageId,
          type: "agent",
          content: "",
          timestamp: new Date(),
        },
      ]);

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonData = JSON.parse(line.slice(6));
              console.log("Parsed JSON data:", line);
              if (jsonData.status === "partial" && jsonData.chunk) {
                agentContent += jsonData.chunk;
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === agentMessageId
                      ? { ...msg, content: agentContent }
                      : msg,
                  ),
                );
              } else if (jsonData.status === "done") {
                setIsLoading(false);
              }
            } catch (parseError) {
              // Silently handle parse errors for non-JSON lines
            }
          }
        }

        if (messages.at(-1)?.content.startsWith("**Error**")) {
          setError(
            messages.at(-1)?.content.replace("**Error**", "Error").trim() ||
              "An error occurred",
          );
        }
      }
      inputRef.current?.focus();
    } catch (err) {
      if (err instanceof Error && err.name === "AuthError") {
        redirectToLogin("supervisor");
      }
      setIsLoading(false);
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Failed to get response from agent";
      setError(errorMessage);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          type: "agent",
          content: `${errorMessage}`,
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleReset = async () => {
    setMessages([]);
    setInput("reset");
    setError("");
    setIsLoading(false);
    setSessionId(uuid());
    await sendRequuest("reset");
  };

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin("supervisor");
    }
  }, []);
  useEffect(() => {
    if (messages.length === 0) {
      sendRequuest("");
    }
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    inputRef.current?.focus();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    sendRequuest(input);
    inputRef.current?.focus();
  };
  return (
    <div className="money-transfer-agent-container">
      <div className="money-transfer-container">
        <div className="chat-header">
          <h1>Supervisor</h1>
          <p>Ask any question to the agent</p>
        </div>

        <div className="messages-container">
          {messages.length === 0 && !isLoading && (
            <div className="empty-state">
              <p>No messages yet. Ask me something!</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={`${message.id}-${index}`}
              className={`message message-${message.type}`}
            >
              <div className="message-label">
                {message.type === "user" ? "👤 You" : "🤖 Agent"}
              </div>
              <div className="message-content">{message.content}</div>
            </div>
          ))}

          {isLoading && (
            <div className="message message-agent">
              <div className="message-label">🤖 Agent</div>
              <div className="message-content loading">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          {error && <div className="error-message">{error}</div>}

          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything..."
              disabled={isLoading}
              className="input-field"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="submit-button"
            >
              {isLoading ? "Thinking..." : "Send"}
            </button>
            <button
              type="button"
              className="submit-button"
              onClick={handleReset}
            >
              Reset
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

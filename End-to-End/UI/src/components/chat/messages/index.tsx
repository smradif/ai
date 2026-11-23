import React, { useState, useRef, useEffect } from "react";
import {
  getChatResponse,
  getChatHistoryResponse,
  isAuthenticated,
  redirectToLogin,
} from "../../../service";
import { ChatHistoryResponse, VendorResponse } from "../../../types";
import { v4 as uuid } from "uuid";
import { Vendor } from "../../vendor";

type Props = {
  vendors: VendorResponse[];
  selectedChatId?: number;
  setSelectedChatId: (id: number | undefined) => void;
};

interface Message {
  id: string;
  type: "HumanMessage" | "AIMessage";
  content: string;
  timestamp: Date;
}

export const ChatMessages = ({
  vendors,
  selectedChatId,
  setSelectedChatId,
}: Props): JSX.Element => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedVendor, setVendor] = useState<number | undefined>(undefined);
  const [sessionId, setSessionId] = useState<string>(uuid());

  const getHistoryItem = async () => {
    if (selectedChatId) {
      const historyItem =
        await getChatHistoryResponse<ChatHistoryResponse>(selectedChatId);
      if (historyItem) {
        setMessages(
          JSON.parse(historyItem.conversation).map((msg: any) => ({
            id: uuid(),
            type: msg.type,
            content: msg.content,
            timestamp: new Date(msg.timestamp),
          })),
        );
      }
    }
  };

  const sendRequuest = async (query: string) => {
    if (selectedChatId === undefined && !query.trim()) {
      setError("Please enter a question");
      return;
    }
    setIsLoading(true);
    setInput("");
    setError("");

    const isReseting = query === "reset";
    if (!isReseting) {
      const userMessage: Message = {
        id: uuid(),
        type: "HumanMessage",
        content: query,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
    }

    try {
      const reader = await getChatResponse({
        name: "",
        query,
        vendor_id: selectedVendor,
        session_id: sessionId,
        previous_state_id: selectedChatId,
      });

      const decoder = new TextDecoder();
      let agentContent = "";
      let agentMessageId = uuid();

      setMessages((prev) => [
        ...prev,
        {
          id: agentMessageId,
          type: "AIMessage",
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
        redirectToLogin("chat")
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
          id: uuid(),
          type: "AIMessage",
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

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    sendRequuest(input);
    inputRef.current?.focus();
  };

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin("chat")
    }
  }, []);

  useEffect(() => {
    inputRef.current?.focus();
  }, [messages]);

  useEffect(() => {
    if (selectedChatId) {
      sendRequuest("");
      getHistoryItem();
      setSelectedChatId(undefined);
    }
  }, [selectedChatId]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>AI Agent Chat</h1>
        <p>Ask any question to the agent</p>
        <div className="vendors-list">
          {vendors.map((vendor) => {
            return (
              <Vendor
                key={vendor.id}
                id={vendor.id}
                name={vendor.name}
                isSelected={vendor.id === selectedVendor}
                onClick={(id) => {
                  setVendor(id);
                  handleReset();
                }}
              />
            );
          })}
        </div>
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
              {message.type === "HumanMessage" ? "👤 You" : "🤖 Agent"}
            </div>
            <div className="message-content">{message.content}</div>
          </div>
        ))}

        {isLoading && (
          <div className="message message-agent">
            <div className="message-label">Thinking...</div>
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
            disabled={isLoading || messages.length === 0}
          >
            Start over
          </button>
        </div>
      </form>
    </div>
  );
};

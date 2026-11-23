import React, { useState, useEffect } from "react";
import {
  getChatResponse,
  getVendorsResponse,
  getChatsHistoryResponse,
  getChatHistoryResponse,
  isAuthenticated,
} from "../../../service";
import { ChatHistoryResponse } from "../../../types";
import { ChatHistoryItem } from "./historyItem";

type Props = {
  selectedChatId: number | undefined;
  selectedVendorId?: number;
  onSelected: (id: number) => void;
};
export const ChatHistory = ({
  selectedChatId,
  selectedVendorId,
  onSelected,
}: Props): JSX.Element => {
  const [historyItems, setHistoryItems] = useState<ChatHistoryResponse[]>([]);

  const getHistoryItems = async () => {
    if(selectedVendorId){
      const historyItems =
        await getChatsHistoryResponse<ChatHistoryResponse[]>(selectedVendorId);
      setHistoryItems(historyItems || []);
    }
  };

  useEffect(() => {
    if (selectedVendorId) {
      getHistoryItems();
    }
  }, [selectedVendorId]);

  return (
    <div className="chat_history">
      <h2>Chat History</h2>
      {historyItems.length === 0 && <p>No history items found.</p>}
      {historyItems.map((item) => (
        <ChatHistoryItem
         key={item.id}
          historyItem={item}
          isSelected={selectedChatId === item.id}
          onSelected={onSelected}
        />
      ))}
    </div>
  );
};

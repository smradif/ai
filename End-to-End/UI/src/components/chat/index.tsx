import React, { useState, useRef, useEffect } from "react";
import {
  getVendorsResponse,
  isAuthenticated,
  redirectToLogin,
} from "../../service";
import { VendorResponse } from "../../types";
import { v4 as uuid } from "uuid";
import { ChatMessages } from "./messages";
import { ChatHistory } from "./history";

interface Message {
  id: string;
  type: "user" | "agent";
  content: string;
  timestamp: Date;
}

export const Chat = (): JSX.Element => {
  const [vendors, setVendors] = useState<VendorResponse[]>([]);
  const [selectedVendor, setVendor] = useState<number | undefined>(undefined);
  const [selectedChatId, setSelectedChatId] = useState<number | undefined>(
    undefined,
  );

  const getVendors = async () => {
    const vendors = await getVendorsResponse<VendorResponse[]>();
    if (vendors.length > 0) {
      setVendors(vendors);
      setVendor(vendors[0].id);
    }
  };

  useEffect(() => {
    if (!isAuthenticated()) {
      redirectToLogin("chat");
    }
  }, []);

  useEffect(() => {
    getVendors();
  }, []);

  return (
    <div className="chat-agent-container">
      <ChatHistory
        selectedVendorId={selectedVendor}
        selectedChatId={selectedChatId}
        onSelected={(id: number) => {
          setSelectedChatId(id);
        }}
      />
      <ChatMessages
        vendors={vendors}
        selectedChatId={selectedChatId}
        setSelectedChatId={setSelectedChatId}
      />
    </div>
  );
};

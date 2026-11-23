import React, { useState, useEffect } from "react";
import { ChatHistoryResponse } from "../../../../types";

type Props = {
  isSelected: boolean;
  historyItem: ChatHistoryResponse;
  onSelected: (id: number) => void;
};
export const ChatHistoryItem = ({
  isSelected,
  historyItem,
  onSelected,
}: Props): JSX.Element => {
  const { id, title } = historyItem;
  const className = isSelected ? "history-item selected-history-item" : "history-item";
  return (
    <div
      className={className}
      onClick={() => {
        onSelected(id);
      }}
    >
      {title}
    </div>
  );
};

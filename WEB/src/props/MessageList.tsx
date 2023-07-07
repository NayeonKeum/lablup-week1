import React, { useState } from "react";
import Message from "./Message";
import "../styles/home.css";

export type MessageType = {
  curUser: String;
  sender: string;
  time: string;
  content: string;
};

const MessageList = ({ messageList }: { messageList: MessageType[] }) => {
  const filteredMessageList: MessageType[] = [];
  // Filter list with length
  for (let i = 0; i < messageList.length; i++) {
    filteredMessageList.push(messageList[i]);
  }
  return (
    <div>
      {filteredMessageList &&
        filteredMessageList.map((message) => (
          <Message message={message}></Message>
        ))}
    </div>
  );
};

export default MessageList;

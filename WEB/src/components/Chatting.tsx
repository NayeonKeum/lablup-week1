import React, { useContext, useState } from "react";
import { WebSocketContext } from "../websocket/WebSocketProvider";
import MessageList, { MessageType } from "../props/MessageList";

function Chatting({ name }: { name: String }) {
  const ws = useContext(WebSocketContext);
  const [messageList, setMessageList] = useState<MessageType[]>([]);

  // props list
  const addMessage = (message: MessageType) => {
    setMessageList([...messageList, message]);
  };

  ws.current.onmessage = (evt: MessageEvent) => {
    // props list
    const data = JSON.parse(evt.data);
    const sender = data.content.split(": ")[0];
    const content = data.content.split(": ")[1];
    const time = data.time.split(".")[0];
    var message: MessageType = {
      curUser: name,
      sender: sender,
      content: content,
      time: time,
    };
    addMessage(message);
  };

  return (
    <div>
      <MessageList messageList={messageList} />
    </div>
  );
}

export default Chatting;

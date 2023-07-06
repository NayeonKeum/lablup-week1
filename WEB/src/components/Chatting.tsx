import React, { useContext, useState } from "react";
import { WebSocketContext } from "../websocket/WebSocketProvider";

function Chatting({ name }: { name: String }) {
  const ws = useContext(WebSocketContext);
  const [items, setItems] = useState<string[]>([]);

  const addItem = (item: string) => {
    setItems([...items, item]);
  };

  ws.current.onmessage = (evt: MessageEvent) => {
    var content = JSON.parse(evt.data).content;
    // my chat
    // test docker ci
    if (content.startsWith(name + ": ")) {
      content = content.split(": ")[1];
    }
    addItem(content);
  };

  return (
    <ul>
      {items.map((message) => {
        return <li>{message}</li>;
      })}
    </ul>
  );
}

export default Chatting;

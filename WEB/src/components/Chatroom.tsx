import React, { FC } from "react";
import "../styles/home.css";
import Chatting from "./Chatting";
import TextInputBox from "./TextInputBox";
import WebSocketProvider from "../websocket/WebSocketProvider";
import { useLocation } from "react-router-dom";
const Chatroom: FC = () => {
  const location = useLocation();
  const name = location.state.name;
  return (
    <div>
      <h1> Hi {name} 👋</h1>
      <WebSocketProvider>
        <Chatting name={name} />
        <TextInputBox name={name} />
      </WebSocketProvider>
    </div>
  );
};
export default Chatroom;
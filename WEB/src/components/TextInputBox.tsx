import React, { useState, useContext } from "react";
import { WebSocketContext } from "../websocket/WebSocketProvider";
import "../styles/chat.css";

function TextInputBox({ name }: { name: String }) {
  const [message, setMessage] = useState("");
  const [isAvailable, setIsAvailable] = useState<boolean>(true);
  const ws = useContext(WebSocketContext);

  const handleChangeText = (e: any) => {
    setMessage(e.target.value);
  };

  const handleClickSubmit = () => {
    ws.current.send(message);
    setMessage("");
    if (message == "quit") {
      setIsAvailable(false);
    }
  };

  return (
    <div>
      {isAvailable && (
        <div className="text-input-box">
          <input
            type="text"
            value={message}
            onChange={handleChangeText}
          ></input>
          <button type="button" onClick={handleClickSubmit}>
            Send!
          </button>
        </div>
      )}
      {!isAvailable && (
        <div>
          <p>채팅방을 나가셨습니다.</p>
        </div>
      )}
    </div>
  );
}

export default TextInputBox;

import React, { useState, useContext } from "react";
import { WebSocketContext } from "../websocket/WebSocketProvider";
import "../styles/chat.css";

function TextInputBox() {
  const [message, setMessage] = useState("");
  const [isAvailable, setIsAvailable] = useState<boolean>(true);
  const ws = useContext(WebSocketContext);

  const handleChangeText = (e: any) => {
    setMessage(e.target.value);
  };

  const handleClickSend = () => {
    ws.current.send(message);
    setMessage("");
    if (message == "quit") {
      setIsAvailable(false);
    }
  };
  const handleClickQuit = () => {
    ws.current.send("quit");
    setMessage("");
    setIsAvailable(false);
  };

  return (
    <div>
      {isAvailable && (
        <div className="text-input-box">
          <div className="text-input">
            <input
              type="text"
              className="form-control form-control-sm"
              value={message}
              onChange={handleChangeText}
            />
          </div>
          <button
            className="btn btn-outline-success text-center mb-3 text-input-btn"
            type="button"
            onClick={handleClickSend}
          >
            Send
          </button>
          <button
            className="btn btn-outline-danger text-center mb-3 text-input-btn"
            type="button"
            onClick={handleClickQuit}
          >
            Quit
          </button>
        </div>
      )}
      {!isAvailable && (
        <div className="text-input-box">
          <div>
            <p>채팅방을 나가셨습니다.</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default TextInputBox;

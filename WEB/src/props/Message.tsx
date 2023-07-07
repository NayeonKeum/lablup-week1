import React, { useEffect, useState } from "react";
import { MessageType } from "./MessageList";
import "../styles/chat.css";
type MessageProps = {
  message: MessageType;
};
const Message = ({ message }: MessageProps) => {
  const { curUser, sender, time, content } = message;
  const [type, setType] = useState<number>(2); // 0: server, 1: mine, 2: others

  // Set only at first
  useEffect(() => {
    if (sender == "server") {
      // server message
      setType(0);
    } else if (sender == curUser) {
      // My message
      setType(1);
    }
  }, []);

  return (
    <div className="card mb-2 mt-2 rounded">
      {type == 0 && (
        <div className="card-body server-chat">
          <p className="">{content}</p>
        </div>
      )}
      {type == 1 && (
        <div className="card-body my-chat">
          <h3 className="">{content}</h3>
          <p className="">&nbsp;&nbsp;{time}</p>
        </div>
      )}
      {type == 2 && (
        <div className="card-body others-chat">
          <h3 className="">
            {sender}: {content}
          </h3>
          <p className="">&nbsp;&nbsp;{time}</p>
        </div>
      )}
    </div>
  );
};

export default Message;

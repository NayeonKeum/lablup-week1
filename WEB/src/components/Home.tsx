import React, { FC, useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import "../styles/home.css";
import axios from "axios";
import Chatting from "./Chatting";
import TextInputBox from "./TextInputBox";
import WebSocketProvider from "../websocket/WebSocketProvider";
const Home: FC = (): JSX.Element => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const [isNameSet, setisNameSet] = useState<boolean>(false);
  const [name, setName] = useState<String>("");

  const login = async (data: any) => {
    setName(data.name);
    let params = {
      name: data.name,
    };
    console.log(params);
    axios
      .post("http://localhost:8080/", new URLSearchParams(params))
      .then(function (response) {
        console.log("success... print response");
        console.log(response);
        if (response.data == "Success") {
          alert("로그인 성공!");
          setisNameSet(true);
        }
      })
      .catch(function (error) {
        console.log("error accured");
        console.log(error);
      });
  };

  return (
    <div>
      {!isNameSet && (
        <div>
          <h1>Login to Chat</h1>
          <form autoComplete="off" onSubmit={handleSubmit(login)}>
            <div className="">
              <label className="form-label">이름을 입력해주세요.</label>
              <input
                type="text"
                className="form-control form-control-sm"
                id="exampleFormControlInput3"
                {...register("name", {
                  required: "name is required!",
                })}
              />
              {errors.name && (
                <p className="text-danger" style={{ fontSize: 14 }}>
                  Error in name
                </p>
              )}
            </div>
            <button
              className="btn btn-outline-primary text-center shadow-none mb-3"
              type="submit"
            >
              로그인
            </button>
          </form>
        </div>
      )}
      {isNameSet && (
        <div>
          <h1> Hi {name} 👋</h1>
          <WebSocketProvider>
            <Chatting />
            <TextInputBox />
          </WebSocketProvider>
        </div>
      )}
    </div>
  );
};
export default Home;

import React, { FC, useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import "../styles/home.css";
import axios from "axios";
import { useNavigate } from "react-router-dom";
const Home: FC = (): JSX.Element => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const navigate = useNavigate();
  const login = async (data: any) => {
    let params = {
      name: data.name,
    };
    axios
      .post("http://localhost:8080/", new URLSearchParams(params))
      .then(function (response) {
        if (response.data == "Success") {
          alert("로그인 성공!");
        }
        navigate("/chatroom", {
          state: { name: data.name },
        });
      })
      .catch(function (error) {
        console.log("error accured");
        console.log(error);
      });
  };

  return (
    <div>
      <h1>Login</h1>
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
  );
};
export default Home;

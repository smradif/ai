import React, { useState, useRef, useEffect } from "react";
import { Money } from "./components/money";
import { RegistrationPage } from "./components/user/register";
import { SignInPage } from "./components/user/signIn";
import { Chat } from "./components/chat";
import { Supervisor } from "./components/supervisor";
import { Orchestrator } from "./components/orchestrator";
import { Page } from "./types";

export const App = (): JSX.Element => {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";

  const pages: Page[] = [
    {
      id: 1,
      title: "Chat",
      path: "/chat",
      component: () => <Chat />,
      isMenuItem: true,
    },
    {
      id: 2,
      title: "Money transfer",
      path: "/money",
      component: () => <Money />,
      isMenuItem: true,
    },
    {
      id: 3,
      title: "Supervisor",
      path: "/supervisor",
      component: () => <Supervisor />,
      isMenuItem: true,
    },
    {
      id: 4,
      title: "Orchestrator",
      path: "/orchestrator",
      component: () => <Orchestrator />,
      isMenuItem: true,
    },
    { id: 5, title: "Login", path: "/login", component: () => <SignInPage /> },
    {
      id: 6,
      title: "Register",
      path: "/register",
      component: () => <RegistrationPage />,
    },
  ];

  const getPage = () => {
    const page = pages.find((page) => page.path === path);
    if (page) {
      return page.component();
    }
    return <Chat />;
  };

  return (
    <div className="app">
      <div className="menu">
        {pages
          .filter((page) => page.isMenuItem)
          .map((page) => {
            return (
              <a href={path !== page.path ? page.path : "javascript: void(0)"}>
                {page.title}
              </a>
            );
          })}
      </div>
      {getPage()}
    </div>
  );
};

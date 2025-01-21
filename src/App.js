import React from "react";
import "./App.css"; // Import CSS globally

import Signup from "./Components/Signup";
import Login from "./Components/Login";

function App() {
  return (
    <div>
      <h1>Signup and Login</h1>
      <Signup />
      <Login />
    </div>
  );
}

export default App;

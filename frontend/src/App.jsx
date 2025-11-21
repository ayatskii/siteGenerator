import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import AppNavBar from "./components/AppNavBar";

  return (
    <div className="md:h-screen bg-blue-50">
      <BrowserRouter>
        <ToastContainer />
        <AppNavBar/>
        <div>
          <Routes>
            <Route path="/" exact
              element={
                <Home isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />
              }
            />
            <Route path="register" exact
              element={
                <Register
                  isLoggedIn={isLoggedIn}
                  setIsLoggedIn={setIsLoggedIn}
                  setName={setName}
                  setEmail={setEmail}
                />
              }
            />
            <Route path="login" exact
              element={
                <Login
                  isLoggedIn={isLoggedIn}
                  setIsLoggedIn={setIsLoggedIn}
                  setName={setName}
                  setEmail={setEmail}
                />
              }
            />
};

export default App;
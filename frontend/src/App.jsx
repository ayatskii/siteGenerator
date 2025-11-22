import { useState, useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";

import AppNavBar from "./components/AppNavBar";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import SiteDashboard from "./pages/SiteDashboard";
import PageEditor from "./pages/PageEditor";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsLoggedIn(true);
    }
  }, []);

  return (
    <div className="md:h-screen bg-blue-50">
      <BrowserRouter>
        <ToastContainer />
        <AppNavBar isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} name={name} />
        <div>
          <Routes>
            <Route path="/" element={<Home isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} />} />
            <Route path="/register" element={<Register isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} setName={setName} setEmail={setEmail} />} />
            <Route path="/login" element={<Login isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} setName={setName} setEmail={setEmail} />} />
            <Route path="/sites/:siteId" element={<SiteDashboard />} />
            <Route path="/sites/:siteId/pages/:pageId" element={<PageEditor />} />
          </Routes>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
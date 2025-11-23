import { useState, useEffect } from "react";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import "./App.css";
import api from "./services/api";

import AppNavBar from "./components/AppNavBar";
import SidebarLayout from "./components/SidebarLayout";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import CreateSite from "./pages/CreateSite";
import SiteDashboard from "./pages/SiteDashboard";
import PageEditor from "./pages/PageEditor";
import PromptManager from "./pages/PromptManager";
import AnalyticsDashboard from "./components/analytics/AnalyticsDashboard";
import Settings from "./pages/Settings";
import MediaLibrary from "./pages/MediaLibrary";
import Templates from "./pages/Templates";
import SitesList from "./pages/SitesList";
import Profile from "./pages/Profile";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    const fetchUser = async () => {
      if (isLoggedIn) {
        try {
          const response = await api.get("/api/me/");
          if (response.data.success) {
            setName(response.data.user.name);
            setEmail(response.data.user.email);
          }
        } catch (error) {
          console.error("Failed to fetch user profile:", error);
          // If 401, the interceptor will handle redirect, but we should update state
          if (error.response && error.response.status === 401) {
            setIsLoggedIn(false);
            setName("");
            setEmail("");
          }
        }
      }
    };

    fetchUser();
  }, [isLoggedIn]);

  return (
    <div className="h-screen bg-gray-50">
      <BrowserRouter>
        <ToastContainer />
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/register" 
            element={
              <>
                <AppNavBar isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} name={name} setName={setName} email={email} setEmail={setEmail} />
                <Register isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} setName={setName} setEmail={setEmail} />
              </>
            } 
          />
          <Route 
            path="/login" 
            element={
              isLoggedIn ? <Navigate to="/" replace /> : (
                <>
                  <AppNavBar isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} name={name} setName={setName} email={email} setEmail={setEmail} />
                  <Login isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} setName={setName} setEmail={setEmail} />
                </>
              )
            } 
          />

          {/* Protected Routes with Sidebar */}
          {isLoggedIn ? (
            <Route element={<SidebarLayout isLoggedIn={isLoggedIn} setIsLoggedIn={setIsLoggedIn} name={name} setName={setName} email={email} setEmail={setEmail} />}>
              <Route path="/" element={<Home />} />
              <Route path="/create-site" element={<CreateSite />} />
              <Route path="/media-library" element={<MediaLibrary />} />
              <Route path="/analytics" element={<AnalyticsDashboard />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/prompts" element={<PromptManager />} />
              <Route path="/templates" element={<Templates />} />
              <Route path="/sites-list" element={<SitesList />} />
              <Route path="/sites/:siteId" element={<SiteDashboard />} />
              <Route path="/sites/:siteId/analytics" element={<AnalyticsDashboard />} />
              <Route path="/sites/:siteId/pages/:pageId" element={<PageEditor />} />
              <Route path="/profile" element={<Profile isLoggedIn={isLoggedIn} name={name} email={email} />} />
            </Route>
          ) : (
            // Redirect to login if accessing protected routes while logged out
            <Route path="*" element={<Navigate to="/login" replace />} />
          )}
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
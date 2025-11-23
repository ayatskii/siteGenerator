import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button } from "./ui";
import LanguageSwitcher from "./LanguageSwitcher";

/**
 * AppNavBar - Public-facing navigation for non-authenticated pages
 * Only shows on Login/Register pages
 */
const AppNavBar = (props) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isLoggedIn, setIsLoggedIn, setName, setEmail } = props;

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    setName("");
    setEmail("");
    navigate("/login");
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo/Brand */}
          <Link to="/" className="flex items-center">
            <span className="text-2xl font-bold text-blue-600">Site Generator</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-4">
            <LanguageSwitcher />
            {!isLoggedIn ? (
              <>
                <Link
                  to="/login"
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
                >
                  {t('auth.loginButton')}
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">
                    {t('auth.getStarted')}
                  </Button>
                </Link>
              </>
            ) : (
              <Button variant="outline" size="sm" onClick={handleLogout}>
                {t('nav.logout')}
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default AppNavBar;

import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { toast } from "react-toastify";
import { Button, Input, Card } from "../components/ui";

const Login = (props) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isLoggedIn, setIsLoggedIn, setName, setEmail } = props;
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: false,
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isLoggedIn) navigate("/");
  }, [isLoggedIn, navigate]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const res = await api.post("/api/login/", {
        email: formData.email,
        password: formData.password,
      });
      
      const data = res.data;
      
      if (data.access) {
        localStorage.setItem("token", data.access);
        if (data.refresh) localStorage.setItem("refresh_token", data.refresh);
        
        toast.success("Login successful!");
        
        // Fetch user details
        try {
            const userRes = await api.get("/api/me/");
            if (userRes.data.success) {
                setName(userRes.data.user.name);
                setEmail(userRes.data.user.email);
            }
        } catch (err) {
            console.error("Failed to fetch user details", err);
        }

        setIsLoggedIn(true);
        navigate("/");
      } else {
        toast.error("Login failed: No token received");
      }
    } catch (error) {
      console.error("Login error:", error);
      const msg = error.response?.data?.detail || "Login failed";
      toast.error(msg);
      
      // Set field-specific errors if available
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Site Generator</h1>
          <h2 className="mt-2 text-xl text-gray-600">{t('auth.loginTitle')}</h2>
        </div>

        <Card>
          <form onSubmit={handleLogin} className="space-y-6">
            <Input
              label={t('auth.email')}
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="you@example.com"
              error={errors.email}
              required
            />

            <Input
              label={t('auth.password')}
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              error={errors.password}
              required
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember"
                  name="remember"
                  type="checkbox"
                  checked={formData.remember}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="remember" className="ml-2 block text-sm text-gray-700">
                  Remember me
                </label>
              </div>

              <Link
                to="/forgot-password"
                className="text-sm font-medium text-blue-600 hover:text-blue-500"
              >
                {t('auth.forgotPassword')}
              </Link>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              disabled={loading}
            >
              {loading ? t('common.loading') : t('auth.loginButton')}
            </Button>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                {t('auth.noAccount')}{" "}
                <Link
                  to="/register"
                  className="font-medium text-blue-600 hover:text-blue-500"
                >
                  {t('auth.registerButton')}
                </Link>
              </p>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Login;
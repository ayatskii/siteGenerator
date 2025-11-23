import axios from "axios";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const URL = import.meta.env.VITE_BACKEND_URL + "/api/forgotPassword";

const ForgotPassword = () => {
  const { t } = useTranslation();
  const handleSubmit = async (ev) => {
    ev.preventDefault();
    const email = ev.target.email.value;
    const formData = { email: email };
    const res = await axios.post(URL, formData);
    const data = res.data;
    if (data.success === true) toast.success(data.message);
    else toast.error(data.message);
  };

  return (
    <div className="flex justify-center my-4">
      <div className="w-full max-w-lg p-6 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
        <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white text-center">{t('auth.resetTitle')}</h5>
        <form className="flex max-w-md flex-col gap-4" onSubmit={handleSubmit}>
          <div>
            <div className="mb-2 block">
              <label htmlFor="email" className="text-sm font-medium required">{t('auth.email')}</label>
            </div>
            <input id="email" type="email" name="email" placeholder={t('auth.resetDesc')} required
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            />
          </div>
          <div className="mt-2 block">
            <button type="submit" className="w-full focus:outline-none text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-800">
              {t('auth.sendResetLink')}
            </button>
          </div>
          <p className="text-center text-sm text-gray-500">
            {t('auth.rememberPassword')}{" "}
            <a href="login" className="font-semibold leading-6 text-blue-600 hover:text-blue-500">
              {t('auth.backToLogin')}
            </a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default ForgotPassword;
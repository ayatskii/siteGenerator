import { React } from "react";
import axios from "axios";
import { useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const URL = import.meta.env.VITE_BACKEND_URL + "/api/resetPassword";

const ResetPassword = () => {
  const [searchParams] = useSearchParams();
  let navigate = useNavigate();
  const { t } = useTranslation();
  const id = searchParams.get("id");
  const token = searchParams.get("token");

  const handleResetPassword = async (ev) => {
    ev.preventDefault();
    const newpassword = ev.target.newpassword.value;
    const confirmpassword = ev.target.confirmpassword.value;
    if (newpassword !== confirmpassword)
      toast.error(t('auth.passwordsDoNotMatch'));
    const formData = { id: id, token: token, password: newpassword };
    const res = await axios.post(URL, formData);
    const data = res.data;
    if (data.success === true) {
      toast.success(data.message);
      navigate("/login");
    } else toast.error(data.message);
  };

  return (
    <div className="w-full flex justify-center my-4">
      <div className="w-full max-w-lg p-6 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
        <h5 className="text-2xl font-bold tracking-tight text-gray-900 dark:text-white text-center">
          {t('auth.resetTitle')}
        </h5>
        <form className="w-full flex max-w-md flex-col gap-4"onSubmit={handleResetPassword}>
          <div>
            <div className="mb-2 block">
              <label htmlFor="newpassword" className="text-sm font-medium required">
                {t('auth.newPassword')}
              </label>
            </div>
            <input id="newpassword" name="newpassword" type="password" placeholder={t('auth.newPassword')} required
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            />
          </div>
          <div>
            <div className="mb-2 block">
              <label htmlFor="confirmpassword" className="text-sm font-medium required">
                {t('auth.confirmNewPassword')}
              </label>
            </div>
            <input id="confirmpassword" name="confirmpassword" type="password" placeholder={t('auth.confirmNewPassword')} required
              className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            />
          </div>
          <div className="mt-2 block">
            <button type="submit" className="w-full focus:outline-none text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-800">
              {t('auth.resetPasswordButton')}
            </button>
          </div>

          <p className="text-center text-sm text-gray-500">
            {t('auth.notRegistered')}{" "}
            <a href="register" className="font-semibold leading-6 text-blue-600 hover:text-blue-500">
              {t('auth.registerHere')}
            </a>
          </p>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
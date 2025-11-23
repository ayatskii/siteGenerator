import { useEffect } from "react";
import UserIcon from "../images/user.png";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

const Profile = (props) => {
  const { isLoggedIn, name, email } = props;
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    if (!isLoggedIn) {
        navigate('/login');
    }
  }, [isLoggedIn, navigate]);

  return (
    <div className="flex items-center justify-center mt-5">
      <div className="w-full max-w-lg p-6 bg-white border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700">
        <div className="flex flex-col items-center pb-10">
          <img alt={t('profile.userIconAlt')} width="96" height="96" src={UserIcon} className="mb-3 rounded-full shadow-lg"/>
          <h5 className="mb-1 text-xl font-medium text-gray-900 dark:text-white">{name}</h5>
          <span className="text-sm text-gray-500 dark:text-gray-400">{email}</span>
        </div>
      </div>
    </div>
  );
};

export default Profile;
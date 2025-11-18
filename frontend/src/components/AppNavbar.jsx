import { 
  Avatar,
  Dropdown,
  DropdownDivider,
  DropdownHeader,
  DropdownItem,
  Navbar,
  NavbarBrand,
  NavbarCollapse,
  NavbarLink,
  NavbarToggle
} from "flowbite-react";
import UserIcon from "../images/user.png";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";

const AppNavBar = (props) => {
  let navigate = useNavigate();

  const { isLoggedIn, setIsLoggedIn, name, setName, email, setEmail } = props;

  const handleLogout = () => {
    setIsLoggedIn(false);
    setName(null);
    setEmail(null);
    navigate("/");
    toast.success("You are successfully logged out!");
  };

  return (
    <Navbar fluid>
      <NavbarBrand href="https://girishgr8.github.io">
        <img
          src="https://media.geeksforgeeks.org/wp-content/uploads/20210224040124/JSBinCollaborativeJavaScriptDebugging6-300x160.png"
          className="mr-3 h-6 sm:h-9"
          alt="Flowbite React Logo"
        />
        <span className="self-center whitespace-nowrap text-3xl font-semibold text-blue-900 dark:text-white">
          GeeksForGeeks
        </span>
      </NavbarBrand>
      
      {isLoggedIn && (
        <div className="flex md:order-2">
          <Dropdown 
            arrowIcon={false} 
            inline
            label={<Avatar alt="User settings" img={UserIcon} rounded />}
          >
            <DropdownHeader>
              <span className="block text-sm">{name}</span>
              <span className="block truncate text-sm font-medium">{email}</span>
            </DropdownHeader>
            <DropdownItem>Settings</DropdownItem>
            <DropdownItem>Your Orders</DropdownItem>
            <DropdownDivider />
            <DropdownItem onClick={handleLogout}>Log out</DropdownItem>
          </Dropdown>
          <NavbarToggle />
        </div>
      )}
      
      <NavbarCollapse>
        <NavbarLink href="/" className="text-lg">Home</NavbarLink>
        <NavbarLink href="#" className="text-lg">About</NavbarLink>
        <NavbarLink href="#" className="text-lg">Services</NavbarLink>
        <NavbarLink href="#" className="text-lg">Pricing</NavbarLink>
        <NavbarLink href="#" className="text-lg">Contact</NavbarLink>
        {!isLoggedIn && (
          <NavbarLink href="/login" className="text-lg">Login</NavbarLink>
        )}
      </NavbarCollapse>
    </Navbar>
  );
};

export default AppNavBar;

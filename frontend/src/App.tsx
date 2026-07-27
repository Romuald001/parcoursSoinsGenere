import { useAuth } from "./context/useAuth";
import LoginPage from "./pages/LoginPage";
import PatientOwnDashboardPage from "./pages/PatientOwnDashboardPage";
import AdminDashboardPage from "./pages/AdminDashboardPage";
import DoctorHome from "./pages/DoctorHome";

function App() {
  const { token, role } = useAuth();

  if (!token) return <LoginPage />;
  if (role === "admin") return <AdminDashboardPage />;
  if (role === "patient") return <PatientOwnDashboardPage />;
  return <DoctorHome />;
}

export default App;

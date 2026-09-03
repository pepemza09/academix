import { BrowserRouter as Router, Routes, Route } from "react-router";
import SignIn from "./pages/AuthPages/SignIn";
import SignUp from "./pages/AuthPages/SignUp";
import NotFound from "./pages/OtherPage/NotFound";
import UserProfiles from "./pages/UserProfiles";
import Calendar from "./pages/Calendar";
import AppLayout from "./layout/AppLayout";
import { ScrollToTop } from "./components/common/ScrollToTop";
import ProtectedRoute from "./components/common/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import Home from "./pages/Dashboard/AcademicsHome";
import Universidad from "./pages/Institucional/Universidad";
import UnidadAcademica from "./pages/Institucional/UnidadAcademica";
import Sede from "./pages/Institucional/Sede";
import Carreras from "./pages/Academica/Carreras";
import Planes from "./pages/Academica/Planes";
import Areas from "./pages/Academica/Areas";

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <ScrollToTop />
        <Routes>
          {/* Dashboard Layout */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route index path="/" element={<Home />} />

            {/* Institucional */}
            <Route path="/universidad" element={<Universidad />} />
            <Route path="/unidad-academica" element={<UnidadAcademica />} />
            <Route path="/sede" element={<Sede />} />

            {/* Académica */}
            <Route path="/academica/carreras" element={<Carreras />} />
            <Route path="/academica/planes" element={<Planes />} />
            <Route path="/academica/areas" element={<Areas />} />

            {/* Perfil y utilidades */}
            <Route path="/profile" element={<UserProfiles />} />
            <Route path="/calendar" element={<Calendar />} />
          </Route>

          {/* Auth Layout */}
          <Route path="/signin" element={<SignIn />} />
          <Route path="/signup" element={<SignUp />} />

          {/* Fallback Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

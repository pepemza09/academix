import { Suspense, lazy } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router";
import AppLayout from "./layout/AppLayout";
import { ScrollToTop } from "./components/common/ScrollToTop";
import ProtectedRoute from "./components/common/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";

const SignIn = lazy(() => import("./pages/AuthPages/SignIn"));
const SignUp = lazy(() => import("./pages/AuthPages/SignUp"));
const NotFound = lazy(() => import("./pages/OtherPage/NotFound"));
const UserProfiles = lazy(() => import("./pages/UserProfiles"));
const Calendar = lazy(() => import("./pages/Calendar"));
const Home = lazy(() => import("./pages/Dashboard/AcademicsHome"));
const Universidad = lazy(() => import("./pages/Institucional/Universidad"));
const UnidadAcademica = lazy(
  () => import("./pages/Institucional/UnidadAcademica"),
);
const Sede = lazy(() => import("./pages/Institucional/Sede"));
const Carreras = lazy(() => import("./pages/Academica/Carreras"));
const Planes = lazy(() => import("./pages/Academica/Planes"));
const Areas = lazy(() => import("./pages/Academica/Areas"));
const Materias = lazy(() => import("./pages/Academica/Materias"));

const fallback = (
  <div className="flex min-h-screen items-center justify-center text-sm text-gray-500 dark:text-gray-400">
    Cargando…
  </div>
);

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <ScrollToTop />
        <Suspense fallback={fallback}>
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
              <Route
                path="/unidad-academica"
                element={<UnidadAcademica />}
              />
              <Route path="/sede" element={<Sede />} />

              {/* Académica */}
              <Route path="/academica/carreras" element={<Carreras />} />
              <Route path="/academica/planes" element={<Planes />} />
              <Route path="/academica/areas" element={<Areas />} />
              <Route path="/academica/materias" element={<Materias />} />

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
        </Suspense>
      </Router>
    </AuthProvider>
  );
}

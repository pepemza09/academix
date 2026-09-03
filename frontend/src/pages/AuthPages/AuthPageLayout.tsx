import React, { useEffect } from "react";
import GridShape from "../../components/common/GridShape";
import { Link } from "react-router";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("dark");
    return () => {
      if (localStorage.getItem("theme") === "dark") {
        root.classList.add("dark");
      } else {
        root.classList.remove("dark");
      }
    };
  }, []);

  return (
    <div className="relative p-6 bg-white z-1 sm:p-0">
      <div className="relative flex flex-col justify-center w-full min-h-screen lg:flex-row sm:p-0">
        {children}
        <div className="flex-col items-center justify-center hidden w-full min-h-screen lg:w-1/2 bg-brand-950 lg:flex">
          <div className="relative flex items-center justify-center z-1">
            {/* <!-- ===== Common Grid Shape Start ===== --> */}
            <GridShape />
            <div className="flex flex-col items-center max-w-xs">
              <Link to="/" className="block mb-4">
                <img
                  width={166}
                  height={42}
                  src="/images/logo/academix-auth-logo.svg"
                  alt="Academix"
                />
              </Link>
              <p className="text-center text-gray-400">
                Plataforma de gestión académica universitaria
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";

import { useTheme } from "../../context/ThemeContext";

const zoomOptions = [100, 90, 80] as const;

export const ZoomSelectorButton: React.FC = () => {
  const { zoom, setZoom } = useTheme();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        aria-label="Seleccionar zoom de pantalla"
        aria-expanded={isOpen}
        className="flex items-center justify-center h-11 min-w-16 rounded-full border border-gray-200 bg-white px-3 text-xs font-semibold text-gray-700 transition-colors hover:bg-gray-100 hover:text-gray-900 dark:border-gray-800 dark:bg-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
      >
        {zoom}%
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full z-50 mt-2 min-w-28 rounded-xl border border-gray-200 bg-white p-1.5 shadow-theme-lg dark:border-gray-800 dark:bg-gray-900">
          {zoomOptions.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => {
                setZoom(option);
                setIsOpen(false);
              }}
              className={`flex w-full items-center justify-center rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                zoom === option
                  ? "bg-brand-50 text-brand-500 dark:bg-brand-500/15 dark:text-brand-400"
                  : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/5"
              }`}
            >
              {option}%
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

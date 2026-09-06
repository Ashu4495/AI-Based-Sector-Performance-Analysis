import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="inline-flex items-center gap-2 px-2.5 py-1 text-xs font-mono rounded border border-subtle bg-surface text-primary hover:bg-surface-hover transition-colors cursor-pointer"
      title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} theme`}
      aria-label="Toggle Theme"
      id="theme-toggle-btn"
    >
      {theme === 'dark' ? (
        <>
          <Sun className="w-3.5 h-3.5 text-brand" />
          <span>Light</span>
        </>
      ) : (
        <>
          <Moon className="w-3.5 h-3.5 text-brand" />
          <span>Dark</span>
        </>
      )}
    </button>
  );
}

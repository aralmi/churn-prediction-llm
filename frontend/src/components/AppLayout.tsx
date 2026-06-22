import { NavLink } from "react-router-dom";
import type { PropsWithChildren } from "react";
import { useEffect, useState } from "react";

const navItems = [
  { to: "/", label: "Главная" },
  { to: "/customers", label: "Клиенты" },
  { to: "/predict", label: "Прогноз" },
  { to: "/analytics", label: "Аналитика" },
];

export function AppLayout({ children }: PropsWithChildren) {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("theme");
    const nextTheme = savedTheme === "dark" ? "dark" : "light";
    setTheme(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
  }, []);

  function toggleTheme() {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    document.documentElement.dataset.theme = nextTheme;
    window.localStorage.setItem("theme", nextTheme);
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div>
          <h1>Прогнозирование оттока клиентов</h1>
        </div>
        <nav className="site-nav" aria-label="Основная навигация">
          <button
            aria-label={theme === "light" ? "Включить темную тему" : "Включить светлую тему"}
            className="theme-toggle"
            onClick={toggleTheme}
            type="button"
          >
            {theme === "light" ? "☾" : "☀"}
          </button>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
              to={item.to}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="page-content">{children}</main>
    </div>
  );
}

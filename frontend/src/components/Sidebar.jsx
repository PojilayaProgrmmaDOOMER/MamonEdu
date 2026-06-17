import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { getMyProfile } from "../api/userApi";

const icons = {
  home: "M3 11.5L12 4l9 7.5V21a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.5z",
  graph: "M6 6h.01 M18 6h.01 M12 18h.01 M6 6l6 12 M18 6l-6 12 M6 6h12",
  builder: "M4 4h16v4H4z M4 10h10v10H4z M16 10h4v4h-4z M16 16h4v4h-4z",
  results: "M4 19V5 M4 19h16 M8 15l3-4 3 2 4-7",
  settings: "M12 8a4 4 0 1 1 0 8a4 4 0 0 1 0-8z M12 2v3 M12 19v3 M4.9 4.9l2.1 2.1 M17 17l2.1 2.1 M2 12h3 M19 12h3",
};

function Icon({ name }) {
  return (
    <svg className="sidebar-icon" viewBox="0 0 24 24" fill="none">
      <path
        d={icons[name]}
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function roleLabel(role) {
  if (role === "teacher") return "Преподаватель";
  if (role === "student") return "Студент";
  if (role === "admin") return "Администратор";
  return role || "Пользователь";
}

function Sidebar() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    async function loadProfile() {
      const data = await getMyProfile();
      setProfile(data);
    }

    loadProfile();
  }, []);

  const menu = [
    { path: "/", icon: "home", title: "Главная" },
    { path: "/knowledge-graph", icon: "graph", title: "Граф знаний" },
    { path: "/results", icon: "results", title: "Мои результаты" },
    { path: "/settings", icon: "settings", title: "Настройки" },
  ];

  const canUseBuilder =
    profile?.role === "teacher" || profile?.role === "admin";

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/login");
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <img
          src="/mamont-logo.png"
          alt="MamontEdu"
          className="sidebar-logo-image"
        />

        <h2>
          Mamont<span>Edu</span>
        </h2>
      </div>

      <nav className="nav">
        {menu.map((item) => (
          <NavLink key={item.path} to={item.path} className="sidebar-link">
            <Icon name={item.icon} />
            <span>{item.title}</span>
          </NavLink>
        ))}

        {canUseBuilder && (
          <button
            type="button"
            className="sidebar-link sidebar-button-link"
            onClick={() => window.dispatchEvent(new Event("openCourseBuilder"))}
          >
            <Icon name="builder" />
            <span>Конструктор курсов</span>
          </button>
        )}
      </nav>

      <img src="/mammoth-watermark.png" alt="" className="sidebar-mammoth-bg" />

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="avatar">
            {profile?.avatar_url ? (
              <img
                src={
                  profile.avatar_url.startsWith("/static")
                    ? `http://127.0.0.1:8000${profile.avatar_url}`
                    : profile.avatar_url
                }
                alt=""
              />
            ) : (
              profile?.username?.[0]?.toUpperCase() || "U"
            )}
          </div>

          <div>
            <strong>{profile?.username || "Пользователь"}</strong>
            <span>{roleLabel(profile?.role)}</span>
          </div>
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          ↩ Выйти
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
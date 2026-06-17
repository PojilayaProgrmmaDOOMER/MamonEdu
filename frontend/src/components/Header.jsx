import { useLocation } from "react-router-dom";
import ActiveCourseSelector from "./ActiveCourseSelector";

function Header() {
  const location = useLocation();

  const pageInfo = {
    "/": {
      title: "Главная",
      subtitle: "Обзор обучения и активности",
    },

    "/knowledge-graph": {
      title: "Граф знаний",
      subtitle: "Онтология предметной области",
    },

    "/results": {
      title: "Мои результаты",
      subtitle: "Статистика обучения",
    },

    "/settings": {
      title: "Настройки",
      subtitle: "Профиль пользователя",
    },

    "/courses": {
      title: "Курс",
      subtitle: "Прохождение учебного материала",
    },
  };

  let current = {
    title: "MamontEdu",
    subtitle: "Интеллектуальная образовательная система",
  };

  Object.entries(pageInfo).forEach(([path, info]) => {
    if (location.pathname.startsWith(path) && path !== "/") {
      current = info;
    }
  });

  if (location.pathname === "/") {
    current = pageInfo["/"];
  }

  return (
    <header className="header">
      <div>
        <h1>{current.title}</h1>
        <p>{current.subtitle}</p>
      </div>

      <div className="header-actions">
        <ActiveCourseSelector />
      </div>
    </header>
  );
}

export default Header;
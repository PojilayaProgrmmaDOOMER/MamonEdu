import { Link } from "react-router-dom";

function HomePage() {
  return (
    <main className="page">
      <section className="hero">
        <h1>AI EduSeg</h1>
        <p>
          Электронное пособие по методам сегментации изображений
          с адаптивным тестированием, онтологией и практическими заданиями.
        </p>

        <div className="actions">
          <Link to="/topics">Перейти к темам</Link>
          <Link to="/login">Войти</Link>
          <Link to="/register">Регистрация</Link>
        </div>
      </section>
    </main>
  );
}

export default HomePage;
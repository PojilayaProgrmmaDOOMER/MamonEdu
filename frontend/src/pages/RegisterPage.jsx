import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";

function RegisterPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "student",
  });

  const [error, setError] = useState("");

  function handleChange(event) {
    setForm({
      ...form,
      [event.target.name]: event.target.value,
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    try {
      await api.post("/register", form);
      navigate("/login");
    } catch {
      setError("Не удалось зарегистрироваться. Проверьте данные.");
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-hero">
        <div className="auth-brand">
          <img src="/mamont-logo.png" alt="MamontEdu" />
          <h1>
            Mamont<span>Edu</span>
          </h1>
        </div>

        <h2>Создайте аккаунт</h2>
        <p>
          Получите доступ к курсам, графу знаний, адаптивным тестам и
          персональным рекомендациям.
        </p>

        <div className="auth-features">
          <span>Курсы</span>
          <span>Тесты</span>
          <span>Рекомендации</span>
        </div>
      </section>

      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Регистрация</h2>
        <p className="auth-subtitle">Заполните данные нового пользователя.</p>

        {error && <p className="auth-error">{error}</p>}

        <label>
          Имя пользователя
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Email
          <input
            name="email"
            type="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Пароль
          <input
            name="password"
            type="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Роль
          <select name="role" value={form.role} onChange={handleChange}>
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
          </select>
        </label>

        <button type="submit">Зарегистрироваться</button>

        <p className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </form>
    </main>
  );
}

export default RegisterPage;
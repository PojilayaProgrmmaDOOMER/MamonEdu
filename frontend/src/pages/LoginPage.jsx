import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api/client";

function LoginPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: "",
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
      const response = await api.post("/login", form);
      localStorage.setItem("access_token", response.data.access_token);
      navigate("/");
    } catch {
      setError("Неверный email или пароль");
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

        <h2>Интеллектуальная образовательная система</h2>
        <p>
          Изучайте сегментацию изображений, проходите адаптивные тесты и
          получайте рекомендации на основе онтологии знаний.
        </p>

        <div className="auth-features">
          <span>Онтология</span>
          <span>Адаптивное обучение</span>
          <span>Автопоиск материалов</span>
        </div>
      </section>

      <form className="auth-card" onSubmit={handleSubmit}>
        <h2>Вход</h2>
        <p className="auth-subtitle">Войдите в аккаунт, чтобы продолжить.</p>

        {error && <p className="auth-error">{error}</p>}

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

        <button type="submit">Войти</button>

        <p className="auth-switch">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </form>
    </main>
  );
}

export default LoginPage;
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getMyProgress,
  getMyRecommendations,
  getMyProfile,
} from "../api/userApi";
import { getCourses } from "../api/ontologyApi";

function DashboardPage() {
  const [profile, setProfile] = useState(null);
  const [progress, setProgress] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [progressData, recommendationsData, courseData, profileData] =
          await Promise.all([
            getMyProgress(),
            getMyRecommendations(),
            getCourses(),
            getMyProfile(),
          ]);

        setProgress(progressData);
        setRecommendations(recommendationsData);
        setCourses(courseData);
        setProfile(profileData);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return <p>Загрузка...</p>;
  }

  const user = profile;
  const summary = progress?.summary;

  function getCourseProgressPercent(courseId) {
    const items =
      progress?.module_progress?.filter(
        (item) => String(item.course_id) === String(courseId)
      ) || [];

    if (items.length === 0) return 0;

    const completed = items.filter(
      (item) => item.status === "completed" || item.is_completed
    ).length;

    return Math.round((completed / items.length) * 100);
  }

  return (
    <div className="dashboard">
      {/* Новый верхний блок */}
      <section className="dashboard-hero">
        <div className="dashboard-profile">
          <div className="dashboard-avatar">
            {user?.avatar_url ? (
              <img
                src={
                  user.avatar_url.startsWith("/static")
                    ? `http://127.0.0.1:8000${user.avatar_url}`
                    : user.avatar_url
                }
                alt=""
              />
            ) : (
              <span>{user?.username?.[0]?.toUpperCase() || "U"}</span>
            )}
          </div>

          <div>
            <h2>Добро пожаловать, {user?.username}!</h2>
            <p className="dashboard-role">{user?.role}</p>
            <p className="dashboard-bio">
              {user?.bio || "Описание профиля пока не заполнено."}
            </p>
          </div>
        </div>

        <div className="dashboard-hero-actions">
          <div className="dashboard-mini-stat">
            <strong>{courses.length}</strong>
            <span>курсов доступно</span>
          </div>

          <div className="dashboard-mini-stat">
            <strong>{summary?.completed_test_attempts_count || 0}</strong>
            <span>тестов пройдено</span>
          </div>

          <div className="dashboard-mini-stat">
            <strong>{summary?.average_practical_score || 0}</strong>
            <span>средний балл</span>
          </div>

          {courses.length > 0 && (
            <Link
              to={`/courses/${courses[0].id}/learn`}
              className="course-open-btn"
            >
              Продолжить обучение
            </Link>
          )}
        </div>
      </section>

      {/* Мои курсы */}
      <section className="card my-courses-card">
        <h3>Мои курсы</h3>

        {courses.length > 0 ? (
          <div className="dashboard-courses-list">
            {courses.map((course) => {
              const percent = getCourseProgressPercent(course.id);

              return (
                <div className="dashboard-course-item" key={course.id}>
                  <div className="dashboard-course-cover">
                    {course.cover_url ? (
                      <img
                        src={
                          course.cover_url.startsWith("/static")
                            ? `http://127.0.0.1:8000${course.cover_url}`
                            : course.cover_url
                        }
                        alt=""
                      />
                    ) : (
                      <span>{course.title?.[0]?.toUpperCase() || "C"}</span>
                    )}
                  </div>

                  <div className="dashboard-course-main">
                    <h4>{course.title}</h4>
                    <p>{course.description || "Описание не указано."}</p>

                    <div className="course-progress-wrap">
                      <div className="course-progress-top">
                        <span>Прогресс курса</span>
                        <b>{percent}%</b>
                      </div>

                      <div className="course-progress-bar">
                        <div
                          className="course-progress-fill"
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <Link
                    to={`/courses/${course.id}/learn`}
                    className="course-open-btn"
                  >
                    Открыть курс
                  </Link>
                </div>
              );
            })}
          </div>
        ) : (
          <p>У вас пока нет доступных курсов.</p>
        )}
      </section>

      <section className="grid">
        {/* Блок активности вместо практических заданий */}
        <div className="card">
          <h3>Активность обучения</h3>

          <div className="activity-grid">
            <div className="activity-item">
              <strong>{summary?.completed_test_attempts_count || 0}</strong>
              <span>завершённых тестов</span>
            </div>

            <div className="activity-item">
              <strong>{summary?.practical_submissions_count || 0}</strong>
              <span>практических попыток</span>
            </div>

            <div className="activity-item">
              <strong>{summary?.average_practical_score || 0}</strong>
              <span>средний балл практики</span>
            </div>
          </div>
        </div>

        {/* Рекомендации */}
        <div className="card">
          <h3>Рекомендации</h3>

          {recommendations?.materials?.length > 0 ? (
            recommendations.materials.map((material) => (
              <div className="list-item" key={material.material_id}>
                {material.title}
                <br />
                <small>{material.reason}</small>
              </div>
            ))
          ) : (
            <p>Пока нет рекомендаций.</p>
          )}
        </div>
      </section>
    </div>
  );
}

export default DashboardPage;
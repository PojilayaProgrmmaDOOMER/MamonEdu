import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyProgress, getMyRecommendations } from "../api/userApi";
import { getCourses, getCourseModuleProgress, downloadCourseCertificate } from "../api/ontologyApi";

function ResultsPage() {
  const [progress, setProgress] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [moduleProgress, setModuleProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadData() {
    try {
      const [progressData, recommendationsData, coursesData] =
        await Promise.all([
          getMyProgress(),
          getMyRecommendations(),
          getCourses(),
        ]);

      setProgress(progressData);
      setRecommendations(recommendationsData);
      setCourses(coursesData);

      if (coursesData.length > 0) {
        setSelectedCourseId(String(coursesData[0].id));
        const modules = progressData.module_progress.filter(
          (item) => String(item.course_id) === String(coursesData[0].id)
        );
        setModuleProgress(modules);
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectCourse(courseId) {
    setSelectedCourseId(courseId);

    const modules = progress.module_progress.filter(
      (item) => String(item.course_id) === String(courseId)
    );
    setModuleProgress(modules);
  }

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <p>Загрузка результатов...</p>;

  const weakTopics = progress?.weak_topics || [];
  const recentPracticals = progress?.recent_practical_submissions || [];
  const materials =
    progress?.recommended_materials ||
    recommendations?.materials ||
    [];

  const completedCourses = courses.filter((course) => {
    const courseModules = progress?.module_progress?.filter(
      (item) => String(item.course_id) === String(course.id)
    ) || [];

    if (courseModules.length === 0) return false;

    return courseModules.every(
      (item) => item.is_completed || item.status === "completed"
    );
  });

  console.log("MODULE PROGRESS:", moduleProgress);

  return (
    <div className="results-page">
      <section className="results-card results-main-head">
        <div>
          <h2>Анализ обучения</h2>
          <p>
            Здесь собраны слабые темы, рекомендации и прогресс по модулям курса.
          </p>
        </div>

        {courses.length > 0 && (
          <select
            value={selectedCourseId}
            onChange={(e) => handleSelectCourse(e.target.value)}
          >
            {courses.map((course) => (
              <option key={course.id} value={course.id}>
                {course.title}
              </option>
            ))}
          </select>
        )}
      </section>

      <section className="results-card certificates-card">
        <div className="results-section-head">
          <div>
            <h3>Мои сертификаты</h3>
            <p>Сертификаты появляются после успешного завершения курса.</p>
          </div>
        </div>

        {completedCourses.length > 0 ? (
          <div className="certificates-list">
            {completedCourses.map((course) => (
              <div className="certificate-item" key={course.id}>
                <div>
                  <strong>{course.title}</strong>
                  <span>Курс успешно завершён</span>
                </div>

                <button
                  type="button"
                  onClick={() => downloadCourseCertificate(course.id)}
                >
                  Скачать сертификат
                </button>
              </div>
            ))}
          </div>
        ) : (
          <p>Завершённых курсов пока нет.</p>
        )}
      </section>

      <div className="results-analytics-grid">
        <section className="results-card">
          <h3>Слабые концепты</h3>

          {weakTopics.length > 0 ? (
            <div className="weak-concepts-list">
              {weakTopics.map((item, index) => (
                <div className="weak-concept-item" key={index}>
                  <strong>{item.concept_name || item.name || item.title}</strong>
                  <span>
                    {item.reason || item.error_count
                      ? `${item.error_count || 1} ошибок`
                      : "требует повторения"}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p>Слабые концепты пока не выявлены.</p>
          )}
        </section>

        <section className="results-card">
          <h3>Рекомендуется повторить</h3>

          {materials.length > 0 ? (
            <div className="recommendation-list">
              {materials.slice(0, 6).map((material) => (
                <div className="recommendation-item" key={material.id || material.material_id}>
                  <strong>{material.title}</strong>
                  <span>{material.reason || "Рекомендованный материал"}</span>

                  {material.source_url && (
                    <a href={material.source_url} target="_blank" rel="noreferrer">
                      Открыть материал
                    </a>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p>Рекомендаций пока нет.</p>
          )}
        </section>
      </div>

      <section className="results-card">
        <div className="results-section-head">
          <div>
            <h3>Карта модулей</h3>
            <p>Состояние прохождения модулей выбранного курса.</p>
          </div>

          {selectedCourseId && (
            <Link
              to={`/courses/${selectedCourseId}/learn`}
              className="course-open-btn"
            >
              Открыть курс
            </Link>
          )}
        </div>

        {moduleProgress.length > 0 ? (
          <div className="module-map-list">
            {moduleProgress.map((module) => (
              <div className="module-map-item" key={module.module_id}>
                <div className="module-map-status">
                  {module.status === "completed" || module.is_completed
                    ? "✓"
                    : module.status === "locked"
                    ? "🔒"
                    : "⏳"}
                </div>

                <div>
                  <strong>
                    {module.module_title || `Модуль ${module.module_id}`}
                  </strong>
                  <span>
                    {module.status === "completed" || module.is_completed
                      ? "Пройден"
                      : module.status === "locked"
                      ? "Закрыт"
                      : "В процессе"}
                  </span>
                </div>

                <b>{module.score || 0}%</b>
              </div>
            ))}
          </div>
        ) : (
          <p>По этому курсу пока нет данных о прохождении.</p>
        )}
      </section>

      <section className="results-card">
        <h3>История активности</h3>

        {recentPracticals.length > 0 ? (
          <div className="attempt-history-list">
            {recentPracticals.map((item) => (
              <div className="attempt-history-item" key={item.id}>
                <strong>Практика #{item.practical_task_id}</strong>
                <span>Статус: {item.status}</span>
                <b>{item.score} баллов</b>
              </div>
            ))}
          </div>
        ) : (
          <p>История попыток пока пуста.</p>
        )}
      </section>
    </div>
  );
}

export default ResultsPage;
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import CourseEditorModal from "./CourseEditorModal";
import {
  getCourses,
  createCourse,
  deleteCourse,
  updateCourse,
  getOntologyGraph,
  getCourseStudents,
  addStudentToCourseByUsername,
  removeStudentFromCourse,
} from "../api/ontologyApi";

function CourseBuilderModal({ open, onClose }) {
  const [courses, setCourses] = useState([]);
  const [rootOptions, setRootOptions] = useState([]);

  const [form, setForm] = useState({
    title: "",
    description: "",
    root_entity_name: "",
    root_entity_type: "Concept",
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);

  // Состояния для управления студентами
  const [selectedStudentCourse, setSelectedStudentCourse] = useState(null);
  const [courseStudents, setCourseStudents] = useState([]);
  const [studentUsername, setStudentUsername] = useState("");

  // Состояния для редактора курса
  const [editorOpen, setEditorOpen] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);

  async function loadData() {
    setLoading(true);
    try {
      const [courseData, graphData] = await Promise.all([
        getCourses(),
        getOntologyGraph(),
      ]);
      setCourses(courseData);
      const freeEntities = graphData.nodes.filter(
        (node) => node.course_id == null
      );
      setRootOptions(freeEntities);
    } finally {
      setLoading(false);
    }
  }

  async function loadStudents(courseId) {
    const data = await getCourseStudents(courseId);
    setCourseStudents(data);
  }

  useEffect(() => {
    if (open) {
      loadData();
      setEditingCourse(null);
      setSelectedStudentCourse(null);
      setCourseStudents([]);
      setStudentUsername("");
      setForm({
        title: "",
        description: "",
        root_entity_name: "",
        root_entity_type: "Concept",
      });
    }
  }, [open]);

  function resetForm() {
    setForm({
      title: "",
      description: "",
      root_entity_name: "",
      root_entity_type: "Concept",
    });
  }

  function closeModal() {
    resetForm();
    onClose();
  }

  async function handleCreateCourse(event) {
    event.preventDefault();

    if (!form.title.trim() || !form.root_entity_name.trim()) {
      return;
    }

    setSaving(true);
    try {
      if (editingCourse) {
        await updateCourse(editingCourse.id, {
          title: form.title,
          description: form.description,
        });
      } else {
        // Создаем сущность онтологии и курс
        await createCourse({
          title: form.title,
          description: form.description,
          root_entity_name: form.root_entity_name,
          root_entity_type: form.root_entity_type,
        });
      }

      setEditingCourse(null);
      setForm({
        title: "",
        description: "",
        root_entity_name: "",
        root_entity_type: "Concept",
      });

      await loadData();
      window.dispatchEvent(new Event("coursesChanged"));
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteCourse(courseId) {
    const confirmed = window.confirm(
      "Удалить курс? Вместе с ним удалится онтология курса."
    );
    if (!confirmed) return;

    await deleteCourse(courseId);
    await loadData();
    window.dispatchEvent(new Event("coursesChanged"));
  }

  if (!open) return null;

  return (
    <div className="relation-modal-overlay">
      <div className="course-builder-modal">
        <div className="course-modal-head">
          <div>
            <h3>Конструктор курсов</h3>
            <p>
              Создайте новый курс и выберите корневой концепт из уже
              существующих сущностей.
            </p>
          </div>
          <button type="button" onClick={closeModal}>
            ×
          </button>
        </div>

        {loading ? (
          <p>Загрузка данных...</p>
        ) : (
          <div className="course-builder-modal-grid">
            <form className="course-builder-form" onSubmit={handleCreateCourse}>
              <h4>{editingCourse ? "Редактирование курса" : "Новый курс"}</h4>

              <label>
                Название курса
                <input
                  value={form.title}
                  onChange={(event) =>
                    setForm({ ...form, title: event.target.value })
                  }
                  placeholder="Например: Сегментация изображений"
                  required
                />
              </label>

              <label>
                Описание курса
                <textarea
                  rows="4"
                  value={form.description}
                  onChange={(event) =>
                    setForm({ ...form, description: event.target.value })
                  }
                  placeholder="Краткое описание курса..."
                />
              </label>

              <hr />

              <h4>Корневой концепт онтологии</h4>

              <label>
                Корневая сущность
                <input
                  value={form.root_entity_name}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      root_entity_name: e.target.value,
                    })
                  }
                  placeholder="Image Segmentation"
                />
              </label>

              <label>
                Тип сущности
                <select
                  value={form.root_entity_type}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      root_entity_type: e.target.value,
                    })
                  }
                >
                  <option value="Concept">Concept</option>
                  <option value="Method">Method</option>
                  <option value="Task">Task</option>
                  <option value="Algorithm">Algorithm</option>
                </select>
              </label>

              <p className="help-text">
                Будет создана новая сущность онтологии как корневой концепт курса.
              </p>

              <button type="submit" disabled={saving}>
                {saving
                  ? "Сохранение..."
                  : editingCourse
                  ? "Сохранить изменения"
                  : "Создать курс"}
              </button>

              {editingCourse && (
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => {
                    setEditingCourse(null);
                    setForm({
                      title: "",
                      description: "",
                      root_entity_name: "",
                      root_entity_type: "Concept",
                    });
                  }}
                >
                  Отмена
                </button>
              )}
            </form>

            <div className="course-builder-list">
              <h4>Ваши курсы</h4>

              {courses.length > 0 ? (
                courses.map((course) => (
                  <div className="course-mini-card" key={course.id}>
                    <div className="course-mini-card-head">
                      <strong>{course.title}</strong>
                      <span>#{course.id}</span>
                    </div>

                    <p>{course.description || "Описание не указано."}</p>

                    <small>
                      Корневой концепт:{" "}
                      <b>
                        {course.root_entity_name
                          ? `${course.root_entity_name} (${course.root_entity_type})`
                          : `ID ${course.root_entity_id}`}
                      </b>
                    </small>

                    <div className="course-actions">
                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => {
                          setSelectedCourse(course);
                          setEditorOpen(true);
                        }}
                      >
                        Редактировать
                      </button>

                      <button
                        type="button"
                        className="students-btn"
                        onClick={async () => {
                          setSelectedStudentCourse(course);
                          await loadStudents(course.id);
                        }}
                      >
                        Студенты
                      </button>

                      <Link
                        to={`/courses/${course.id}/learn`}
                        className="edit-btn"
                      >
                        Смотреть курс
                      </Link>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeleteCourse(course.id)}
                      >
                        Удалить курс
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Курсов пока нет</h4>
                  <p>
                    Создайте первый курс. Для него автоматически будет
                    использована выбранная корневая сущность.
                  </p>
                </div>
              )}
            </div>

            {/* Панель управления студентами выбранного курса */}
            {selectedStudentCourse && (
              <div className="course-students-panel">
                <h4>Студенты курса "{selectedStudentCourse.title}"</h4>

                <div className="student-add-row">
                  <input
                    value={studentUsername}
                    onChange={(e) => setStudentUsername(e.target.value)}
                    placeholder="Логин студента"
                  />
                  <button
                    type="button"
                    onClick={async () => {
                      if (!studentUsername.trim()) return;
                      await addStudentToCourseByUsername(
                        selectedStudentCourse.id,
                        studentUsername
                      );
                      setStudentUsername("");
                      await loadStudents(selectedStudentCourse.id);
                    }}
                  >
                    Пригласить
                  </button>
                </div>

                {courseStudents.length === 0 ? (
                  <p>Нет записанных студентов.</p>
                ) : (
                  courseStudents.map((student) => (
                    <div key={student.id} className="student-row">
                      <span>
                        <strong>
                          {student.username || `Студент #${student.student_id}`}
                        </strong>
                        {student.email && <small>{student.email}</small>}
                      </span>
                      <button
                        type="button"
                        className="danger-small-btn"
                        onClick={async () => {
                          await removeStudentFromCourse(
                            selectedStudentCourse.id,
                            student.student_id
                          );
                          await loadStudents(selectedStudentCourse.id);
                        }}
                      >
                        Удалить
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        {/* Модальное окно редактора курса */}
        <CourseEditorModal
          open={editorOpen}
          course={selectedCourse}
          onClose={() => {
            setEditorOpen(false);
            setSelectedCourse(null);
          }}
          onCourseUpdated={loadData}
          onCourseChanged={(updatedCourse) => {
            setSelectedCourse(updatedCourse);
          }}
        />
      </div>
    </div>
  );
}

export default CourseBuilderModal;
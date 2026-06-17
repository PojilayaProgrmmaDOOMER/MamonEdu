import { useEffect, useMemo, useState } from "react";

import {
  getCourses,
  createCourse,
  deleteCourse,
  getOntologyGraph,
} from "../api/ontologyApi";

export default function CoursesBuilderPage() {
  const [courses, setCourses] = useState([]);
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const [form, setForm] = useState({
    title: "",
    description: "",
    root_entity_id: "",
  });

  async function loadCourses() {
    const data = await getCourses();
    setCourses(data);
  }

  async function loadGraph() {
    const data = await getOntologyGraph();
    setGraph(data);
  }

  useEffect(() => {
    loadCourses();
    loadGraph();
  }, []);

  const rootOptions = useMemo(() => {
    return graph.nodes.filter((node) => node.type !== "TypeGroup");
  }, [graph.nodes]);

  function openCreateModal() {
    setForm({
      title: "",
      description: "",
      root_entity_id: rootOptions[0]?.id || "",
    });

    setShowModal(true);
  }

  function closeCreateModal() {
    setShowModal(false);

    setForm({
      title: "",
      description: "",
      root_entity_id: "",
    });
  }

  async function handleSubmit(event) {
    event.preventDefault();

    if (!form.title.trim() || !form.root_entity_id) return;

    setSaving(true);

    try {
      await createCourse({
        title: form.title,
        description: form.description,
        root_entity_id: Number(form.root_entity_id),
      });

      await loadCourses();

      closeCreateModal();
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteCourse(courseId) {
    const confirmed = window.confirm("Удалить курс?");

    if (!confirmed) return;

    await deleteCourse(courseId);
    await loadCourses();
  }

  function getRootName(rootId) {
    const node = graph.nodes.find((item) => String(item.id) === String(rootId));

    return node?.label || `ID ${rootId}`;
  }

  return (
    <div className="course-builder-page">
      <div className="course-builder-header">
        <div>
          <h2>Конструктор курсов</h2>
          <p>
            Создавайте учебные курсы на основе выбранного корневого концепта
            онтологии.
          </p>
        </div>

        <button type="button" onClick={openCreateModal}>
          + Создать курс
        </button>
      </div>

      <div className="course-builder-grid">
        {courses.length > 0 ? (
          courses.map((course) => (
            <div className="course-builder-card" key={course.id}>
              <div className="course-builder-card-top">
                <span>Курс</span>
                <b>#{course.id}</b>
              </div>

              <h3>{course.title}</h3>

              <p>{course.description || "Описание курса не указано."}</p>

              <div className="course-root-chip">
                Корневой концепт: <strong>{getRootName(course.root_entity_id)}</strong>
              </div>

              <div className="course-card-actions">
                <button type="button">Открыть курс</button>

                <button
                  type="button"
                  className="danger-small-btn"
                  onClick={() => handleDeleteCourse(course.id)}
                >
                  Удалить
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="empty-course-state">
            <h3>Курсов пока нет</h3>
            <p>
              Создайте первый курс, выбрав корневой концепт из графа знаний.
            </p>
          </div>
        )}
      </div>

      {showModal && (
        <div className="relation-modal-overlay">
          <form className="course-create-modal" onSubmit={handleSubmit}>
            <div className="course-modal-head">
              <div>
                <h3>Создать курс</h3>
                <p>Курс будет связан с выбранной онтологией.</p>
              </div>

              <button type="button" onClick={closeCreateModal}>
                ×
              </button>
            </div>

            <label>
              Название курса
              <input
                value={form.title}
                onChange={(event) =>
                  setForm({
                    ...form,
                    title: event.target.value,
                  })
                }
                placeholder="Например: Сегментация изображений"
                required
              />
            </label>

            <label>
              Описание
              <textarea
                rows="5"
                value={form.description}
                onChange={(event) =>
                  setForm({
                    ...form,
                    description: event.target.value,
                  })
                }
                placeholder="Краткое описание курса..."
              />
            </label>

            <label>
              Корневой концепт
              <select
                value={form.root_entity_id}
                onChange={(event) =>
                  setForm({
                    ...form,
                    root_entity_id: event.target.value,
                  })
                }
                required
              >
                {rootOptions.map((node) => (
                  <option value={node.id} key={node.id}>
                    {node.label} — {node.type}
                  </option>
                ))}
              </select>
            </label>

            <div className="modal-buttons">
              <button type="button" onClick={closeCreateModal}>
                Отмена
              </button>

              <button type="submit" disabled={saving}>
                {saving ? "Создание..." : "Создать курс"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
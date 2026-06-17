import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  getCourseModules,
  getModuleLectures,
  getLectureBlocks,
  generateModuleTest,
  getModuleTestAttempt,
  submitModuleTestAttempt,
  createAdaptiveRetry,
  getCourseModuleProgress,
  getQuestionOptions,
  getCourseMaterials,
  downloadCourseCertificate,
} from "../api/ontologyApi";

function CourseLearningPage() {
  const { courseId } = useParams();

  const [modules, setModules] = useState([]);
  const [progress, setProgress] = useState([]);
  const [courseMaterials, setCourseMaterials] = useState([]);

  const [selectedModule, setSelectedModule] = useState(null);
  const [lectures, setLectures] = useState([]);

  const [selectedLecture, setSelectedLecture] = useState(null);
  const [showMaterials, setShowMaterials] = useState(false);
  const [lectureBlocks, setLectureBlocks] = useState([]);

  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [practicalAnswers, setPracticalAnswers] = useState({});
  const [questionOptions, setQuestionOptions] = useState({});
  const [result, setResult] = useState(null);

  async function loadCourseData() {
    const [modulesData, progressData, materialsData] = await Promise.all([
      getCourseModules(courseId),
      getCourseModuleProgress(courseId),
      getCourseMaterials(courseId),
    ]);

    setModules(modulesData);
    setProgress(progressData);
    setCourseMaterials(materialsData);

    if (modulesData.length > 0) {
      setSelectedModule(modulesData[0]);
    }
  }

  async function loadModuleLectures(module) {
    setSelectedModule(module);
    setSelectedLecture(null);
    setLectureBlocks([]);
    setAttempt(null);
    setResult(null);
    setShowMaterials(false);

    const data = await getModuleLectures(courseId, module.id);
    setLectures(data);
  }

  async function openLecture(lecture) {
    setSelectedLecture(lecture);
    setAttempt(null);
    setResult(null);
    setShowMaterials(false);

    const blocks = await getLectureBlocks(lecture.id);
    setLectureBlocks(blocks);
  }

  async function loadOptionsForAttempt(attemptData) {
    const optionsMap = {};

    for (const question of attemptData.questions) {
      if (
        question.question_type === "single_choice" ||
        question.question_type === "multiple_choice"
      ) {
        const options = await getQuestionOptions(question.id);
        optionsMap[question.id] = options;
      }
    }

    setQuestionOptions(optionsMap);
  }

  async function startModuleTest() {
    if (!selectedModule) return;

    const data = await generateModuleTest(courseId, selectedModule.id);

    setAttempt(data);
    setSelectedLecture(null);
    setLectureBlocks([]);
    setResult(null);
    setAnswers({});
    setPracticalAnswers({});
    setQuestionOptions({});

    await loadOptionsForAttempt(data);
  }

  async function submitTest() {
    if (!attempt) return;

    const payload = {
      question_answers: attempt.questions.map((question) => ({
        question_id: question.id,
        selected_answer: answers[question.id] || "",
      })),
      practical_results: attempt.practical_tasks?.map((task) => ({
        task_id: task.id,
        submitted_code: practicalAnswers[task.id] || "",
        score: practicalAnswers[task.id]?.trim() ? 100 : 0,
      })) || [],
    };

    const data = await submitModuleTestAttempt(attempt.attempt_id, payload);
    setResult(data);
    setAttempt(null);

    const progressData = await getCourseModuleProgress(courseId);
    setProgress(progressData);
  }

  async function retryAdaptive() {
    if (!result?.attempt_id) return;

    const data = await createAdaptiveRetry(result.attempt_id);

    setAttempt(data);
    setResult(null);
    setAnswers({});
    setPracticalAnswers({});
    setQuestionOptions({});

    await loadOptionsForAttempt(data);
  }

  function getModuleStatus(moduleId) {
    const item = progress.find(
      (progressItem) => String(progressItem.module_id) === String(moduleId)
    );

    return item?.status || "available";
  }

  function isModuleLocked(module) {
    if (module.position === 1) return false;

    const previousModule = modules.find(
      (item) => item.position === module.position - 1
    );

    if (!previousModule) return false;

    const previousProgress = progress.find(
      (item) => String(item.module_id) === String(previousModule.id)
    );

    return !(
      previousProgress?.status === "completed" ||
      previousProgress?.is_completed
    );
  }

  function isSelectedModuleCompleted() {
    if (!selectedModule) return false;

    const item = progress.find(
      (progressItem) =>
        String(progressItem.module_id) === String(selectedModule.id)
    );

    return item?.status === "completed" || item?.is_completed;
  }

  function isCourseCompleted() {
    if (!modules.length || !progress.length) return false;

    return modules.every((module) => {
      const item = progress.find(
        (progressItem) => String(progressItem.module_id) === String(module.id)
      );

      return item?.is_completed || item?.status === "completed";
    });
  }

  function getLearningStats() {
    const completedModules = progress.filter(
      (item) => item.status === "completed" || item.is_completed
    ).length;

    return {
      totalModules: modules.length,
      completedModules,
      totalLectures: lectures.length,
      completedPercent:
        modules.length > 0 ? Math.round((completedModules / modules.length) * 100) : 0,
    };
  }

  const stats = getLearningStats();

  function toggleMultipleAnswer(questionId, optionId) {
    const current = answers[questionId]
      ? String(answers[questionId]).split(",").filter(Boolean)
      : [];

    const optionString = String(optionId);

    const updated = current.includes(optionString)
      ? current.filter((item) => item !== optionString)
      : [...current, optionString];

    setAnswers({
      ...answers,
      [questionId]: updated.join(","),
    });
  }

  useEffect(() => {
    loadCourseData();
  }, [courseId]);

  useEffect(() => {
    if (selectedModule) {
      loadModuleLectures(selectedModule);
    }
  }, [selectedModule?.id]);

  return (
    <div className="learning-page">
      <div className="learning-sidebar">
        <h2>Курс</h2>

        {modules.map((module) => (
          <button
            key={module.id}
            type="button"
            className={
              `${selectedModule?.id === module.id ? "learning-module active" : "learning-module"} ${
                isModuleLocked(module) ? "locked" : ""
              }`
            }
            onClick={() => {
              if (isModuleLocked(module)) return;
              loadModuleLectures(module);
            }}
          >
            <strong>
              {module.position}. {module.title}
            </strong>
            <span>
              {isModuleLocked(module)
                ? "Закрыт"
                : getModuleStatus(module.id) === "completed"
                ? "Пройден"
                : "Доступен"}
            </span>
          </button>
        ))}
      </div>

      <div className="learning-content">
        <div className="learning-stats">
          <div>
            <strong>{stats.completedModules}/{stats.totalModules}</strong>
            <span>модулей пройдено</span>
          </div>

          <div>
            <strong>{stats.totalLectures}</strong>
            <span>лекций в модуле</span>
          </div>

          <div>
            <strong>{stats.completedPercent}%</strong>
            <span>прогресс курса</span>
          </div>
        </div>

        {selectedModule && (
          <div className="learning-header">
            <div>
              <h1>{selectedModule.title}</h1>
              <p>{selectedModule.description}</p>
            </div>
          </div>
        )}

        {isCourseCompleted() && (
          <div className="certificate-banner">
            <div>
              <h3>Поздравляем! Курс завершён</h3>
              <p>Вы успешно прошли все модули курса и можете получить сертификат.</p>
            </div>

            <button
              type="button"
              onClick={() => downloadCourseCertificate(courseId)}
            >
              Скачать сертификат
            </button>
          </div>
        )}

        {!attempt && !selectedLecture && !showMaterials && (
          <div className="learning-section">
            <h3>Лекции модуля</h3>

            {lectures.length > 0 ? (
              lectures.map((lecture) => (
                <button
                  key={lecture.id}
                  type="button"
                  className="learning-lecture-card"
                  onClick={() => openLecture(lecture)}
                >
                  <strong>
                    {lecture.position}. {lecture.title}
                  </strong>
                  <span>
                    {lecture.is_published ? "Опубликована" : "Черновик"}
                  </span>
                </button>
              ))
            ) : (
              <p>В этом модуле пока нет лекций.</p>
            )}

            {courseMaterials.length > 0 && (
              <button
                type="button"
                className="learning-lecture-card materials-entry-card"
                onClick={() => {
                  setSelectedLecture(null);
                  setAttempt(null);
                  setResult(null);
                  setShowMaterials(true);
                }}
              >
                <strong>Дополнительные материалы курса</strong>
                <span>{courseMaterials.length} материалов</span>
              </button>
            )}

            <div className="module-test-start-card">
              <div>
                <h3>Итоговый тест модуля</h3>
                <p>
                  После изучения лекций пройдите тест, чтобы открыть следующий модуль.
                </p>
              </div>

              {isSelectedModuleCompleted() ? (
                <div className="module-completed-notice">
                  ✓ Модуль успешно пройден
                </div>
              ) : (
                <button type="button" onClick={startModuleTest}>
                  Пройти тест модуля
                </button>
              )}
            </div>
          </div>
        )}

        {selectedLecture && (
          <div className="learning-section">
            <button type="button" onClick={() => setSelectedLecture(null)}>
              ← Назад к лекциям
            </button>

            <h2>{selectedLecture.title}</h2>

            {lectureBlocks.length > 0 ? (
              lectureBlocks.map((block) => (
                <div className="lecture-view-block" key={block.id}>
                  {block.block_type === "text" ? (
                    <p>{block.content}</p>
                  ) : block.image_url ? (
                    <img
                      src={`http://127.0.0.1:8000${block.image_url}`}
                      alt=""
                    />
                  ) : null}
                </div>
              ))
            ) : (
              <p>{selectedLecture.content || "Содержимое лекции не указано."}</p>
            )}
          </div>
        )}

        {showMaterials && (
          <div className="learning-section">
            <button type="button" onClick={() => setShowMaterials(false)}>
              ← Назад к модулю
            </button>

            <div className="materials-page-head">
              <div>
                <h2>Дополнительные материалы курса</h2>
                <p>
                  Статьи и источники, найденные автоматически и привязанные к узлам онтологии.
                </p>
              </div>
            </div>

            <div className="student-materials-grid">
              {courseMaterials.map((material) => (
                <article className="student-material-card" key={material.id}>
                  <div className="student-material-card-head">
                    <span>{material.material_type || "article"}</span>
                    <strong>{material.title}</strong>
                  </div>

                  <p>
                    {material.content?.length > 280
                      ? `${material.content.slice(0, 280)}...`
                      : material.content || "Описание не указано."}
                  </p>

                  {material.concepts?.length > 0 && (
                    <div className="student-material-concepts">
                      {material.concepts.map((concept) => (
                        <span key={concept.id}>
                          {concept.name} · {concept.type}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="student-material-actions">
                    {material.source_url && (
                      <a href={material.source_url} target="_blank" rel="noreferrer">
                        Открыть источник
                      </a>
                    )}

                    {material.pdf_url && (
                      <a href={material.pdf_url} target="_blank" rel="noreferrer">
                        Скачать PDF
                      </a>
                    )}
                  </div>
                </article>
              ))}
            </div>
          </div>
        )}

        {attempt && (
          <div className="learning-section">
            <h2>Тест модуля</h2>

            {attempt.questions.map((question) => (
              <div className="test-question-card" key={question.id}>
                <div className="test-question-head">
                  <span>{question.difficulty}</span>
                  <span>{question.question_type}</span>
                </div>

                <h4>{question.question_text}</h4>

                {question.question_type === "text" && (
                  <input
                    value={answers[question.id] || ""}
                    onChange={(event) =>
                      setAnswers({
                        ...answers,
                        [question.id]: event.target.value,
                      })
                    }
                    placeholder="Введите ответ"
                  />
                )}

                {question.question_type === "single_choice" && (
                  <div className="test-options-list">
                    {(questionOptions[question.id] || []).map((option) => (
                      <label className="test-option" key={option.id}>
                        <input
                          type="radio"
                          name={`question-${question.id}`}
                          checked={String(answers[question.id] || "") === String(option.id)}
                          onChange={() =>
                            setAnswers({
                              ...answers,
                              [question.id]: String(option.id),
                            })
                          }
                        />
                        <span>{option.option_text}</span>
                      </label>
                    ))}
                  </div>
                )}

                {question.question_type === "multiple_choice" && (
                  <div className="test-options-list">
                    {(questionOptions[question.id] || []).map((option) => {
                      const selectedIds = String(answers[question.id] || "")
                        .split(",")
                        .filter(Boolean);

                      return (
                        <label className="test-option" key={option.id}>
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(String(option.id))}
                            onChange={() => toggleMultipleAnswer(question.id, option.id)}
                          />
                          <span>{option.option_text}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
              </div>
            ))}

            {attempt.practical_tasks?.length > 0 && (
              <div className="test-practical-section">
                <h3>Практические задания</h3>

                {attempt.practical_tasks.map((task) => (
                  <div className="test-question-card" key={task.id}>
                    <h4>{task.title}</h4>
                    <p>{task.description}</p>

                    {task.starter_code && (
                      <pre className="code-preview">{task.starter_code}</pre>
                    )}

                    <textarea
                      placeholder="Вставьте решение практического задания"
                      rows="8"
                      value={practicalAnswers[task.id] || ""}
                      onChange={(event) =>
                        setPracticalAnswers({
                          ...practicalAnswers,
                          [task.id]: event.target.value,
                        })
                      }
                    />
                  </div>
                ))}
              </div>
            )}

            <button type="button" onClick={submitTest}>
              Завершить тест
            </button>
          </div>
        )}

        {result && (
          <div className="learning-result">
            <h2>Результат</h2>

            <p>
              Итоговый балл: <b>{result.final_score}</b>
            </p>

            <p>
              Статус:{" "}
              <b>{result.is_passed ? "Модуль пройден" : "Модуль не пройден"}</b>
            </p>

            {!result.is_passed && (
              <>
                <h3>Слабые концепты</h3>

                {result.weak_concepts.map((concept) => (
                  <p key={concept.id}>
                    {concept.name} — {concept.type}
                  </p>
                ))}

                <h3>Рекомендованные материалы</h3>

                {result.recommended_materials?.length > 0 ? (
                  <div className="student-materials-grid">
                    {result.recommended_materials.map((material) => (
                      <article className="student-material-card" key={material.id}>
                        <div className="student-material-card-head">
                          <span>{material.resource_type || material.material_type || "материал"}</span>
                          <strong>{material.title}</strong>
                        </div>

                        {material.description && (
                          <p>
                            {material.description.length > 260
                              ? `${material.description.slice(0, 260)}...`
                              : material.description}
                          </p>
                        )}

                        {material.reason && (
                          <small>{material.reason}</small>
                        )}

                        <div className="student-material-actions">
                          {material.source_url && (
                            <a href={material.source_url} target="_blank" rel="noreferrer">
                              Открыть источник
                            </a>
                          )}

                          {material.pdf_url && (
                            <a href={material.pdf_url} target="_blank" rel="noreferrer">
                              Скачать PDF
                            </a>
                          )}
                        </div>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p>Для слабых концептов пока нет прикреплённых материалов.</p>
                )}

                <button type="button" onClick={retryAdaptive}>
                  Пройти адаптивную попытку
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CourseLearningPage;
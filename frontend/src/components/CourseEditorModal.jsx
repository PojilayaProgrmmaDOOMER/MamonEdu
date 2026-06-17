import { useEffect, useState } from "react";

import {
  getCourseModules,
  createCourseModule,
  updateCourseModule,
  deleteCourseModule,
  publishCourse,
  unpublishCourse,
  getModuleLectures,
  createModuleLecture,
  updateModuleLecture,
  deleteModuleLecture,
  uploadLectureImage,
  getLectureBlocks,
  createLectureBlock,
  updateLectureBlock,
  deleteLectureBlock,
  uploadLectureBlockImage,
  getCourseQuestionBank,
  createCourseQuestion,
  updateCourseQuestion,
  deleteCourseQuestion,
  getQuestionOptions,
  createQuestionOption,
  deleteQuestionOption,
  getQuestionConcepts,
  addQuestionConcept,
  deleteQuestionConcept,
  getOntologyGraph,
  getCoursePracticalBank,
  createCoursePractical,
  updateCoursePractical,
  deleteCoursePractical,
  getPracticalConcepts,
  addPracticalConcept,
  deletePracticalConcept,
  getModuleTestSettings,
  createModuleTestSettings,
  updateModuleTestSettings,
  getModuleTestConcepts,
  addModuleTestConcept,
  deleteModuleTestConcept,
  generateModuleTest,
  uploadCourseCover,
  getMaterialSearchProfiles,
  createMaterialSearchProfile,
  runMaterialSearchProfile,
  getMaterialCandidates,
  approveMaterialCandidate,
  rejectMaterialCandidate,
  deleteMaterialSearchProfile,
  clearMaterialCandidates,
  getCourseMaterials,
  deleteCourseMaterial,
  createCourseMaterial,
  getCourseStudentsProgress,
} from "../api/ontologyApi";

function CourseEditorModal({ open, course, onClose, onCourseUpdated, onCourseChanged }) {
  const [activeTab, setActiveTab] = useState("modules");

  const [modules, setModules] = useState([]);
  const [lectures, setLectures] = useState([]);

  const [editingModule, setEditingModule] = useState(null);
  const [editingLecture, setEditingLecture] = useState(null);

  const [selectedModuleId, setSelectedModuleId] = useState("");
  const [selectedImageFile, setSelectedImageFile] = useState(null);

  // Состояния для редактора блоков лекции
  const [selectedLectureForBlocks, setSelectedLectureForBlocks] = useState(null);
  const [lectureBlocks, setLectureBlocks] = useState([]);
  const [editingBlock, setEditingBlock] = useState(null);
  const [selectedBlockImageFile, setSelectedBlockImageFile] = useState(null);

  // Состояния для вопросов
  const [questions, setQuestions] = useState([]);
  const [editingQuestion, setEditingQuestion] = useState(null);

  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [questionOptions, setQuestionOptions] = useState([]);
  const [questionConcepts, setQuestionConcepts] = useState([]);

  // Состояния для практических заданий
  const [practicals, setPracticals] = useState([]);
  const [editingPractical, setEditingPractical] = useState(null);
  const [selectedPractical, setSelectedPractical] = useState(null);
  const [practicalConcepts, setPracticalConcepts] = useState([]);
  const [selectedPracticalConceptId, setSelectedPracticalConceptId] = useState("");

  // Состояния для тестов
  const [testConcepts, setTestConcepts] = useState([]);
  const [selectedTestConceptId, setSelectedTestConceptId] = useState("");
  const [generatedTest, setGeneratedTest] = useState(null);

  const [testSettingsForm, setTestSettingsForm] = useState({
    pass_score: 70,
    question_count: 10,
    practical_count: 0,
    beginner_count: 4,
    intermediate_count: 4,
    advanced_count: 2,
  });

  // Состояния для материалов
  const [searchProfiles, setSearchProfiles] = useState([]);
  const [materialCandidates, setMaterialCandidates] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [candidateConcepts, setCandidateConcepts] = useState({});
  const [courseMaterials, setCourseMaterials] = useState([]);

  const [searchProfileForm, setSearchProfileForm] = useState({
    name: "",
    query: "",
    source: "arxiv",
    max_results: 10,
  });

  const [manualMaterialForm, setManualMaterialForm] = useState({
    title: "",
    description: "",
    source_url: "",
    resource_type: "article",
    concept_id: "",
  });

  const [graphNodes, setGraphNodes] = useState([]);

  const [loading, setLoading] = useState(false);

  const [moduleForm, setModuleForm] = useState({
    title: "",
    description: "",
    position: 1,
    is_published: true,
  });

  const [lectureForm, setLectureForm] = useState({
    title: "",
    content: "",
    image_url: "",
    position: 1,
    is_published: true,
  });

  const [blockForm, setBlockForm] = useState({
    block_type: "text",
    content: "",
    image_url: "",
    position: 1,
  });

  const [questionForm, setQuestionForm] = useState({
    question_text: "",
    question_type: "text",
    difficulty: "beginner",
    explanation: "",
    correct_answer: "",
  });

  const [optionForm, setOptionForm] = useState({
    option_text: "",
    is_correct: false,
    position: 1,
  });

  const [selectedConceptId, setSelectedConceptId] = useState("");

  const [practicalForm, setPracticalForm] = useState({
    title: "",
    description: "",
    task_type: "code",
    difficulty: "beginner",
    starter_code: "",
    tests_code: "",
    max_score: 100,
  });

  const [courseCoverFile, setCourseCoverFile] = useState(null);

  const [studentsProgress, setStudentsProgress] = useState(null);

  async function loadModules() {
    if (!course?.id) return;

    setLoading(true);

    try {
      const data = await getCourseModules(course.id);
      setModules(data);

      if (!selectedModuleId && data.length > 0) {
        setSelectedModuleId(String(data[0].id));
      }
    } finally {
      setLoading(false);
    }
  }

  async function loadLectures(moduleId = selectedModuleId) {
    if (!course?.id || !moduleId) {
      setLectures([]);
      return;
    }

    setLoading(true);

    try {
      const data = await getModuleLectures(course.id, moduleId);
      setLectures(data);
    } finally {
      setLoading(false);
    }
  }

  async function loadStudentsProgress() {
    if (!course?.id) return;

    const data = await getCourseStudentsProgress(course.id);
    setStudentsProgress(data);
  }

  // Функции для работы с блоками лекции
  async function loadLectureBlocks(lectureId) {
    if (!lectureId) return;

    const data = await getLectureBlocks(lectureId);
    setLectureBlocks(data);
  }

  async function openLectureBlockEditor(lecture) {
    setSelectedLectureForBlocks(lecture);
    setEditingBlock(null);
    setSelectedBlockImageFile(null);
    setBlockForm({
      block_type: "text",
      content: "",
      image_url: "",
      position: 1,
    });

    await loadLectureBlocks(lecture.id);
  }

  function resetBlockForm() {
    setEditingBlock(null);
    setSelectedBlockImageFile(null);
    setBlockForm({
      block_type: "text",
      content: "",
      image_url: "",
      position: lectureBlocks.length + 1,
    });
  }

  async function handleSaveBlock(event) {
    event.preventDefault();

    if (!selectedLectureForBlocks?.id) return;

    const payload = {
      block_type: blockForm.block_type,
      content: blockForm.block_type === "text" ? blockForm.content : null,
      image_url: blockForm.image_url || null,
      position: Number(blockForm.position),
    };

    let savedBlock;

    if (editingBlock) {
      savedBlock = await updateLectureBlock(
        selectedLectureForBlocks.id,
        editingBlock.id,
        payload
      );
    } else {
      savedBlock = await createLectureBlock(
        selectedLectureForBlocks.id,
        payload
      );
    }

    if (selectedBlockImageFile && savedBlock?.id) {
      await uploadLectureBlockImage(
        selectedLectureForBlocks.id,
        savedBlock.id,
        selectedBlockImageFile
      );
    }

    resetBlockForm();
    await loadLectureBlocks(selectedLectureForBlocks.id);
  }

  async function handleDeleteBlock(blockId) {
    if (!window.confirm("Удалить блок лекции?")) return;

    await deleteLectureBlock(selectedLectureForBlocks.id, blockId);
    await loadLectureBlocks(selectedLectureForBlocks.id);
  }

  // Функции для вопросов
  async function loadQuestions() {
    if (!course?.id) return;

    setLoading(true);

    try {
      const data = await getCourseQuestionBank(course.id);
      setQuestions(data);
    } finally {
      setLoading(false);
    }
  }

  async function loadGraphNodes() {
    if (!course?.id) return;

    const data = await getOntologyGraph(course.id);
    setGraphNodes(data.nodes || []);
  }

  async function loadQuestionDetails(question) {
    setSelectedQuestion(question);

    const [optionsData, conceptsData] = await Promise.all([
      getQuestionOptions(question.id),
      getQuestionConcepts(question.id),
    ]);

    setQuestionOptions(optionsData);
    setQuestionConcepts(conceptsData);
  }

  function resetQuestionForm() {
    setEditingQuestion(null);

    setQuestionForm({
      question_text: "",
      question_type: "text",
      difficulty: "beginner",
      explanation: "",
      correct_answer: "",
    });
  }

  function resetOptionForm() {
    setOptionForm({
      option_text: "",
      is_correct: false,
      position: questionOptions.length + 1,
    });
  }

  async function handleSaveQuestion(event) {
    event.preventDefault();

    if (!questionForm.question_text.trim()) return;

    const payload = {
      question_text: questionForm.question_text,
      question_type: questionForm.question_type,
      difficulty: questionForm.difficulty,
      explanation: questionForm.explanation,
      correct_answer:
        questionForm.question_type === "text"
          ? questionForm.correct_answer
          : null,
    };

    if (editingQuestion) {
      await updateCourseQuestion(course.id, editingQuestion.id, payload);
    } else {
      await createCourseQuestion(course.id, payload);
    }

    resetQuestionForm();
    await loadQuestions();
  }

  async function handleDeleteQuestion(questionId) {
    if (!window.confirm("Удалить вопрос?")) return;

    await deleteCourseQuestion(course.id, questionId);

    if (selectedQuestion?.id === questionId) {
      setSelectedQuestion(null);
      setQuestionOptions([]);
      setQuestionConcepts([]);
    }

    await loadQuestions();
  }

  async function handleAddOption(event) {
    event.preventDefault();

    if (!selectedQuestion?.id || !optionForm.option_text.trim()) return;

    await createQuestionOption(selectedQuestion.id, {
      option_text: optionForm.option_text,
      is_correct: optionForm.is_correct,
      position: Number(optionForm.position),
    });

    resetOptionForm();
    await loadQuestionDetails(selectedQuestion);
  }

  async function handleDeleteOption(optionId) {
    if (!selectedQuestion?.id) return;

    await deleteQuestionOption(selectedQuestion.id, optionId);
    await loadQuestionDetails(selectedQuestion);
  }

  async function handleAddQuestionConcept(event) {
    event.preventDefault();

    if (!selectedQuestion?.id || !selectedConceptId) return;

    await addQuestionConcept(selectedQuestion.id, selectedConceptId);

    setSelectedConceptId("");
    await loadQuestionDetails(selectedQuestion);
  }

  async function handleDeleteQuestionConcept(entityId) {
    if (!selectedQuestion?.id) return;

    await deleteQuestionConcept(selectedQuestion.id, entityId);
    await loadQuestionDetails(selectedQuestion);
  }

  // Функции для практических заданий
  async function loadPracticals() {
    if (!course?.id) return;

    setLoading(true);

    try {
      const data = await getCoursePracticalBank(course.id);
      setPracticals(data);
    } finally {
      setLoading(false);
    }
  }

  async function loadPracticalDetails(task) {
    setSelectedPractical(task);

    const data = await getPracticalConcepts(task.id);
    setPracticalConcepts(data);
  }

  function resetPracticalForm() {
    setEditingPractical(null);
    setPracticalForm({
      title: "",
      description: "",
      task_type: "code",
      difficulty: "beginner",
      starter_code: "",
      tests_code: "",
      max_score: 100,
    });
  }

  async function handleSavePractical(event) {
    event.preventDefault();

    if (!practicalForm.title.trim()) return;

    const payload = {
      title: practicalForm.title,
      description: practicalForm.description,
      task_type: practicalForm.task_type,
      difficulty: practicalForm.difficulty,
      starter_code: practicalForm.starter_code,
      tests_code: practicalForm.tests_code,
      max_score: Number(practicalForm.max_score),
    };

    if (editingPractical) {
      await updateCoursePractical(course.id, editingPractical.id, payload);
    } else {
      await createCoursePractical(course.id, payload);
    }

    resetPracticalForm();
    await loadPracticals();
  }

  async function handleDeletePractical(taskId) {
    if (!window.confirm("Удалить практическое задание?")) return;

    await deleteCoursePractical(course.id, taskId);

    if (selectedPractical?.id === taskId) {
      setSelectedPractical(null);
      setPracticalConcepts([]);
    }

    await loadPracticals();
  }

  async function handleAddPracticalConcept(event) {
    event.preventDefault();

    if (!selectedPractical?.id || !selectedPracticalConceptId) return;

    await addPracticalConcept(selectedPractical.id, selectedPracticalConceptId);

    setSelectedPracticalConceptId("");
    await loadPracticalDetails(selectedPractical);
  }

  async function handleDeletePracticalConcept(entityId) {
    if (!selectedPractical?.id) return;

    await deletePracticalConcept(selectedPractical.id, entityId);
    await loadPracticalDetails(selectedPractical);
  }

  // Функции для тестов
  async function loadTestData(moduleId = selectedModuleId) {
    if (!course?.id || !moduleId) return;

    try {
      const settings = await getModuleTestSettings(course.id, moduleId);

      setTestSettingsForm({
        pass_score: settings.pass_score,
        question_count: settings.question_count,
        practical_count: settings.practical_count,
        beginner_count: settings.beginner_count,
        intermediate_count: settings.intermediate_count,
        advanced_count: settings.advanced_count,
      });
    } catch {
      setTestSettingsForm({
        pass_score: 70,
        question_count: 10,
        practical_count: 0,
        beginner_count: 4,
        intermediate_count: 4,
        advanced_count: 2,
      });
    }

    const concepts = await getModuleTestConcepts(course.id, moduleId);
    setTestConcepts(concepts);
  }

  async function handleSaveTestSettings(event) {
    event.preventDefault();

    if (!selectedModuleId) return;

    const payload = {
      pass_score: Number(testSettingsForm.pass_score),
      question_count: Number(testSettingsForm.question_count),
      practical_count: Number(testSettingsForm.practical_count),
      beginner_count: Number(testSettingsForm.beginner_count),
      intermediate_count: Number(testSettingsForm.intermediate_count),
      advanced_count: Number(testSettingsForm.advanced_count),
    };

    try {
      await updateModuleTestSettings(course.id, selectedModuleId, payload);
    } catch {
      await createModuleTestSettings(course.id, selectedModuleId, payload);
    }

    await loadTestData(selectedModuleId);
  }

  async function handleAddTestConcept(event) {
    event.preventDefault();

    if (!selectedModuleId || !selectedTestConceptId) return;

    await addModuleTestConcept(course.id, selectedModuleId, selectedTestConceptId);

    setSelectedTestConceptId("");
    await loadTestData(selectedModuleId);
  }

  async function handleDeleteTestConcept(entityId) {
    if (!selectedModuleId) return;

    await deleteModuleTestConcept(course.id, selectedModuleId, entityId);
    await loadTestData(selectedModuleId);
  }

  async function handleGenerateTestPreview() {
    if (!selectedModuleId) return;

    const data = await generateModuleTest(course.id, selectedModuleId);
    setGeneratedTest(data);
  }

  // Функции для материалов
  async function loadCourseMaterials() {
    if (!course?.id) return;

    const data = await getCourseMaterials(course.id);
    setCourseMaterials(data);
  }

  async function loadMaterialSearchData() {
    setSearchLoading(true);

    try {
      const [profilesData, candidatesData] = await Promise.all([
        getMaterialSearchProfiles(course.id),
        getMaterialCandidates(course.id),
      ]);

      setSearchProfiles(profilesData);
      setMaterialCandidates(candidatesData);
      await loadCourseMaterials();
    } finally {
      setSearchLoading(false);
    }
  }

  async function handleCreateSearchProfile(event) {
    event.preventDefault();

    if (!searchProfileForm.name.trim() || !searchProfileForm.query.trim()) return;

    await createMaterialSearchProfile({
      name: searchProfileForm.name,
      keywords: searchProfileForm.query,
      source: searchProfileForm.source,
      required_keywords: "",
      excluded_keywords: "",
      max_results: Number(searchProfileForm.max_results),
      course_id: course.id,
    });

    setSearchProfileForm({
      name: "",
      query: "",
      source: "arxiv",
      max_results: 10,
    });

    await loadMaterialSearchData();
  }

  async function handleRunSearchProfile(profileId) {
    await runMaterialSearchProfile(profileId);
    await loadMaterialSearchData();
  }

  async function handleDeleteSearchProfile(profileId) {
    if (!window.confirm("Удалить профиль поиска?")) return;

    await deleteMaterialSearchProfile(profileId);
    await loadMaterialSearchData();
  }

  async function handleApproveCandidate(candidateId) {
    const conceptId = candidateConcepts[candidateId];

    if (!conceptId) {
      alert("Выберите концепт для привязки материала");
      return;
    }

    await approveMaterialCandidate(candidateId, {
      course_id: course.id,
      concept_id: Number(conceptId),
    });

    await loadMaterialSearchData();
  }

  async function handleRejectCandidate(candidateId) {
    await rejectMaterialCandidate(candidateId);
    await loadMaterialSearchData();
  }

  async function handleClearCandidates() {
    if (!window.confirm("Очистить список найденных материалов?")) return;

    await clearMaterialCandidates(course.id);
    await loadMaterialSearchData();
  }

  async function handleDeleteCourseMaterial(materialId) {
    if (!window.confirm("Удалить материал курса?")) return;

    await deleteCourseMaterial(materialId);
    await loadCourseMaterials();
  }

  async function handleCreateManualMaterial(event) {
    event.preventDefault();

    if (
      !manualMaterialForm.title.trim() ||
      !manualMaterialForm.source_url.trim() ||
      !manualMaterialForm.concept_id
    ) {
      alert("Заполните название, ссылку и концепт");
      return;
    }

    await createCourseMaterial(course.id, {
      title: manualMaterialForm.title,
      description: manualMaterialForm.description,
      source_url: manualMaterialForm.source_url,
      resource_type: manualMaterialForm.resource_type,
      concept_id: Number(manualMaterialForm.concept_id),
    });

    setManualMaterialForm({
      title: "",
      description: "",
      source_url: "",
      resource_type: "article",
      concept_id: "",
    });

    await loadCourseMaterials();
  }

  useEffect(() => {
    if (open && course?.id) {
      loadModules();
      setActiveTab("modules");
    }
  }, [open, course?.id]);

  useEffect(() => {
    if (activeTab === "lectures" && selectedModuleId) {
      loadLectures(selectedModuleId);
    }
  }, [activeTab, selectedModuleId]);

  useEffect(() => {
    if (activeTab === "questions" && course?.id) {
      loadQuestions();
      loadGraphNodes();
    }
  }, [activeTab, course?.id]);

  useEffect(() => {
    if (activeTab === "practicals" && course?.id) {
      loadPracticals();
      loadGraphNodes();
    }
  }, [activeTab, course?.id]);

  useEffect(() => {
    if (activeTab === "test" && course?.id) {
      loadGraphNodes();

      if (selectedModuleId) {
        loadTestData(selectedModuleId);
      }
    }
  }, [activeTab, course?.id, selectedModuleId]);

  useEffect(() => {
    if (activeTab === "materials" && course?.id) {
      loadMaterialSearchData();
      loadGraphNodes();
    }
  }, [activeTab, course?.id]);

  useEffect(() => {
    if (activeTab === "students") {
      loadStudentsProgress();
    }
  }, [activeTab, course?.id]);

  function resetModuleForm() {
    setEditingModule(null);
    setModuleForm({
      title: "",
      description: "",
      position: modules.length + 1,
      is_published: true,
    });
  }

  function resetLectureForm() {
    setEditingLecture(null);
    setSelectedImageFile(null);
    setLectureForm({
      title: "",
      content: "",
      image_url: "",
      position: lectures.length + 1,
      is_published: true,
    });
  }

  async function handleSaveModule(event) {
    event.preventDefault();

    if (!moduleForm.title.trim()) return;

    if (editingModule) {
      await updateCourseModule(course.id, editingModule.id, moduleForm);
    } else {
      await createCourseModule(course.id, moduleForm);
    }

    resetModuleForm();
    await loadModules();
  }

  async function handleDeleteModule(moduleId) {
    if (!window.confirm("Удалить модуль?")) return;

    await deleteCourseModule(course.id, moduleId);
    await loadModules();

    if (String(selectedModuleId) === String(moduleId)) {
      setSelectedModuleId("");
      setLectures([]);
    }
  }

  async function handleSaveLecture(event) {
    event.preventDefault();

    if (!selectedModuleId || !lectureForm.title.trim()) return;

    let savedLecture;

    const payload = {
      title: lectureForm.title,
      content: lectureForm.content,
      image_url: lectureForm.image_url || null,
      position: Number(lectureForm.position),
      is_published: lectureForm.is_published,
    };

    if (editingLecture) {
      savedLecture = await updateModuleLecture(
        course.id,
        selectedModuleId,
        editingLecture.id,
        payload
      );
    } else {
      savedLecture = await createModuleLecture(
        course.id,
        selectedModuleId,
        payload
      );
    }

    if (selectedImageFile && savedLecture?.id) {
      await uploadLectureImage(savedLecture.id, selectedImageFile);
    }

    resetLectureForm();
    await loadLectures(selectedModuleId);
  }

  async function handleDeleteLecture(lectureId) {
    if (!window.confirm("Удалить лекцию?")) return;

    await deleteModuleLecture(course.id, selectedModuleId, lectureId);
    await loadLectures(selectedModuleId);
  }

  async function handleTogglePublish() {
    let updatedCourse;

    if (course.status === "published") {
      updatedCourse = await unpublishCourse(course.id);
    } else {
      updatedCourse = await publishCourse(course.id);
    }

    if (onCourseChanged) {
      onCourseChanged(updatedCourse);
    }

    if (onCourseUpdated) {
      await onCourseUpdated();
    }
  }

  async function handleUploadCourseCover(event) {
    event.preventDefault();

    if (!courseCoverFile || !course?.id) return;

    const uploaded = await uploadCourseCover(course.id, courseCoverFile);

    setCourseCoverFile(null);

    if (onCourseChanged) {
      onCourseChanged({
        ...course,
        cover_url: uploaded.cover_url,
      });
    }

    if (onCourseUpdated) {
      await onCourseUpdated();
    }
  }

  if (!open || !course) return null;

  return (
    <div className="relation-modal-overlay">
      <div className="course-editor-modal">
        <div className="course-modal-head">
          <div>
            <h3>Редактор курса</h3>
            <p>{course.title}</p>
          </div>

          <button type="button" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="course-editor-status">
          <span>
            Статус:{" "}
            <b>{course.status === "published" ? "Опубликован" : "Черновик"}</b>
          </span>

          <button type="button" onClick={handleTogglePublish}>
            {course.status === "published"
              ? "Снять с публикации"
              : "Опубликовать"}
          </button>
        </div>

        <form className="course-cover-panel" onSubmit={handleUploadCourseCover}>
          <div className="course-cover-preview">
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
              <span>Обложка курса</span>
            )}
          </div>

          <div className="course-cover-controls">
            <h4>Обложка курса</h4>
            <p>Загрузите изображение, которое будет отображаться на главной странице.</p>

            <input
              type="file"
              accept="image/*"
              onChange={(e) => setCourseCoverFile(e.target.files[0])}
            />

            <button type="submit" disabled={!courseCoverFile}>
              Загрузить обложку
            </button>
          </div>
        </form>

        <div className="course-editor-tabs">
          <button
            className={activeTab === "modules" ? "active" : ""}
            onClick={() => setActiveTab("modules")}
          >
            Модули
          </button>

          <button
            className={activeTab === "lectures" ? "active" : ""}
            onClick={() => setActiveTab("lectures")}
          >
            Лекции
          </button>

          <button
            className={activeTab === "questions" ? "active" : ""}
            onClick={() => setActiveTab("questions")}
          >
            Вопросы
          </button>

          <button
            className={activeTab === "practicals" ? "active" : ""}
            onClick={() => setActiveTab("practicals")}
          >
            Практики
          </button>

          <button
            className={activeTab === "test" ? "active" : ""}
            onClick={() => setActiveTab("test")}
          >
            Тест
          </button>

          <button
            className={activeTab === "materials" ? "active" : ""}
            onClick={() => setActiveTab("materials")}
          >
            Материалы
          </button>

          <button
            type="button"
            className={activeTab === "students" ? "active" : ""}
            onClick={() => setActiveTab("students")}
          >
            Студенты
          </button>
        </div>

        {activeTab === "modules" && (
          <div className="course-editor-grid">
            <form className="course-builder-form" onSubmit={handleSaveModule}>
              <h4>{editingModule ? "Редактировать модуль" : "Новый модуль"}</h4>

              <label>
                Название модуля
                <input
                  value={moduleForm.title}
                  onChange={(e) =>
                    setModuleForm({
                      ...moduleForm,
                      title: e.target.value,
                    })
                  }
                  placeholder="Например: Основы сегментации"
                />
              </label>

              <label>
                Описание
                <textarea
                  rows="4"
                  value={moduleForm.description}
                  onChange={(e) =>
                    setModuleForm({
                      ...moduleForm,
                      description: e.target.value,
                    })
                  }
                  placeholder="Краткое описание модуля"
                />
              </label>

              <label>
                Позиция
                <input
                  type="number"
                  value={moduleForm.position}
                  onChange={(e) =>
                    setModuleForm({
                      ...moduleForm,
                      position: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={moduleForm.is_published}
                  onChange={(e) =>
                    setModuleForm({
                      ...moduleForm,
                      is_published: e.target.checked,
                    })
                  }
                />
                Опубликовать модуль
              </label>

              <button type="submit">
                {editingModule ? "Сохранить модуль" : "Создать модуль"}
              </button>

              {editingModule && (
                <button type="button" onClick={resetModuleForm}>
                  Отмена
                </button>
              )}
            </form>

            <div className="course-builder-list">
              <h4>Модули курса</h4>

              {loading ? (
                <p>Загрузка...</p>
              ) : modules.length > 0 ? (
                modules.map((module) => (
                  <div className="course-mini-card" key={module.id}>
                    <div className="course-mini-card-head">
                      <strong>
                        {module.position}. {module.title}
                      </strong>

                      <span>
                        {module.is_published ? "Опубликован" : "Черновик"}
                      </span>
                    </div>

                    <p>{module.description || "Описание не указано."}</p>

                    <div className="course-actions">
                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => {
                          setEditingModule(module);
                          setModuleForm({
                            title: module.title,
                            description: module.description || "",
                            position: module.position,
                            is_published: module.is_published,
                          });
                        }}
                      >
                        Редактировать
                      </button>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeleteModule(module.id)}
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Модулей пока нет</h4>
                  <p>Создайте первый модуль курса.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "lectures" && (
          <div className="course-editor-grid">
            <form className="course-builder-form" onSubmit={handleSaveLecture}>
              <h4>{editingLecture ? "Редактировать лекцию" : "Новая лекция"}</h4>

              <label>
                Модуль
                <select
                  value={selectedModuleId}
                  onChange={(e) => {
                    setSelectedModuleId(e.target.value);
                    resetLectureForm();
                  }}
                >
                  <option value="">Выберите модуль</option>

                  {modules.map((module) => (
                    <option key={module.id} value={module.id}>
                      {module.position}. {module.title}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Название лекции
                <input
                  value={lectureForm.title}
                  onChange={(e) =>
                    setLectureForm({
                      ...lectureForm,
                      title: e.target.value,
                    })
                  }
                  placeholder="Например: Что такое сегментация"
                />
              </label>

              <label>
                Текст лекции
                <textarea
                  rows="8"
                  value={lectureForm.content}
                  onChange={(e) =>
                    setLectureForm({
                      ...lectureForm,
                      content: e.target.value,
                    })
                  }
                  placeholder="Введите текст лекции..."
                />
              </label>

              <label>
                Позиция
                <input
                  type="number"
                  value={lectureForm.position}
                  onChange={(e) =>
                    setLectureForm({
                      ...lectureForm,
                      position: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Картинка лекции
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setSelectedImageFile(e.target.files[0])}
                />
              </label>

              {lectureForm.image_url && (
                <div className="lecture-image-preview">
                  <img
                    src={`http://127.0.0.1:8000${lectureForm.image_url}`}
                    alt=""
                  />
                </div>
              )}

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={lectureForm.is_published}
                  onChange={(e) =>
                    setLectureForm({
                      ...lectureForm,
                      is_published: e.target.checked,
                    })
                  }
                />
                Опубликовать лекцию
              </label>

              <button type="submit">
                {editingLecture ? "Сохранить лекцию" : "Создать лекцию"}
              </button>

              {editingLecture && (
                <button type="button" onClick={resetLectureForm}>
                  Отмена
                </button>
              )}
            </form>

            <div className="course-builder-list">
              <h4>Лекции модуля</h4>

              {!selectedModuleId ? (
                <div className="empty-course-state">
                  <h4>Выберите модуль</h4>
                  <p>Лекции создаются внутри конкретного модуля.</p>
                </div>
              ) : loading ? (
                <p>Загрузка...</p>
              ) : lectures.length > 0 ? (
                lectures.map((lecture) => (
                  <div className="course-mini-card" key={lecture.id}>
                    <div className="course-mini-card-head">
                      <strong>
                        {lecture.position}. {lecture.title}
                      </strong>

                      <span>
                        {lecture.is_published ? "Опубликована" : "Черновик"}
                      </span>
                    </div>

                    <p>{lecture.content || "Текст лекции не указан."}</p>

                    {lecture.image_url && (
                      <div className="lecture-image-preview">
                        <img
                          src={`http://127.0.0.1:8000${lecture.image_url}`}
                          alt=""
                        />
                      </div>
                    )}

                    <div className="course-actions">
                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => {
                          setEditingLecture(lecture);
                          setLectureForm({
                            title: lecture.title,
                            content: lecture.content || "",
                            image_url: lecture.image_url || "",
                            position: lecture.position,
                            is_published: lecture.is_published,
                          });
                          setSelectedImageFile(null);
                        }}
                      >
                        Редактировать
                      </button>

                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => openLectureBlockEditor(lecture)}
                      >
                        Открыть редактор
                      </button>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeleteLecture(lecture.id)}
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Лекций пока нет</h4>
                  <p>Создайте первую лекцию для выбранного модуля.</p>
                </div>
              )}
            </div>

            {/* Редактор содержимого лекции (блоки) */}
            {selectedLectureForBlocks && (
              <div className="lecture-block-editor">
                <div className="lecture-block-editor-head">
                  <div>
                    <h4>Редактор содержимого лекции</h4>
                    <p>{selectedLectureForBlocks.title}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setSelectedLectureForBlocks(null);
                      setLectureBlocks([]);
                    }}
                  >
                    Закрыть редактор
                  </button>
                </div>

                <form className="lecture-block-form" onSubmit={handleSaveBlock}>
                  <label>
                    Тип блока
                    <select
                      value={blockForm.block_type}
                      onChange={(e) =>
                        setBlockForm({
                          ...blockForm,
                          block_type: e.target.value,
                        })
                      }
                    >
                      <option value="text">Текст</option>
                      <option value="image">Изображение</option>
                    </select>
                  </label>

                  {blockForm.block_type === "text" ? (
                    <label>
                      Текстовый блок
                      <textarea
                        rows="12"
                        value={blockForm.content}
                        onChange={(e) =>
                          setBlockForm({
                            ...blockForm,
                            content: e.target.value,
                          })
                        }
                        placeholder="Введите часть лекции..."
                      />
                    </label>
                  ) : (
                    <label>
                      Изображение
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => setSelectedBlockImageFile(e.target.files[0])}
                      />
                    </label>
                  )}

                  <label>
                    Позиция
                    <input
                      type="number"
                      value={blockForm.position}
                      onChange={(e) =>
                        setBlockForm({
                          ...blockForm,
                          position: Number(e.target.value),
                        })
                      }
                    />
                  </label>

                  <button type="submit">
                    {editingBlock ? "Сохранить блок" : "Добавить блок"}
                  </button>

                  {editingBlock && (
                    <button type="button" onClick={resetBlockForm}>
                      Отмена
                    </button>
                  )}
                </form>

                <div className="lecture-blocks-list">
                  {lectureBlocks.length > 0 ? (
                    lectureBlocks.map((block) => (
                      <div className="lecture-block-card" key={block.id}>
                        <div className="lecture-block-card-head">
                          <strong>
                            {block.position}.{" "}
                            {block.block_type === "text" ? "Текст" : "Изображение"}
                          </strong>
                        </div>

                        {block.block_type === "text" ? (
                          <p>{block.content}</p>
                        ) : block.image_url ? (
                          <img
                            src={`http://127.0.0.1:8000${block.image_url}`}
                            alt=""
                          />
                        ) : (
                          <p>Изображение не загружено.</p>
                        )}

                        <div className="course-actions">
                          <button
                            type="button"
                            className="edit-btn"
                            onClick={() => {
                              setEditingBlock(block);
                              setSelectedBlockImageFile(null);
                              setBlockForm({
                                block_type: block.block_type,
                                content: block.content || "",
                                image_url: block.image_url || "",
                                position: block.position,
                              });
                            }}
                          >
                            Редактировать
                          </button>

                          <button
                            type="button"
                            className="delete-course-btn"
                            onClick={() => handleDeleteBlock(block.id)}
                          >
                            Удалить
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="empty-course-state">
                      <h4>Блоков пока нет</h4>
                      <p>Добавьте текст или изображение в лекцию.</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "questions" && (
          <div className="course-editor-grid">
            <form className="course-builder-form" onSubmit={handleSaveQuestion}>
              <h4>{editingQuestion ? "Редактировать вопрос" : "Новый вопрос"}</h4>

              <label>
                Текст вопроса
                <textarea
                  rows="5"
                  value={questionForm.question_text}
                  onChange={(e) =>
                    setQuestionForm({
                      ...questionForm,
                      question_text: e.target.value,
                    })
                  }
                  placeholder="Введите текст вопроса..."
                />
              </label>

              <label>
                Тип вопроса
                <select
                  value={questionForm.question_type}
                  onChange={(e) =>
                    setQuestionForm({
                      ...questionForm,
                      question_type: e.target.value,
                    })
                  }
                >
                  <option value="text">Текстовый ответ</option>
                  <option value="single_choice">Один вариант</option>
                  <option value="multiple_choice">Несколько вариантов</option>
                </select>
              </label>

              <label>
                Сложность
                <select
                  value={questionForm.difficulty}
                  onChange={(e) =>
                    setQuestionForm({
                      ...questionForm,
                      difficulty: e.target.value,
                    })
                  }
                >
                  <option value="beginner">beginner</option>
                  <option value="intermediate">intermediate</option>
                  <option value="advanced">advanced</option>
                </select>
              </label>

              {questionForm.question_type === "text" && (
                <label>
                  Правильный ответ
                  <input
                    value={questionForm.correct_answer}
                    onChange={(e) =>
                      setQuestionForm({
                        ...questionForm,
                        correct_answer: e.target.value,
                      })
                    }
                    placeholder="Например: convolutional neural network"
                  />
                </label>
              )}

              <label>
                Пояснение
                <textarea
                  rows="3"
                  value={questionForm.explanation}
                  onChange={(e) =>
                    setQuestionForm({
                      ...questionForm,
                      explanation: e.target.value,
                    })
                  }
                  placeholder="Пояснение после ответа..."
                />
              </label>

              <button type="submit">
                {editingQuestion ? "Сохранить вопрос" : "Создать вопрос"}
              </button>

              {editingQuestion && (
                <button type="button" onClick={resetQuestionForm}>
                  Отмена
                </button>
              )}
            </form>

            <div className="course-builder-list">
              <h4>Банк вопросов</h4>

              {loading ? (
                <p>Загрузка...</p>
              ) : questions.length > 0 ? (
                questions.map((question) => (
                  <div className="course-mini-card" key={question.id}>
                    <div className="course-mini-card-head">
                      <strong>{question.question_text}</strong>
                      <span>{question.difficulty}</span>
                    </div>

                    <p>Тип: {question.question_type}</p>

                    <div className="course-actions">
                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => {
                          setEditingQuestion(question);
                          setQuestionForm({
                            question_text: question.question_text,
                            question_type: question.question_type,
                            difficulty: question.difficulty,
                            explanation: question.explanation || "",
                            correct_answer: question.correct_answer || "",
                          });
                        }}
                      >
                        Редактировать
                      </button>

                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => loadQuestionDetails(question)}
                      >
                        Настроить
                      </button>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeleteQuestion(question.id)}
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Вопросов пока нет</h4>
                  <p>Создайте первый вопрос для банка курса.</p>
                </div>
              )}
            </div>

            {selectedQuestion && (
              <div className="lecture-block-editor">
                <div className="lecture-block-editor-head">
                  <div>
                    <h4>Настройка вопроса</h4>
                    <p>{selectedQuestion.question_text}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setSelectedQuestion(null);
                      setQuestionOptions([]);
                      setQuestionConcepts([]);
                    }}
                  >
                    Закрыть
                  </button>
                </div>

                {selectedQuestion.question_type !== "text" && (
                  <form className="lecture-block-form" onSubmit={handleAddOption}>
                    <h4>Варианты ответа</h4>

                    <label>
                      Текст варианта
                      <input
                        value={optionForm.option_text}
                        onChange={(e) =>
                          setOptionForm({
                            ...optionForm,
                            option_text: e.target.value,
                          })
                        }
                        placeholder="Введите вариант ответа"
                      />
                    </label>

                    <label>
                      Позиция
                      <input
                        type="number"
                        value={optionForm.position}
                        onChange={(e) =>
                          setOptionForm({
                            ...optionForm,
                            position: Number(e.target.value),
                          })
                        }
                      />
                    </label>

                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={optionForm.is_correct}
                        onChange={(e) =>
                          setOptionForm({
                            ...optionForm,
                            is_correct: e.target.checked,
                          })
                        }
                      />
                      Правильный вариант
                    </label>

                    <button type="submit">Добавить вариант</button>
                  </form>
                )}

                {selectedQuestion.question_type !== "text" && (
                  <div className="lecture-blocks-list">
                    {questionOptions.map((option) => (
                      <div className="lecture-block-card" key={option.id}>
                        <strong>
                          {option.position}. {option.option_text}
                        </strong>
                        <p>{option.is_correct ? "Правильный" : "Неправильный"}</p>

                        <button
                          type="button"
                          className="delete-course-btn"
                          onClick={() => handleDeleteOption(option.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                <form className="lecture-block-form" onSubmit={handleAddQuestionConcept}>
                  <h4>Связанные концепты</h4>

                  <label>
                    Концепт
                    <select
                      value={selectedConceptId}
                      onChange={(e) => setSelectedConceptId(e.target.value)}
                    >
                      <option value="">Выберите концепт</option>

                      {graphNodes.map((node) => (
                        <option key={node.id} value={node.id}>
                          {node.label} — {node.type}
                        </option>
                      ))}
                    </select>
                  </label>

                  <button type="submit">Привязать концепт</button>
                </form>

                <div className="lecture-blocks-list">
                  {questionConcepts.map((concept) => (
                    <div className="lecture-block-card" key={concept.id}>
                      <strong>
                        {concept.entity_name} — {concept.entity_type}
                      </strong>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeleteQuestionConcept(concept.entity_id)}
                      >
                        Удалить связь
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "practicals" && (
          <div className="course-editor-grid">
            <form className="course-builder-form" onSubmit={handleSavePractical}>
              <h4>{editingPractical ? "Редактировать практику" : "Новая практика"}</h4>

              <label>
                Название задания
                <input
                  value={practicalForm.title}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      title: e.target.value,
                    })
                  }
                  placeholder="Например: Реализация IoU"
                />
              </label>

              <label>
                Описание задания
                <textarea
                  rows="5"
                  value={practicalForm.description}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      description: e.target.value,
                    })
                  }
                  placeholder="Что должен сделать студент..."
                />
              </label>

              <label>
                Тип задания
                <select
                  value={practicalForm.task_type}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      task_type: e.target.value,
                    })
                  }
                >
                  <option value="code">Код</option>
                  <option value="iou_function">IoU-функция</option>
                  <option value="custom_pytests">Pytest-проверка</option>
                  <option value="segmentation">Сегментация изображения</option>
                </select>
              </label>

              <label>
                Сложность
                <select
                  value={practicalForm.difficulty}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      difficulty: e.target.value,
                    })
                  }
                >
                  <option value="beginner">beginner</option>
                  <option value="intermediate">intermediate</option>
                  <option value="advanced">advanced</option>
                </select>
              </label>

              <label>
                Стартовый код
                <textarea
                  rows="8"
                  value={practicalForm.starter_code}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      starter_code: e.target.value,
                    })
                  }
                  placeholder="Код, который увидит студент..."
                />
              </label>

              <label>
                Код проверки / тесты
                <textarea
                  rows="8"
                  value={practicalForm.tests_code}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      tests_code: e.target.value,
                    })
                  }
                  placeholder="Проверочные тесты..."
                />
              </label>

              <label>
                Максимальный балл
                <input
                  type="number"
                  value={practicalForm.max_score}
                  onChange={(e) =>
                    setPracticalForm({
                      ...practicalForm,
                      max_score: Number(e.target.value),
                    })
                  }
                />
              </label>

              <button type="submit">
                {editingPractical ? "Сохранить практику" : "Создать практику"}
              </button>

              {editingPractical && (
                <button type="button" onClick={resetPracticalForm}>
                  Отмена
                </button>
              )}
            </form>

            <div className="course-builder-list">
              <h4>Банк практических заданий</h4>

              {loading ? (
                <p>Загрузка...</p>
              ) : practicals.length > 0 ? (
                practicals.map((task) => (
                  <div className="course-mini-card" key={task.id}>
                    <div className="course-mini-card-head">
                      <strong>{task.title}</strong>
                      <span>{task.difficulty}</span>
                    </div>

                    <p>{task.description || "Описание не указано."}</p>
                    <small>Тип: {task.task_type}</small>

                    <div className="course-actions">
                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => {
                          setEditingPractical(task);
                          setPracticalForm({
                            title: task.title,
                            description: task.description || "",
                            task_type: task.task_type,
                            difficulty: task.difficulty,
                            starter_code: task.starter_code || "",
                            tests_code: task.tests_code || "",
                            max_score: task.max_score,
                          });
                        }}
                      >
                        Редактировать
                      </button>

                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => loadPracticalDetails(task)}
                      >
                        Концепты
                      </button>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeletePractical(task.id)}
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Практик пока нет</h4>
                  <p>Создайте первое практическое задание.</p>
                </div>
              )}
            </div>

            {selectedPractical && (
              <div className="lecture-block-editor">
                <div className="lecture-block-editor-head">
                  <div>
                    <h4>Концепты практического задания</h4>
                    <p>{selectedPractical.title}</p>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setSelectedPractical(null);
                      setPracticalConcepts([]);
                    }}
                  >
                    Закрыть
                  </button>
                </div>

                <form className="lecture-block-form" onSubmit={handleAddPracticalConcept}>
                  <label>
                    Концепт
                    <select
                      value={selectedPracticalConceptId}
                      onChange={(e) => setSelectedPracticalConceptId(e.target.value)}
                    >
                      <option value="">Выберите концепт</option>

                      {graphNodes.map((node) => (
                        <option key={node.id} value={node.id}>
                          {node.label} — {node.type}
                        </option>
                      ))}
                    </select>
                  </label>

                  <button type="submit">Привязать концепт</button>
                </form>

                <div className="lecture-blocks-list">
                  {practicalConcepts.length > 0 ? (
                    practicalConcepts.map((concept) => (
                      <div className="lecture-block-card" key={concept.id}>
                        <strong>
                          {concept.entity_name} — {concept.entity_type}
                        </strong>

                        <button
                          type="button"
                          className="delete-course-btn"
                          onClick={() => handleDeletePracticalConcept(concept.entity_id)}
                        >
                          Удалить связь
                        </button>
                      </div>
                    ))
                  ) : (
                    <div className="empty-course-state">
                      <h4>Концепты не привязаны</h4>
                      <p>Привяжите практику к одному или нескольким концептам.</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "test" && (
          <div className="course-editor-grid">
            <form className="course-builder-form" onSubmit={handleSaveTestSettings}>
              <h4>Настройки теста модуля</h4>

              <label>
                Модуль
                <select
                  value={selectedModuleId}
                  onChange={(e) => {
                    setSelectedModuleId(e.target.value);
                    setGeneratedTest(null);
                  }}
                >
                  <option value="">Выберите модуль</option>

                  {modules.map((module) => (
                    <option key={module.id} value={module.id}>
                      {module.position}. {module.title}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Проходной балл
                <input
                  type="number"
                  value={testSettingsForm.pass_score}
                  onChange={(e) =>
                    setTestSettingsForm({
                      ...testSettingsForm,
                      pass_score: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Количество вопросов
                <input
                  type="number"
                  value={testSettingsForm.question_count}
                  onChange={(e) =>
                    setTestSettingsForm({
                      ...testSettingsForm,
                      question_count: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Количество практик
                <input
                  type="number"
                  value={testSettingsForm.practical_count}
                  onChange={(e) =>
                    setTestSettingsForm({
                      ...testSettingsForm,
                      practical_count: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Beginner
                <input
                  type="number"
                  value={testSettingsForm.beginner_count}
                  onChange={(e) =>
                    setTestSettingsForm({
                      ...testSettingsForm,
                      beginner_count: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Intermediate
                <input
                  type="number"
                  value={testSettingsForm.intermediate_count}
                  onChange={(e) =>
                    setTestSettingsForm({
                      ...testSettingsForm,
                      intermediate_count: Number(e.target.value),
                    })
                  }
                />
              </label>

              <label>
                Advanced
                <input
                  type="number"
                  value={testSettingsForm.advanced_count}
                  onChange={(e) =>
                    setTestSettingsForm({
                      ...testSettingsForm,
                      advanced_count: Number(e.target.value),
                    })
                  }
                />
              </label>

              <button type="submit">Сохранить настройки</button>

              <button
                type="button"
                onClick={handleGenerateTestPreview}
                disabled={!selectedModuleId}
              >
                Сгенерировать тест
              </button>
            </form>

            <div className="course-builder-list">
              <h4>Концепты теста</h4>

              <form className="lecture-block-form" onSubmit={handleAddTestConcept}>
                <label>
                  Концепт
                  <select
                    value={selectedTestConceptId}
                    onChange={(e) => setSelectedTestConceptId(e.target.value)}
                  >
                    <option value="">Выберите концепт</option>

                    {graphNodes.map((node) => (
                      <option key={node.id} value={node.id}>
                        {node.label} — {node.type}
                      </option>
                    ))}
                  </select>
                </label>

                <button type="submit">Добавить концепт</button>
              </form>

              {testConcepts.length > 0 ? (
                testConcepts.map((concept) => (
                  <div className="course-mini-card" key={concept.id}>
                    <div className="course-mini-card-head">
                      <strong>
                        {concept.entity_name} — {concept.entity_type}
                      </strong>
                    </div>

                    <button
                      type="button"
                      className="delete-course-btn"
                      onClick={() => handleDeleteTestConcept(concept.entity_id)}
                    >
                      Удалить
                    </button>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Концепты не выбраны</h4>
                  <p>Добавьте концепты, по которым будет собираться тест.</p>
                </div>
              )}

              {generatedTest && (
                <div className="lecture-block-editor">
                  <h4>Предпросмотр сгенерированного теста</h4>

                  <p>
                    Attempt ID: <b>{generatedTest.attempt_id}</b>
                  </p>

                  <h4>Вопросы</h4>

                  {generatedTest.questions.map((question) => (
                    <div className="lecture-block-card" key={question.id}>
                      <strong>{question.question_text}</strong>
                      <p>
                        {question.difficulty} / {question.question_type}
                      </p>
                    </div>
                  ))}

                  <h4>Практики</h4>

                  {generatedTest.practical_tasks.map((task) => (
                    <div className="lecture-block-card" key={task.id}>
                      <strong>{task.title}</strong>
                      <p>{task.difficulty}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "materials" && (
          <div className="course-editor-grid">
            <form className="course-builder-form" onSubmit={handleCreateSearchProfile}>
              <h4>Профиль автопоиска</h4>

              <label>
                Название профиля
                <input
                  value={searchProfileForm.name}
                  onChange={(e) =>
                    setSearchProfileForm({
                      ...searchProfileForm,
                      name: e.target.value,
                    })
                  }
                  placeholder="Например: Поиск статей по CNN"
                />
              </label>

              <label>
                Поисковый запрос
                <textarea
                  rows="4"
                  value={searchProfileForm.query}
                  onChange={(e) =>
                    setSearchProfileForm({
                      ...searchProfileForm,
                      query: e.target.value,
                    })
                  }
                  placeholder="Например: image segmentation convolutional neural network"
                />
              </label>

              <label>
                Источник
                <select
                  value={searchProfileForm.source}
                  onChange={(e) =>
                    setSearchProfileForm({
                      ...searchProfileForm,
                      source: e.target.value,
                    })
                  }
                >
                  <option value="arxiv">arXiv</option>
                  <option value="semantic_scholar">Semantic Scholar</option>
                  <option value="crossref">Crossref</option>
                </select>
              </label>

              <label>
                Количество результатов
                <input
                  type="number"
                  value={searchProfileForm.max_results}
                  onChange={(e) =>
                    setSearchProfileForm({
                      ...searchProfileForm,
                      max_results: Number(e.target.value),
                    })
                  }
                />
              </label>

              <button type="submit">Создать профиль</button>
            </form>

            <div className="course-builder-list">
              <h4>Профили поиска</h4>

              {searchLoading ? (
                <p>Загрузка...</p>
              ) : searchProfiles.length > 0 ? (
                searchProfiles.map((profile) => (
                  <div className="course-mini-card" key={profile.id}>
                    <div className="course-mini-card-head">
                      <strong>{profile.name}</strong>
                      <span>{profile.source}</span>
                    </div>

                    <p>{profile.query}</p>

                    <div className="course-actions">
                      <button
                        type="button"
                        className="edit-btn"
                        onClick={() => handleRunSearchProfile(profile.id)}
                      >
                        Запустить поиск
                      </button>

                      <button
                        type="button"
                        className="delete-course-btn"
                        onClick={() => handleDeleteSearchProfile(profile.id)}
                      >
                        Удалить
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-course-state">
                  <h4>Профилей пока нет</h4>
                  <p>Создайте профиль поиска научных материалов.</p>
                </div>
              )}
            </div>

            <div className="lecture-block-editor">
              <h4>Найденные материалы</h4>

              <button
                type="button"
                className="delete-course-btn"
                onClick={handleClearCandidates}
              >
                Очистить найденные материалы
              </button>

              {materialCandidates.length > 0 ? (
                <div className="lecture-blocks-list">
                  {materialCandidates.map((candidate) => (
                    <div className="lecture-block-card" key={candidate.id}>
                      <strong>{candidate.title}</strong>

                      <p>{candidate.abstract || candidate.summary || "Описание не указано."}</p>

                      {candidate.url && (
                        <a href={candidate.url} target="_blank" rel="noreferrer">
                          Открыть источник
                        </a>
                      )}

                      <label>
                        Привязать к концепту
                        <select
                          value={candidateConcepts[candidate.id] || ""}
                          onChange={(e) =>
                            setCandidateConcepts({
                              ...candidateConcepts,
                              [candidate.id]: e.target.value,
                            })
                          }
                        >
                          <option value="">Выберите концепт</option>

                          {graphNodes.map((node) => (
                            <option key={node.id} value={node.id}>
                              {node.label} — {node.type}
                            </option>
                          ))}
                        </select>
                      </label>

                      <div className="course-actions">
                        <button
                          type="button"
                          className="edit-btn"
                          onClick={() => handleApproveCandidate(candidate.id)}
                        >
                          Одобрить
                        </button>

                        <button
                          type="button"
                          className="delete-course-btn"
                          onClick={() => handleRejectCandidate(candidate.id)}
                        >
                          Отклонить
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-course-state">
                  <h4>Кандидатов пока нет</h4>
                  <p>Запустите профиль поиска, чтобы получить материалы.</p>
                </div>
              )}
            </div>

            <form className="course-builder-form" onSubmit={handleCreateManualMaterial}>
              <h4>Добавить материал вручную</h4>

              <label>
                Название материала
                <input
                  value={manualMaterialForm.title}
                  onChange={(e) =>
                    setManualMaterialForm({
                      ...manualMaterialForm,
                      title: e.target.value,
                    })
                  }
                  placeholder="Например: Semantic Segmentation Explained"
                />
              </label>

              <label>
                Описание
                <textarea
                  rows="3"
                  value={manualMaterialForm.description}
                  onChange={(e) =>
                    setManualMaterialForm({
                      ...manualMaterialForm,
                      description: e.target.value,
                    })
                  }
                  placeholder="Кратко опишите, чем полезен материал"
                />
              </label>

              <label>
                Ссылка
                <input
                  value={manualMaterialForm.source_url}
                  onChange={(e) =>
                    setManualMaterialForm({
                      ...manualMaterialForm,
                      source_url: e.target.value,
                    })
                  }
                  placeholder="https://..."
                />
              </label>

              <label>
                Тип материала
                <select
                  value={manualMaterialForm.resource_type}
                  onChange={(e) =>
                    setManualMaterialForm({
                      ...manualMaterialForm,
                      resource_type: e.target.value,
                    })
                  }
                >
                  <option value="article">Статья</option>
                  <option value="video">Видео</option>
                  <option value="habr">Habr</option>
                  <option value="youtube">YouTube</option>
                  <option value="documentation">Документация</option>
                </select>
              </label>

              <label>
                Привязать к концепту
                <select
                  value={manualMaterialForm.concept_id}
                  onChange={(e) =>
                    setManualMaterialForm({
                      ...manualMaterialForm,
                      concept_id: e.target.value,
                    })
                  }
                >
                  <option value="">Выберите концепт</option>

                  {graphNodes.map((node) => (
                    <option key={node.id} value={node.id}>
                      {node.label} — {node.type}
                    </option>
                  ))}
                </select>
              </label>

              <button type="submit">Добавить материал</button>
            </form>

            <div className="lecture-block-editor">
              <h4>Материалы курса</h4>

              {courseMaterials.length > 0 ? (
                <div className="lecture-blocks-list">
                  {courseMaterials.map((material) => (
                    <div className="lecture-block-card" key={material.id}>
                      <strong>{material.title}</strong>

                      <p>{material.content || "Описание не указано."}</p>

                      {material.concepts?.length > 0 && (
                        <div className="material-concepts-row">
                          {material.concepts.map((concept) => (
                            <span key={concept.id}>
                              {concept.name} — {concept.type}
                            </span>
                          ))}
                        </div>
                      )}

                      <div className="course-actions">
                        {material.source_url && (
                          <a
                            href={material.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="edit-btn"
                          >
                            Открыть источник
                          </a>
                        )}

                        {material.pdf_url && (
                          <a
                            href={material.pdf_url}
                            target="_blank"
                            rel="noreferrer"
                            className="edit-btn"
                          >
                            Скачать PDF
                          </a>
                        )}

                        <button
                          type="button"
                          className="delete-course-btn"
                          onClick={() => handleDeleteCourseMaterial(material.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-course-state">
                  <h4>Материалов пока нет</h4>
                  <p>Одобрите найденную статью, чтобы она появилась в материалах курса.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === "students" && (
          <div className="course-editor-section">
            <div className="section-head">
              <div>
                <h3>Статистика студентов</h3>
                <p>
                  Прогресс обучающихся, последние попытки и слабые концепты по курсу.
                </p>
              </div>

              <button type="button" onClick={loadStudentsProgress}>
                Обновить
              </button>
            </div>

            {!studentsProgress || studentsProgress.students.length === 0 ? (
              <div className="empty-state">
                <h4>Студентов пока нет</h4>
                <p>
                  Статистика появится после того, как студенты начнут проходить модули курса.
                </p>
              </div>
            ) : (
              <div className="students-progress-list">
                {studentsProgress.students.map((student) => (
                  <article className="student-progress-card" key={student.student_id}>
                    <div className="student-progress-main">
                      <div className="student-progress-avatar">
                        {student.avatar_url ? (
                          <img
                            src={
                              student.avatar_url.startsWith("/static")
                                ? `http://127.0.0.1:8000${student.avatar_url}`
                                : student.avatar_url
                            }
                            alt=""
                          />
                        ) : (
                          <span>{student.username?.[0]?.toUpperCase() || "S"}</span>
                        )}
                      </div>

                      <div>
                        <h4>{student.username}</h4>
                        <p>{student.email}</p>
                      </div>
                    </div>

                    <div className="student-progress-bar-wrap">
                      <div className="student-progress-bar-head">
                        <span>
                          Пройдено модулей: {student.completed_modules}/
                          {student.total_modules}
                        </span>
                        <b>{student.progress_percent}%</b>
                      </div>

                      <div className="student-progress-bar">
                        <div
                          style={{ width: `${student.progress_percent}%` }}
                        />
                      </div>
                    </div>

                    {student.last_attempt ? (
                      <div className="student-progress-last">
                        <strong>Последняя попытка</strong>
                        <span>
                          Балл: {student.last_attempt.score} ·{" "}
                          {student.last_attempt.is_passed ? "пройдено" : "не пройдено"}
                        </span>
                      </div>
                    ) : (
                      <div className="student-progress-last">
                        <strong>Попыток пока нет</strong>
                      </div>
                    )}

                    <div className="student-weak-concepts">
                      <strong>Слабые концепты</strong>

                      {student.weak_concepts?.length > 0 ? (
                        <div>
                          {student.weak_concepts.map((concept) => (
                            <span key={concept.id}>
                              {concept.name} · {concept.error_count}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p>Слабых концептов пока нет.</p>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CourseEditorModal;
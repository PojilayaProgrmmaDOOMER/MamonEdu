import { api } from "./client";

export async function getOntologyGraph(courseId = null) {
  const response = await api.get("/ontology/graph", {
    params: courseId ? { course_id: courseId } : {},
  });

  return response.data;
}

export async function getOntologyConcepts() {
  const response = await api.get("/ontology/concepts");
  return response.data;
}

export async function createOntologyConcept(data) {
  const response = await api.post("/ontology/concepts", data);
  return response.data;
}

export async function getOntologyRelations() {
  const response = await api.get("/ontology/relations");
  return response.data;
}

export async function createOntologyRelation(data) {
  const response = await api.post("/ontology/relations", data);
  return response.data;
}

export async function createOntologyEntity(data) {
  const response = await api.post("/ontology/entities", data);
  return response.data;
}

export async function updateOntologyEntity(entityId, data) {
  const response = await api.put(`/ontology/entities/${entityId}`, data);
  return response.data;
}

export async function deleteOntologyEntity(entityId) {
  const response = await api.delete(`/ontology/entities/${entityId}`);
  return response.data;
}

export async function createOntologyGraphRelation(data) {
  const response = await api.post("/ontology/graph-relations", data);
  return response.data;
}

export async function deleteOntologyGraphRelation(relationId) {
  const response = await api.delete(`/ontology/graph-relations/${relationId}`);
  return response.data;
}

export async function getOntologyEntityTypes(courseId = null) {
  const response = await api.get("/ontology/entity-types", {
    params: courseId ? { course_id: courseId } : {},
  });

  return response.data;
}

export async function createOntologyEntityType(data) {
  const response = await api.post("/ontology/entity-types", data);
  return response.data;
}

export async function updateOntologyEntityType(typeId, data) {
  const response = await api.put(`/ontology/entity-types/${typeId}`, data);
  return response.data;
}

export async function deleteOntologyEntityType(typeId) {
  const response = await api.delete(`/ontology/entity-types/${typeId}`);
  return response.data;
}

export async function getCourses() {
  const response = await api.get("/ontology/courses");
  return response.data;
}

export async function createCourse(data) {
  const response = await api.post("/ontology/courses", data);
  return response.data;
}

export async function updateCourse(courseId, data) {
  const response = await api.put(`/ontology/courses/${courseId}`, data);
  return response.data;
}

export async function deleteCourse(courseId) {
  const response = await api.delete(`/ontology/courses/${courseId}`);
  return response.data;
}

export async function getCourseStudents(courseId) {
  const response = await api.get(`/ontology/courses/${courseId}/students`);
  return response.data;
}

export async function addStudentToCourse(courseId, studentId) {
  const response = await api.post(`/ontology/courses/${courseId}/students`, {
    student_id: Number(studentId),
  });
  return response.data;
}

export async function removeStudentFromCourse(courseId, studentId) {
  const response = await api.delete(
    `/ontology/courses/${courseId}/students/${studentId}`
  );
  return response.data;
}

export async function addStudentToCourseByUsername(courseId, username) {
  const response = await api.post(
    `/ontology/courses/${courseId}/students/by-username`,
    {
      username,
    }
  );

  return response.data;
}

export async function getCourseModules(courseId) {
  const response = await api.get(`/ontology/courses/${courseId}/modules`);
  return response.data;
}

export async function createCourseModule(courseId, data) {
  const response = await api.post(`/ontology/courses/${courseId}/modules`, data);
  return response.data;
}

export async function updateCourseModule(courseId, moduleId, data) {
  const response = await api.put(
    `/ontology/courses/${courseId}/modules/${moduleId}`,
    data
  );
  return response.data;
}

export async function deleteCourseModule(courseId, moduleId) {
  const response = await api.delete(
    `/ontology/courses/${courseId}/modules/${moduleId}`
  );
  return response.data;
}

export async function publishCourse(courseId) {
  const response = await api.post(`/ontology/courses/${courseId}/publish`);
  return response.data;
}

export async function unpublishCourse(courseId) {
  const response = await api.post(`/ontology/courses/${courseId}/unpublish`);
  return response.data;
}

export async function getModuleLectures(courseId, moduleId) {
  const response = await api.get(
    `/ontology/courses/${courseId}/modules/${moduleId}/lectures`
  );
  return response.data;
}

export async function createModuleLecture(courseId, moduleId, data) {
  const response = await api.post(
    `/ontology/courses/${courseId}/modules/${moduleId}/lectures`,
    data
  );
  return response.data;
}

export async function updateModuleLecture(courseId, moduleId, lectureId, data) {
  const response = await api.put(
    `/ontology/courses/${courseId}/modules/${moduleId}/lectures/${lectureId}`,
    data
  );
  return response.data;
}

export async function deleteModuleLecture(courseId, moduleId, lectureId) {
  const response = await api.delete(
    `/ontology/courses/${courseId}/modules/${moduleId}/lectures/${lectureId}`
  );
  return response.data;
}

export async function uploadLectureImage(lectureId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    `/ontology/lectures/${lectureId}/image`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

export async function getLectureBlocks(lectureId) {
  const response = await api.get(`/ontology/lectures/${lectureId}/blocks`);
  return response.data;
}

export async function createLectureBlock(lectureId, data) {
  const response = await api.post(`/ontology/lectures/${lectureId}/blocks`, data);
  return response.data;
}

export async function updateLectureBlock(lectureId, blockId, data) {
  const response = await api.put(
    `/ontology/lectures/${lectureId}/blocks/${blockId}`,
    data
  );
  return response.data;
}

export async function deleteLectureBlock(lectureId, blockId) {
  const response = await api.delete(
    `/ontology/lectures/${lectureId}/blocks/${blockId}`
  );
  return response.data;
}

export async function uploadLectureBlockImage(lectureId, blockId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    `/ontology/lectures/${lectureId}/blocks/${blockId}/image`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

export async function getCourseQuestionBank(courseId) {
  const response = await api.get(`/ontology/courses/${courseId}/question-bank`);
  return response.data;
}

export async function createCourseQuestion(courseId, data) {
  const response = await api.post(
    `/ontology/courses/${courseId}/question-bank`,
    data
  );
  return response.data;
}

export async function updateCourseQuestion(courseId, questionId, data) {
  const response = await api.put(
    `/ontology/courses/${courseId}/question-bank/${questionId}`,
    data
  );
  return response.data;
}

export async function deleteCourseQuestion(courseId, questionId) {
  const response = await api.delete(
    `/ontology/courses/${courseId}/question-bank/${questionId}`
  );
  return response.data;
}

export async function getQuestionOptions(questionId) {
  const response = await api.get(`/ontology/question-bank/${questionId}/options`);
  return response.data;
}

export async function createQuestionOption(questionId, data) {
  const response = await api.post(
    `/ontology/question-bank/${questionId}/options`,
    data
  );
  return response.data;
}

export async function deleteQuestionOption(questionId, optionId) {
  const response = await api.delete(
    `/ontology/question-bank/${questionId}/options/${optionId}`
  );
  return response.data;
}

export async function getQuestionConcepts(questionId) {
  const response = await api.get(`/ontology/question-bank/${questionId}/concepts`);
  return response.data;
}

export async function addQuestionConcept(questionId, entityId) {
  const response = await api.post(`/ontology/question-bank/${questionId}/concepts`, {
    entity_id: Number(entityId),
  });
  return response.data;
}

export async function deleteQuestionConcept(questionId, entityId) {
  const response = await api.delete(
    `/ontology/question-bank/${questionId}/concepts/${entityId}`
  );
  return response.data;
}

export async function getCoursePracticalBank(courseId) {
  const response = await api.get(`/ontology/courses/${courseId}/practical-bank`);
  return response.data;
}

export async function createCoursePractical(courseId, data) {
  const response = await api.post(
    `/ontology/courses/${courseId}/practical-bank`,
    data
  );
  return response.data;
}

export async function updateCoursePractical(courseId, taskId, data) {
  const response = await api.put(
    `/ontology/courses/${courseId}/practical-bank/${taskId}`,
    data
  );
  return response.data;
}

export async function deleteCoursePractical(courseId, taskId) {
  const response = await api.delete(
    `/ontology/courses/${courseId}/practical-bank/${taskId}`
  );
  return response.data;
}

export async function getPracticalConcepts(taskId) {
  const response = await api.get(`/ontology/practical-bank/${taskId}/concepts`);
  return response.data;
}

export async function addPracticalConcept(taskId, entityId) {
  const response = await api.post(`/ontology/practical-bank/${taskId}/concepts`, {
    entity_id: Number(entityId),
  });
  return response.data;
}

export async function deletePracticalConcept(taskId, entityId) {
  const response = await api.delete(
    `/ontology/practical-bank/${taskId}/concepts/${entityId}`
  );
  return response.data;
}

export async function getModuleTestSettings(courseId, moduleId) {
  const response = await api.get(
    `/ontology/courses/${courseId}/modules/${moduleId}/test-settings`
  );
  return response.data;
}

export async function createModuleTestSettings(courseId, moduleId, data) {
  const response = await api.post(
    `/ontology/courses/${courseId}/modules/${moduleId}/test-settings`,
    data
  );
  return response.data;
}

export async function updateModuleTestSettings(courseId, moduleId, data) {
  const response = await api.put(
    `/ontology/courses/${courseId}/modules/${moduleId}/test-settings`,
    data
  );
  return response.data;
}

export async function getModuleTestConcepts(courseId, moduleId) {
  const response = await api.get(
    `/ontology/courses/${courseId}/modules/${moduleId}/test-concepts`
  );
  return response.data;
}

export async function addModuleTestConcept(courseId, moduleId, entityId) {
  const response = await api.post(
    `/ontology/courses/${courseId}/modules/${moduleId}/test-concepts`,
    {
      entity_id: Number(entityId),
    }
  );
  return response.data;
}

export async function deleteModuleTestConcept(courseId, moduleId, entityId) {
  const response = await api.delete(
    `/ontology/courses/${courseId}/modules/${moduleId}/test-concepts/${entityId}`
  );
  return response.data;
}

export async function generateModuleTest(courseId, moduleId) {
  const response = await api.post(
    `/ontology/courses/${courseId}/modules/${moduleId}/generate-test`
  );
  return response.data;
}

export async function getModuleTestAttempt(attemptId) {
  const response = await api.get(`/ontology/module-test-attempts/${attemptId}`);
  return response.data;
}

export async function submitModuleTestAttempt(attemptId, data) {
  const response = await api.post(
    `/ontology/module-test-attempts/${attemptId}/submit`,
    data
  );
  return response.data;
}

export async function createAdaptiveRetry(attemptId) {
  const response = await api.post(
    `/ontology/module-test-attempts/${attemptId}/adaptive-retry`
  );
  return response.data;
}

export async function getCourseModuleProgress(courseId) {
  const response = await api.get(`/ontology/courses/${courseId}/modules/progress`);
  return response.data;
}


export async function uploadCourseCover(courseId, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    `/ontology/courses/${courseId}/cover`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

export async function getMaterialSearchProfiles(courseId) {
  const response = await api.get("/material-search/profiles", {
    params: { course_id: courseId },
  });
  return response.data;
}

export async function createMaterialSearchProfile(data) {
  const response = await api.post("/material-search/profiles", data);
  return response.data;
}

export async function runMaterialSearchProfile(profileId) {
  const response = await api.post(`/material-search/profiles/${profileId}/run`);
  return response.data;
}

export async function getMaterialCandidates(courseId) {
  const response = await api.get("/material-search/candidates", {
    params: { course_id: courseId },
  });
  return response.data;
}

export async function approveMaterialCandidate(candidateId, data = {}) {
  const response = await api.post(
    `/material-search/candidates/${candidateId}/approve`,
    data
  );
  return response.data;
}

export async function rejectMaterialCandidate(candidateId) {
  const response = await api.post(
    `/material-search/candidates/${candidateId}/reject`
  );
  return response.data;
}

export async function deleteMaterialSearchProfile(profileId) {
  const response = await api.delete(`/material-search/profiles/${profileId}`);
  return response.data;
}

export async function clearMaterialCandidates(courseId) {
  const response = await api.delete("/material-search/candidates", {
    params: { course_id: courseId },
  });
  return response.data;
}

export async function getCourseMaterials(courseId) {
  const response = await api.get(`/ontology/courses/${courseId}/materials`);
  return response.data;
}

export async function deleteCourseMaterial(materialId) {
  const response = await api.delete(`/ontology/materials/${materialId}`);
  return response.data;
}

export async function createCourseMaterial(courseId, data) {
  const response = await api.post(`/ontology/courses/${courseId}/materials`, data);
  return response.data;
}

export async function getCourseStudentsProgress(courseId) {
  const response = await api.get(
    `/ontology/courses/${courseId}/students-progress`
  );

  return response.data;
}

export async function downloadCourseCertificate(courseId) {
  const response = await api.get(
    `/ontology/courses/${courseId}/certificate`,
    {
      responseType: "blob",
    }
  );

  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");

  link.href = url;
  link.setAttribute("download", `certificate_course_${courseId}.png`);

  document.body.appendChild(link);
  link.click();

  link.remove();
  window.URL.revokeObjectURL(url);
}
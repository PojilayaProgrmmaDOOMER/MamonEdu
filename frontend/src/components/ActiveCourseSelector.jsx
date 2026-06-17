import { useEffect, useState } from "react";

import { getCourses } from "../api/ontologyApi";

function ActiveCourseSelector() {
  const [courses, setCourses] = useState([]);
  const [activeCourseId, setActiveCourseId] = useState(() => {
    return localStorage.getItem("activeCourseId") || "";
  });

  async function loadCourses() {
    const data = await getCourses();
    setCourses(data);

    if (!localStorage.getItem("activeCourseId") && data.length > 0) {
      const firstId = String(data[0].id);

      localStorage.setItem("activeCourseId", firstId);
      setActiveCourseId(firstId);

      window.dispatchEvent(
        new CustomEvent("activeCourseChanged", {
          detail: firstId,
        })
      );
    }
  }

  useEffect(() => {
    loadCourses();

    function reloadCourses() {
      loadCourses();
    }

    window.addEventListener("coursesChanged", reloadCourses);

    return () => {
      window.removeEventListener("coursesChanged", reloadCourses);
    };
  }, []);

  function handleChange(event) {
    const value = event.target.value;

    setActiveCourseId(value);

    if (value) {
      localStorage.setItem("activeCourseId", value);
    } else {
      localStorage.removeItem("activeCourseId");
    }

    window.dispatchEvent(
      new CustomEvent("activeCourseChanged", {
        detail: value,
      })
    );
  }

  return (
    <div className="active-course-selector">
      <span>Текущий курс</span>

      <select value={activeCourseId} onChange={handleChange}>
        <option value="">Не выбран</option>

        {courses.map((course) => (
          <option value={course.id} key={course.id}>
            {course.title}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ActiveCourseSelector;
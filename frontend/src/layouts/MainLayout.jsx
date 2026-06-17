import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import CourseBuilderModal from "../components/CourseBuilderModal";
import { Outlet } from "react-router-dom";

function MainLayout() {
  const [courseBuilderOpen, setCourseBuilderOpen] = useState(false);

  useEffect(() => {
    function openModal() {
      setCourseBuilderOpen(true);
    }

    window.addEventListener("openCourseBuilder", openModal);

    return () => {
      window.removeEventListener("openCourseBuilder", openModal);
    };
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-area">
        <Header />
        <main className="content">
          <Outlet />
        </main>
      </div>

      <CourseBuilderModal
        open={courseBuilderOpen}
        onClose={() => setCourseBuilderOpen(false)}
      />
    </div>
  );
}

export default MainLayout;
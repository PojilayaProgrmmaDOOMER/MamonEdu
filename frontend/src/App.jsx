import { Routes, Route, Navigate } from "react-router-dom";
import KnowledgeGraphPage from "./pages/KnowledgeGraphPage";
import MainLayout from "./layouts/MainLayout";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import TopicsPage from "./pages/TopicsPage";
import TopicPage from "./pages/TopicPage";
import TestPage from "./pages/TestPage";
import TestResultPage from "./pages/TestResultPage";
import PracticalPage from "./pages/PracticalPage";
import ConceptsPage from "./pages/ConceptsPage";
import CourseLearningPage from "./pages/CourseLearningPage";
import SettingsPage from "./pages/SettingsPage";
import ResultsPage from "./pages/ResultsPage";
function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/topics" element={<TopicsPage />} />
        <Route path="/topics/:id" element={<TopicPage />} />
        <Route path="/tests/:id" element={<TestPage />} />
        <Route path="/tests/result/:attemptId" element={<TestResultPage />} />
        <Route path="/practical/:id" element={<PracticalPage />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
        <Route path="/courses/:courseId/learn" element={<CourseLearningPage />} />
        <Route path="/knowledge-graph/concepts" element={<ConceptsPage />} />
        <Route path="/results" element={<ResultsPage />} />
      </Route>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
import { useEffect, useState } from "react";
import {
  getOntologyConcepts,
  createOntologyConcept,
} from "../api/ontologyApi";

function ConceptsPage() {
  const [concepts, setConcepts] = useState([]);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    name: "",
    description: "",
    concept_type: "Concept",
    difficulty_level: "Medium",
  });

  async function loadConcepts() {
    try {
      const data = await getOntologyConcepts();
      setConcepts(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadConcepts();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();

    await createOntologyConcept(form);

    setForm({
      name: "",
      description: "",
      concept_type: "Concept",
      difficulty_level: "Medium",
    });

    loadConcepts();
  }

  return (
    <div className="concepts-page">
      <div className="concepts-layout">
        <div className="concepts-list">
          <div className="card">
            <h2>Концепты</h2>

            {loading ? (
              <p>Загрузка...</p>
            ) : (
              concepts.map((concept) => (
                <div className="concept-row" key={concept.id}>
                  <strong>{concept.name}</strong>

                  <span>{concept.concept_type}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="concept-editor">
          <div className="card">
            <h2>Создать концепт</h2>

            <form onSubmit={handleSubmit}>
              <label>
                Название

                <input
                  value={form.name}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      name: e.target.value,
                    })
                  }
                />
              </label>

              <label>
                Тип

                <select
                  value={form.concept_type}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      concept_type: e.target.value,
                    })
                  }
                >
                  <option>Concept</option>
                  <option>Architecture</option>
                  <option>Method</option>
                  <option>Dataset</option>
                  <option>Metric</option>
                  <option>Task</option>
                </select>
              </label>

              <label>
                Сложность

                <select
                  value={form.difficulty_level}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      difficulty_level: e.target.value,
                    })
                  }
                >
                  <option>Easy</option>
                  <option>Medium</option>
                  <option>Hard</option>
                </select>
              </label>

              <label>
                Описание

                <textarea
                  rows="5"
                  value={form.description}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      description: e.target.value,
                    })
                  }
                />
              </label>

              <button type="submit">
                Создать концепт
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConceptsPage;
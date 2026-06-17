import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import {
  getOntologyGraph,
  createOntologyEntity,
  updateOntologyEntity,
  deleteOntologyEntity,
  createOntologyGraphRelation,
  deleteOntologyGraphRelation,
  getOntologyEntityTypes,
  createOntologyEntityType,
  updateOntologyEntityType,
  deleteOntologyEntityType,
} from "../api/ontologyApi";
import { getMyProfile } from "../api/userApi";

/* ================================================================
   Динамические цвета
   ================================================================ */
function makeTypeColorMap(entityTypes) {
  const map = { MainConcept: "#9f1239" };
  entityTypes.forEach((type) => {
    map[type.name] = type.color;
  });
  return map;
}

function hexToSoftBackground(hex) {
  if (!hex || !hex.startsWith("#") || hex.length !== 7) return "#f8fafc";
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, 0.10)`;
}

function getNodeColor(type, typeColorMap) {
  return typeColorMap[type] || "#94a3b8";
}

function getNodeBackground(type, typeColorMap) {
  if (type === "MainConcept") return "#9f1239";
  return hexToSoftBackground(typeColorMap[type] || "#94a3b8");
}

/* ================================================================
   Вспомогательные функции
   ================================================================ */
function formatLabel(label) {
  return String(label || "")
    .replace(/([a-zа-я])([A-ZА-Я])/g, "$1 $2")
    .replace(/_/g, " ");
}

function getGroupTitle(type) {
  const titles = {
    Architecture: "Архитектуры",
    Method: "Методы",
    Dataset: "Датасеты",
    Metric: "Метрики",
    Loss: "Функции потерь",
    Task: "Задачи",
    Concept: "Концепты",
    Material: "Материалы",
    Question: "Вопросы",
    Unknown: "Другое",
  };
  return titles[type] || type;
}

/* ================================================================
   Умное размещение узлов внутри одного кластера без пересечений
   ================================================================ */
function getClusterPositions(count, minDistance = 130, firstRadius = 160, step = 140) {
  const positions = [];
  let remaining = count;
  let radius = firstRadius;
  let maxRadius = firstRadius;

  while (remaining > 0) {
    const circumference = 2 * Math.PI * radius;
    const maxOnRing = Math.max(1, Math.floor(circumference / minDistance));
    const nodesOnThisRing = Math.min(remaining, maxOnRing);
    const angleStep = (2 * Math.PI) / nodesOnThisRing;
    const startAngle = -Math.PI / 2;

    for (let i = 0; i < nodesOnThisRing; i++) {
      const angle = startAngle + i * angleStep;
      positions.push({
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
      });
    }

    remaining -= nodesOnThisRing;
    maxRadius = radius;
    radius += step;
  }

  return { positions, maxRadius };
}

/* ================================================================
   Динамическое размещение групп без пересечений (с защитой от NaN)
   ================================================================ */
function computeGroupPositions(groupSizes, centerGap = 40, rootRadius = 85) {
  const N = groupSizes.length;
  if (N === 0) return [];

  if (N === 1) {
    const r = groupSizes[0].r;
    const R = Math.max(rootRadius + r + centerGap, r + 200);
    return [{ angle: 0, R }];
  }

  const maxR = Math.max(...groupSizes.map(g => g.r));
  let R = Math.max(rootRadius + maxR + centerGap, maxR + 200);

  const fits = (R) => {
    let total = 0;
    for (let i = 0; i < N; i++) {
      const r1 = groupSizes[i].r;
      const r2 = groupSizes[(i + 1) % N].r;
      const value = Math.min(0.999, (r1 + r2 + centerGap) / (2 * R));
      total += 2 * Math.asin(value);
    }
    return total <= 2 * Math.PI;
  };

  while (!fits(R)) {
    R += 10;
  }

  let totalNeeded = 0;
  for (let i = 0; i < N; i++) {
    const r1 = groupSizes[i].r;
    const r2 = groupSizes[(i + 1) % N].r;
    const value = Math.min(0.999, (r1 + r2 + centerGap) / (2 * R));
    totalNeeded += 2 * Math.asin(value);
  }
  const extraAngle = (2 * Math.PI - totalNeeded) / N;

  const positions = [];
  let angle = extraAngle / 2;
  for (let i = 0; i < N; i++) {
    positions.push({ angle, R });
    const r1 = groupSizes[i].r;
    const r2 = groupSizes[(i + 1) % N].r;
    const value = Math.min(0.999, (r1 + r2 + centerGap) / (2 * R));
    const needed = 2 * Math.asin(value);
    angle += needed + extraAngle;
  }

  return positions;
}

/* ================================================================
   Построение узла
   ================================================================ */
function createCircleNode(id, label, type, raw, variant = "item", x = 0, y = 0, typeColorMap = {}) {
  const isRoot = variant === "root";
  const isGroup = variant === "group";
  const size = isRoot ? 170 : isGroup ? 120 : 96;
  const color = isRoot ? "#9f1239" : getNodeColor(type, typeColorMap);
  const background = isRoot ? "#9f1239" : getNodeBackground(type, typeColorMap);

  return {
    id,
    position: { x, y },
    connectable: !isRoot && !isGroup,
    data: {
      raw,
      label: (
        <div className={`radial-node radial-node-${variant}`}>
          <strong>{formatLabel(label)}</strong>
          <span>{isGroup ? "Группа" : type}</span>
        </div>
      ),
    },
    style: {
      width: size,
      height: size,
      borderRadius: "50%",
      border: isRoot ? "none" : `3px solid ${color}`,
      background,
      color: isRoot ? "#ffffff" : "#111827",
      boxShadow: "0 10px 26px rgba(15, 23, 42, 0.1)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: 8,
    },
  };
}

/* ================================================================
   Основная раскладка графа
   ================================================================ */
function buildRadialLayout(rawNodes, highlightedNodeId = null, entityTypes = [], rootEntityId = null) {
  if (!rawNodes.length) return { nodes: [], edges: [] };

  const typeColorMap = makeTypeColorMap(entityTypes);

  const mainNode =
    rawNodes.find((node) => String(node.id) === String(rootEntityId)) ||
    rawNodes.find((node) => node.type === "MainConcept") ||
    rawNodes.find((node) => node.label === "ImageSegmentation") ||
    rawNodes[0];

  const grouped = {};
  rawNodes.forEach((node) => {
    if (mainNode && node.id === mainNode.id) return;
    const type = node.type || "Unknown";
    if (!grouped[type]) grouped[type] = [];
    grouped[type].push(node);
  });

  const backendTypeNames = entityTypes.map((type) => type.name);
  const customTypeNames = Object.keys(grouped).filter(
    (type) => !backendTypeNames.includes(type)
  );
  const orderedTypes = [
    ...backendTypeNames.filter((type) => grouped[type]?.length),
    ...customTypeNames,
  ];

  const nodes = [];
  const edges = [];
  const centerX = 2200;
  const centerY = 1600;

  nodes.push(
    createCircleNode(
      "root",
      mainNode.label || "Граф знаний",
      "MainConcept",
      mainNode,
      "root",
      centerX,
      centerY,
      typeColorMap
    )
  );

  const clusterMaxRadii = {};
  orderedTypes.forEach((type) => {
    const group = grouped[type];
    const { maxRadius } = getClusterPositions(group.length);
    clusterMaxRadii[type] = maxRadius;
  });

  const groupSizes = orderedTypes.map((type) => ({
    type,
    r: clusterMaxRadii[type] + 80,
  }));

  const groupPositions = computeGroupPositions(groupSizes, 40, 85);

  orderedTypes.forEach((type, idx) => {
    const { angle, R } = groupPositions[idx];
    const group = grouped[type];
    const groupPosition = {
      x: centerX + Math.cos(angle) * R,
      y: centerY + Math.sin(angle) * R,
    };

    const groupId = `group-${type}`;
    const groupTitle = getGroupTitle(type);

    nodes.push(
      createCircleNode(
        groupId,
        groupTitle,
        type,
        { id: groupId, label: groupTitle, type: "TypeGroup" },
        "group",
        groupPosition.x,
        groupPosition.y,
        typeColorMap
      )
    );

    edges.push({
      id: `root-${groupId}`,
      source: "root",
      target: groupId,
      type: "straight",
      style: { stroke: "#64748b", strokeWidth: 1.8 },
      markerEnd: { type: MarkerType.ArrowClosed },
    });

    const { positions: itemPositions } = getClusterPositions(group.length);
    group.forEach((item, itemIndex) => {
      const pos = itemPositions[itemIndex];
      const itemPosition = {
        x: groupPosition.x + pos.x,
        y: groupPosition.y + pos.y,
      };

      const itemId = String(item.id);
      const node = createCircleNode(
        itemId,
        item.label,
        item.type || "Unknown",
        item,
        "item",
        itemPosition.x,
        itemPosition.y,
        typeColorMap
      );

      if (String(highlightedNodeId) === itemId) {
        node.className = "highlighted-ontology-node";
        node.style = {
          ...node.style,
          boxShadow:
            "0 0 0 14px rgba(245, 197, 66, 0.55), 0 0 90px rgba(245, 197, 66, 1)",
          border: "5px solid #f5c542",
          zIndex: 50,
        };
      }

      nodes.push(node);

      edges.push({
        id: `${groupId}-${itemId}`,
        source: groupId,
        target: itemId,
        type: "straight",
        style: {
          stroke: getNodeColor(type, typeColorMap),
          strokeWidth: 1.35,
          opacity: 0.55,
        },
        markerEnd: { type: MarkerType.ArrowClosed },
      });
    });
  });

  return { nodes, edges };
}

/* ================================================================
   Компонент KnowledgeGraphPage
   ================================================================ */
function KnowledgeGraphPage() {
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState("graph");

  const [conceptForm, setConceptForm] = useState({
    name: "",
    description: "",
    concept_type: "Concept",
    difficulty_level: "Medium",
  });

  const [savingConcept, setSavingConcept] = useState(false);
  const [highlightedNodeId, setHighlightedNodeId] = useState(null);

  const [pendingConnection, setPendingConnection] = useState(null);
  const [relationType, setRelationType] = useState("related_to");
  const [showRelationModal, setShowRelationModal] = useState(false);
  const [savingRelation, setSavingRelation] = useState(false);

  const [editingEntity, setEditingEntity] = useState(null);
  const [editForm, setEditForm] = useState({
    name: "",
    entity_type: "Concept",
    description: "",
  });
  const [savingEdit, setSavingEdit] = useState(false);

  const [entityTypes, setEntityTypes] = useState([]);
  const [newType, setNewType] = useState({ name: "", color: "#f59e0b" });
  const [editingType, setEditingType] = useState(null);
  const [editTypeForm, setEditTypeForm] = useState({ name: "", color: "#f59e0b" });

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const [rootEntityId, setRootEntityId] = useState(() => {
    return localStorage.getItem("ontologyRootEntityId");
  });

  const [activeCourseId, setActiveCourseId] = useState(() => {
    return localStorage.getItem("activeCourseId") || "";
  });

  const [user, setUser] = useState(null);

  const typeColorMap = useMemo(() => makeTypeColorMap(entityTypes), [entityTypes]);

  const canEditGraph = user?.role === "teacher" || user?.role === "admin";

  async function loadGraph() {
    try {
      if (!activeCourseId) {
        setGraph({ nodes: [], edges: [] });
        return { nodes: [], edges: [] };
      }

      const data = await getOntologyGraph(activeCourseId);
      setGraph(data);
      return data;
    } finally {
      setLoading(false);
    }
  }

  async function loadEntityTypes() {
    try {
      if (!activeCourseId) {
        setEntityTypes([]);
        return;
      }
      const data = await getOntologyEntityTypes(activeCourseId);
      setEntityTypes(data);
    } catch (error) {
      console.error("Ошибка загрузки типов сущностей:", error);
    }
  }

  useEffect(() => {
    async function init() {
      try {
        const profile = await getMyProfile();
        setUser(profile);
      } catch (error) {
        console.error("Ошибка загрузки профиля:", error);
      }

      await loadGraph();
      await loadEntityTypes();
    }

    init();
  }, []);

  useEffect(() => {
    function handleCourseChange(event) {
      setActiveCourseId(event.detail || "");
      setSelectedNode(null);
      setSearch("");
    }

    window.addEventListener("activeCourseChanged", handleCourseChange);
    return () => {
      window.removeEventListener("activeCourseChanged", handleCourseChange);
    };
  }, []);

  useEffect(() => {
    loadGraph();
    loadEntityTypes();
  }, [activeCourseId]);

  // ---------- Работа с типами ----------
  async function handleCreateEntityType(event) {
    event.preventDefault();
    if (!canEditGraph) return;
    if (!newType.name.trim()) return;
    await createOntologyEntityType({
      ...newType,
      course_id: activeCourseId ? Number(activeCourseId) : null,
    });
    setNewType({ name: "", color: "#f59e0b" });
    await loadEntityTypes();
  }

  async function handleUpdateEntityType(event) {
    event.preventDefault();
    if (!canEditGraph) return;
    if (!editingType || !editTypeForm.name.trim()) return;
    await updateOntologyEntityType(editingType.id, {
      ...editTypeForm,
      course_id: activeCourseId ? Number(activeCourseId) : null,
    });
    setEditingType(null);
    setEditTypeForm({ name: "", color: "#f59e0b" });
    await loadEntityTypes();
    await loadGraph();
  }

  async function handleDeleteEntityType(typeId) {
    if (!canEditGraph) return;
    const confirmed = window.confirm(
      "Удалить тип сущности? Если он используется в графе, backend не даст его удалить."
    );
    if (!confirmed) return;
    await deleteOntologyEntityType(typeId);
    await loadEntityTypes();
  }

  // ---------- Концепты ----------
  async function handleCreateConcept(event) {
    event.preventDefault();
    if (!canEditGraph) return;
    if (!conceptForm.name.trim()) return;
    setSavingConcept(true);
    try {
      const createdEntity = await createOntologyEntity({
        name: conceptForm.name,
        entity_type: conceptForm.concept_type,
        description: conceptForm.description,
        course_id: activeCourseId ? Number(activeCourseId) : null,
      });
      setConceptForm({
        name: "",
        description: "",
        concept_type: "Concept",
        difficulty_level: "Medium",
      });
      setSearch("");
      await loadGraph();
      setActiveTab("graph");
      setHighlightedNodeId(createdEntity.id);
      setTimeout(() => setHighlightedNodeId(null), 5000);
    } finally {
      setSavingConcept(false);
    }
  }

  async function handleDeleteConcept(entityId) {
    if (!canEditGraph) return;
    const isConfirmed = window.confirm(
      "Удалить концепт? Вместе с ним могут исчезнуть связанные отношения."
    );
    if (!isConfirmed) return;
    await deleteOntologyEntity(entityId);
    if (selectedNode?.id === entityId) setSelectedNode(null);
    await loadGraph();
  }

  function handleEditClick(node) {
    setEditingEntity(node);
    setEditForm({
      name: node.label || "",
      entity_type: node.type || "Concept",
      description: node.description || "",
    });
  }

  function handleEditCancel() {
    setEditingEntity(null);
  }

  async function handleEditSave(event) {
    event.preventDefault();
    if (!canEditGraph) return;
    if (!editingEntity || !editForm.name.trim()) return;
    setSavingEdit(true);
    try {
      await updateOntologyEntity(editingEntity.id, {
        name: editForm.name,
        entity_type: editForm.entity_type,
        description: editForm.description,
      });
      setEditingEntity(null);
      await loadGraph();
    } catch (error) {
      console.error("Ошибка обновления сущности:", error);
    } finally {
      setSavingEdit(false);
    }
  }

  // ---------- Связи ----------
  async function handleCreateRelation() {
    if (!canEditGraph) return;
    if (!pendingConnection) return;
    const sourceId = Number(pendingConnection.source);
    const targetId = Number(pendingConnection.target);
    if (!sourceId || !targetId || sourceId === targetId) {
      setShowRelationModal(false);
      setPendingConnection(null);
      return;
    }
    setSavingRelation(true);
    try {
      await createOntologyGraphRelation({
        source_entity_id: sourceId,
        target_entity_id: targetId,
        relation_type: relationType,
        course_id: activeCourseId ? Number(activeCourseId) : null,
      });
      setShowRelationModal(false);
      setPendingConnection(null);
      setRelationType("related_to");
      await loadGraph();
      setHighlightedNodeId(targetId);
      setTimeout(() => setHighlightedNodeId(null), 5000);
    } finally {
      setSavingRelation(false);
    }
  }

  function cancelRelationModal() {
    setShowRelationModal(false);
    setPendingConnection(null);
    setRelationType("related_to");
  }

  async function handleDeleteRelation(relationId) {
    if (!canEditGraph) return;
    const confirmed = window.confirm("Удалить связь?");
    if (!confirmed) return;
    try {
      await deleteOntologyGraphRelation(relationId);
      setGraph((prev) => ({
        ...prev,
        edges: prev.edges.filter(
          (edge) => String(edge.id) !== String(relationId)
        ),
      }));
      await loadGraph();
    } catch (error) {
      console.error(error);
      await loadGraph();
    }
  }

  function handleSetRootEntity(node) {
    if (!canEditGraph) return;
    const id = String(node.id);
    setRootEntityId(id);
    localStorage.setItem("ontologyRootEntityId", id);
    setSelectedNode(node);
    setHighlightedNodeId(node.id);
    setTimeout(() => setHighlightedNodeId(null), 5000);
  }

  /* ---------- Мемоизированные данные ---------- */
  const nodeMap = useMemo(() => {
    const map = {};
    graph.nodes.forEach((node) => {
      map[String(node.id)] = node.label;
    });
    return map;
  }, [graph.nodes]);

  const filteredNodes = useMemo(() => {
    if (!search.trim()) return graph.nodes;
    return graph.nodes.filter((node) =>
      node.label.toLowerCase().includes(search.toLowerCase())
    );
  }, [graph.nodes, search]);

  useEffect(() => {
    const layouted = buildRadialLayout(
      graph.nodes,
      highlightedNodeId,
      entityTypes,
      rootEntityId
    );
    setNodes(layouted.nodes);
    setEdges(layouted.edges);
  }, [graph.nodes, highlightedNodeId, entityTypes, rootEntityId, setNodes, setEdges]);

  const selectedRelations = useMemo(() => {
    if (!selectedNode || selectedNode.type === "TypeGroup") return [];
    return graph.edges.filter(
      (edge) =>
        String(edge.source) === String(selectedNode.id) ||
        String(edge.target) === String(selectedNode.id)
    );
  }, [selectedNode, graph.edges]);

  const visibleRelationEdges = useMemo(() => {
    if (!selectedNode || selectedNode.type === "TypeGroup") return [];
    return graph.edges
      .filter(
        (edge) =>
          String(edge.source) === String(selectedNode.id) ||
          String(edge.target) === String(selectedNode.id)
      )
      .map((edge) => ({
        id: `selected-relation-${edge.id}`,
        source: String(edge.source),
        target: String(edge.target),
        type: "straight",
        label: edge.label,
        animated: false,
        style: {
          stroke: "#7c3aed",
          strokeWidth: 2,
          strokeDasharray: "7 6",
        },
        labelStyle: { fill: "#4c1d95", fontSize: 12, fontWeight: 700 },
        markerEnd: { type: MarkerType.ArrowClosed },
      }));
  }, [selectedNode, graph.edges]);

  const filteredRelations = useMemo(() => {
    if (!search.trim()) return graph.edges;
    const q = search.toLowerCase();
    return graph.edges.filter((edge) => {
      const source = nodeMap[String(edge.source)] || "";
      const target = nodeMap[String(edge.target)] || "";
      return (
        edge.label?.toLowerCase().includes(q) ||
        source.toLowerCase().includes(q) ||
        target.toLowerCase().includes(q)
      );
    });
  }, [graph.edges, nodeMap, search]);

  if (loading) return <p>Загрузка графа знаний...</p>;

  return (
    <div className="ontology-page">
      <div className="ontology-tabs">
        <button className={activeTab === "graph" ? "active" : ""} onClick={() => setActiveTab("graph")}>Граф знаний</button>
        {canEditGraph && (
          <>
            <button
              className={activeTab === "concepts" ? "active" : ""}
              onClick={() => setActiveTab("concepts")}
            >
              Концепты
            </button>

            <button
              className={activeTab === "relations" ? "active" : ""}
              onClick={() => setActiveTab("relations")}
            >
              Отношения
            </button>

            <button
              className={activeTab === "types" ? "active" : ""}
              onClick={() => setActiveTab("types")}
            >
              Типы сущностей
            </button>
          </>
        )}
      </div>

      <div className="ontology-toolbar">
        {(activeTab === "concepts" || activeTab === "relations") ? (
          <input value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder={activeTab === "relations" ? "Поиск отношений..." : "Поиск концептов..."} />
        ) : <div />}
        <div className="graph-stats">
          <span>{graph.nodes.length} узлов</span>
          <span>{graph.edges.length} связей</span>
        </div>
      </div>

      {/* Вкладка ГРАФ */}
      {activeTab === "graph" && (
        <div className="ontology-workspace">
          <div className="ontology-legend">
            <h4>Типы сущностей</h4>
            {entityTypes.map((type) => (
              <div className="legend-row" key={type.id}>
                <span style={{ background: type.color }}></span>
                {type.name}
              </div>
            ))}
            {canEditGraph && (
              <>
                <hr />
                <h4>Редактирование</h4>
                <p className="legend-note">
                  Потяните стрелку от одного узла к другому, чтобы создать связь.
                </p>
                <hr />
              </>
            )}
            <h4>Типы связей</h4>
            <div className="relation-legend">
              <div><span className="line main-line"></span> содержит</div>
              <div><span className="line purple-line"></span> принадлежит группе</div>
              <div><span className="line selected-line"></span> связь выбранного узла</div>
            </div>
          </div>

          <div className="ontology-canvas">
            <ReactFlow
              nodes={nodes}
              edges={[...edges, ...visibleRelationEdges]}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={
                canEditGraph
                  ? (params) => {
                      if (
                        !params.source ||
                        !params.target ||
                        params.source === params.target ||
                        params.source.startsWith("group-") ||
                        params.target.startsWith("group-") ||
                        params.source === "root" ||
                        params.target === "root"
                      )
                        return;

                      setPendingConnection(params);
                      setShowRelationModal(true);
                    }
                  : undefined
              }
              onNodeClick={(_, node) => setSelectedNode(node.data.raw)}
              fitView
              minZoom={0.06}
              maxZoom={1.6}
              nodesConnectable={canEditGraph}
              elementsSelectable
            >
              <Background gap={18} size={1} color="#dbe3ef" />
              <Controls />
              <MiniMap />
            </ReactFlow>
          </div>

          <aside className="concept-panel">
            {selectedNode ? (
              <>
                <div className="concept-panel-header">
                  <h3>Информация о концепте</h3>
                  <button onClick={() => setSelectedNode(null)}>×</button>
                </div>
                <div className="concept-title">
                  <span style={{ background: getNodeColor(selectedNode.type, typeColorMap) }} />
                  <strong>{selectedNode.label}</strong>
                </div>
                <p><b>ID:</b> {selectedNode.id}</p>
                <p><b>Тип:</b> {selectedNode.type}</p>
                <p>
                  <b>Описание:</b> {selectedNode.description || "Описание не указано."}
                </p>

                {String(rootEntityId) === String(selectedNode.id) ? (
                  <p className="root-node-badge">Корневой узел графа</p>
                ) : (
                  canEditGraph && (
                    <button
                      type="button"
                      onClick={() => handleSetRootEntity(selectedNode)}
                    >
                      Сделать корневым узлом
                    </button>
                  )
                )}

                <hr />
                <h4>Связанные отношения ({selectedRelations.length})</h4>
                {selectedRelations.length > 0 ? (
                  selectedRelations.map((relation) => (
                    <div className="relation-item" key={relation.id}>
                      <strong>{relation.label}</strong>
                      <small className="relation-path">
                        <span>{nodeMap[String(relation.source)] || relation.source}</span>
                        <span>→</span>
                        <span>{nodeMap[String(relation.target)] || relation.target}</span>
                      </small>
                    </div>
                  ))
                ) : <p>Связей нет.</p>}
              </>
            ) : (
              <div className="empty-panel">
                <h3>Информация о концепте</h3>
                <p>Нажмите на узел графа, чтобы увидеть детали.</p>
              </div>
            )}
          </aside>
        </div>
      )}

      {/* Вкладка КОНЦЕПТЫ */}
      {activeTab === "concepts" && (
        <div className="ontology-editor-layout">
          <div className="ontology-table-card">
            <div className="editor-head">
              <div>
                <h3>Концепты и сущности</h3>
                <p>Список понятий, которые входят в онтологию предметной области.</p>
              </div>
            </div>
            <div className="concept-grid">
              {filteredNodes.map((node) => (
                <div className="concept-card" key={node.id}>
                  <div className="concept-card-header">
                    <span style={{ background: getNodeColor(node.type, typeColorMap) }} />
                    <strong>{node.label}</strong>
                  </div>
                  <p>{node.description || "Описание не указано."}</p>
                  <small>ID: {node.id}</small>
                  <small>Тип: {node.type || "Unknown"}</small>
                  {node.type !== "MainConcept" && (
                    <div className="concept-card-actions">
                      <button type="button" className="edit-btn" onClick={() => handleEditClick(node)}>Редактировать</button>
                      <button type="button" className="danger-btn" onClick={() => handleDeleteConcept(node.id)}>Удалить</button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <form className="ontology-form-card" onSubmit={handleCreateConcept}>
            <h3>Новый концепт</h3>
            <p>Добавьте понятие в онтологию. После создания граф знаний обновится автоматически.</p>
            <label>
              Название
              <input value={conceptForm.name} onChange={(e) => setConceptForm({ ...conceptForm, name: e.target.value })} placeholder="Например: U-Net" required />
            </label>
            <label>
              Тип
              <select value={conceptForm.concept_type} onChange={(e) => setConceptForm({ ...conceptForm, concept_type: e.target.value })}>
                {entityTypes.map((type) => (
                  <option value={type.name} key={type.id}>{type.name}</option>
                ))}
              </select>
            </label>
            <label>
              Сложность
              <select value={conceptForm.difficulty_level} onChange={(e) => setConceptForm({ ...conceptForm, difficulty_level: e.target.value })}>
                <option value="beginner">beginner</option>
                <option value="intermediate">intermediate</option>
                <option value="advanced">advanced</option>
                <option value="Medium">Medium</option>
              </select>
            </label>
            <label>
              Описание
              <textarea rows="6" value={conceptForm.description} onChange={(e) => setConceptForm({ ...conceptForm, description: e.target.value })} placeholder="Краткое описание концепта..." />
            </label>
            <button type="submit" disabled={savingConcept}>
              {savingConcept ? "Создание..." : "Создать концепт"}
            </button>
          </form>
        </div>
      )}

      {/* Вкладка ОТНОШЕНИЯ */}
      {activeTab === "relations" && (
        <div className="ontology-table-card">
          <h3>Отношения между сущностями</h3>
          <div className="relations-list">
            {filteredRelations.map((relation) => (
              <div className="relation-row" key={relation.id}>
                <span>{nodeMap[String(relation.source)] || relation.source}</span>
                <strong>{relation.label}</strong>
                <span>{nodeMap[String(relation.target)] || relation.target}</span>
                <button type="button" className="danger-small-btn" onClick={() => handleDeleteRelation(relation.id)}>Удалить</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Вкладка ТИПЫ СУЩНОСТЕЙ */}
      {activeTab === "types" && (
        <div className="ontology-table-card">
          <h3>Управление типами сущностей</h3>
          <form className="entity-type-form" onSubmit={handleCreateEntityType}>
            <input placeholder="Название типа" value={newType.name} onChange={(e) => setNewType({ ...newType, name: e.target.value })} required />
            <input type="color" value={newType.color} onChange={(e) => setNewType({ ...newType, color: e.target.value })} />
            <button type="submit">Создать тип</button>
          </form>

          <div className="type-grid">
            {entityTypes.map((type) => (
              <div className="type-card" key={type.id}>
                <span style={{ background: type.color }} />
                <strong>{type.name}</strong>
                <p>{type.color}</p>
                <button type="button" className="edit-btn" onClick={() => { setEditingType(type); setEditTypeForm({ name: type.name, color: type.color }); }}>Редактировать</button>
                <button type="button" className="danger-small-btn" onClick={() => handleDeleteEntityType(type.id)}>Удалить</button>
              </div>
            ))}
          </div>

          {editingType && (
            <div className="relation-modal-overlay">
              <form className="relation-modal" onSubmit={handleUpdateEntityType}>
                <h3>Редактировать тип</h3>
                <label>
                  Название
                  <input value={editTypeForm.name} onChange={(e) => setEditTypeForm({ ...editTypeForm, name: e.target.value })} required />
                </label>
                <label>
                  Цвет
                  <input type="color" value={editTypeForm.color} onChange={(e) => setEditTypeForm({ ...editTypeForm, color: e.target.value })} />
                </label>
                <div className="modal-buttons">
                  <button type="button" onClick={() => setEditingType(null)}>Отмена</button>
                  <button type="submit">Сохранить</button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* Модальное окно редактирования концепта */}
      {editingEntity && (
        <div className="relation-modal-overlay">
          <div className="relation-modal">
            <h3>Редактировать концепт</h3>
            <form onSubmit={handleEditSave}>
              <label>
                Название
                <input value={editForm.name} onChange={(e) => setEditForm({ ...editForm, name: e.target.value })} required />
              </label>
              <label>
                Тип
                <select value={editForm.entity_type} onChange={(e) => setEditForm({ ...editForm, entity_type: e.target.value })}>
                  {entityTypes.map((type) => (
                    <option value={type.name} key={type.id}>{type.name}</option>
                  ))}
                </select>
              </label>
              <label>
                Описание
                <textarea rows="4" value={editForm.description} onChange={(e) => setEditForm({ ...editForm, description: e.target.value })} placeholder="Описание концепта..." />
              </label>
              <div className="modal-buttons">
                <button type="button" onClick={handleEditCancel}>Отмена</button>
                <button type="submit" disabled={savingEdit}>
                  {savingEdit ? "Сохранение..." : "Сохранить изменения"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Модальное окно создания связи */}
      {showRelationModal && (
        <div className="relation-modal-overlay">
          <div className="relation-modal">
            <h3>Создать связь</h3>
            <div className="relation-preview">
              <strong>{nodeMap[pendingConnection?.source]}</strong>
              <span>→</span>
              <strong>{nodeMap[pendingConnection?.target]}</strong>
            </div>
            <label>
              Тип связи
              <select value={relationType} onChange={(e) => setRelationType(e.target.value)}>
                <option value="related_to">related_to</option>
                <option value="requires">requires</option>
                <option value="required_for">required_for</option>
                <option value="part_of">part_of</option>
                <option value="used_in">used_in</option>
                <option value="contains">contains</option>
                <option value="checks">checks</option>
              </select>
            </label>
            <div className="modal-buttons">
              <button type="button" onClick={cancelRelationModal}>Отмена</button>
              <button type="button" onClick={handleCreateRelation} disabled={savingRelation}>
                {savingRelation ? "Создание..." : "Создать"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default KnowledgeGraphPage;
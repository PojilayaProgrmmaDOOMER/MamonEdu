from rdflib import Graph
from rdflib.namespace import RDF, OWL

from app.database import SessionLocal
from app.models.ontology_entity import OntologyEntity
from app.models.ontology_graph_relation import OntologyGraphRelation


ONTOLOGY_PATH = "app/ontology/ai_eduseg_ontology.rdf"

RELATION_TYPES = [
    "requires",
    "required_for",
    "used_in",
    "related_to",
    "checks",
    "part_of",
    "explains",
]


def short_name(uri):
    return str(uri).split("#")[-1]


def get_or_create_entity(db, name: str, entity_type: str):
    entity = db.query(OntologyEntity).filter(
        OntologyEntity.name == name
    ).first()

    if entity is not None:
        return entity

    entity = OntologyEntity(
        name=name,
        entity_type=entity_type
    )

    db.add(entity)
    db.commit()
    db.refresh(entity)

    return entity


def import_ontology():
    graph = Graph()
    graph.parse(ONTOLOGY_PATH, format="xml")

    db = SessionLocal()

    try:
        for subject in graph.subjects(RDF.type, OWL.NamedIndividual):
            name = short_name(subject)

            entity_type = "Individual"

            for obj in graph.objects(subject, RDF.type):
                obj_name = short_name(obj)

                if obj_name not in ["NamedIndividual"]:
                    entity_type = obj_name

            get_or_create_entity(db, name, entity_type)

        for subject, predicate, obj in graph:
            relation_type = short_name(predicate)

            if relation_type not in RELATION_TYPES:
                continue

            source_name = short_name(subject)
            target_name = short_name(obj)

            source_entity = get_or_create_entity(
                db,
                source_name,
                "Unknown"
            )

            target_entity = get_or_create_entity(
                db,
                target_name,
                "Unknown"
            )

            existing_relation = db.query(OntologyGraphRelation).filter(
                OntologyGraphRelation.source_entity_id == source_entity.id,
                OntologyGraphRelation.target_entity_id == target_entity.id,
                OntologyGraphRelation.relation_type == relation_type
            ).first()

            if existing_relation is None:
                relation = OntologyGraphRelation(
                    source_entity_id=source_entity.id,
                    target_entity_id=target_entity.id,
                    relation_type=relation_type
                )

                db.add(relation)

        db.commit()
        entities_count = db.query(OntologyEntity).count()
        relations_count = db.query(OntologyGraphRelation).count()

        print(f"Entities imported: {entities_count}")
        print(f"Relations imported: {relations_count}")
        print("Ontology imported successfully")
        print("Ontology imported successfully")

    finally:
        db.close()


if __name__ == "__main__":
    import_ontology()
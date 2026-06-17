from app.database import engine, Base
from app.models.study_group import StudyGroup
from app.models.study_group_student import StudyGroupStudent
from app.models.practical_task_concept import PracticalTaskConcept
from app.models.practical_task import PracticalTask
from app.models.code_submission import CodeSubmission
from app.models.test import Test
from app.models.user import User
from app.models.topic import Topic
from app.models.material import Material
from app.models.question import Question
from app.models.answer_option import AnswerOption
from app.models.test_attempt import TestAttempt
from app.models.answer_submission import AnswerSubmission
from app.models.test_attempt_question import TestAttemptQuestion
from app.models.user_topic_mastery import UserTopicMastery
from app.models.ontology_concept import OntologyConcept
from app.models.ontology_relation import OntologyRelation
from app.models.question_concept import QuestionConcept
from app.models.material_concept import MaterialConcept
from app.models.ontology_entity import OntologyEntity
from app.models.ontology_graph_relation import OntologyGraphRelation
from app.models.material_search_profile import MaterialSearchProfile
from app.models.external_material_candidate import ExternalMaterialCandidate

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully")
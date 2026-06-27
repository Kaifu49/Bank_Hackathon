import spacy

from models.entity import Entity


class SpacyEntityExtractor:

    def __init__(self):

        self.nlp = spacy.load(
            "en_core_web_sm"
        )

    def extract(
        self,
        text
    ):

        entities = []

        if not text:
            return entities

        doc = self.nlp(text)

        for ent in doc.ents:

            if ent.label_ == "PERSON":

                entities.append(
                    Entity(
                        entity_type="PERSON",
                        identifier=ent.text,
                        confidence=0.8
                    )
                )

            elif ent.label_ == "ORG":

                entities.append(
                    Entity(
                        entity_type="ORGANIZATION",
                        identifier=ent.text,
                        confidence=0.8
                    )
                )

        return entities
    
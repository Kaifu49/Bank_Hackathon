from models.entity import Entity

from services.upi_extractor import (
    UPIExtractor
)

from services.account_extractor import (
    AccountExtractor
)

from services.bank_extractor import (
    BankExtractor
)

from services.organization_extractor import (
    OrganizationExtractor
)

from services.merchant_extractor import (
    MerchantExtractor
)

from services.person_extractor import (
    PersonExtractor
)

from services.spacy_entity_extractor import (
    SpacyEntityExtractor
)


class EntityExtractor:

    def __init__(self):

        self.upi = (
            UPIExtractor()
        )

        self.account = (
            AccountExtractor()
        )

        self.bank = (
            BankExtractor()
        )

        self.organization = (
            OrganizationExtractor()
        )

        self.merchant = (
            MerchantExtractor()
        )

        self.person = (
            PersonExtractor()
        )

        self.spacy = (
            SpacyEntityExtractor()
        )

    def extract(
        self,
        transactions
    ):

        entities = []

        for txn in transactions:

            narration = str(
                txn.get(
                    "narration",
                    ""
                )
            )

            reference = str(
                txn.get(
                    "reference_number",
                    ""
                )
            )

            text = (
                narration
                + " "
                + reference
            )

            # -------------------------
            # UPI IDs
            # -------------------------

            for upi in (
                self.upi.extract(
                    text
                )
            ):

                entities.append(
                    Entity(
                        entity_type="UPI_ID",
                        identifier=upi,
                        confidence=1.0
                    )
                )

            # -------------------------
            # Account / Reference Numbers
            # -------------------------

            for account in (
                self.account.extract(
                    text
                )
            ):

                entities.append(
                    Entity(
                        entity_type="ACCOUNT_NO",
                        identifier=account,
                        confidence=1.0
                    )
                )

            # -------------------------
            # Banks
            # -------------------------

            for bank in (
                self.bank.extract(
                    text
                )
            ):

                entities.append(
                    Entity(
                        entity_type="BANK",
                        identifier=bank,
                        confidence=1.0
                    )
                )

            # -------------------------
            # Organizations
            # -------------------------

            for org in (
                self.organization.extract(
                    text
                )
            ):

                entities.append(
                    Entity(
                        entity_type="ORGANIZATION",
                        identifier=org,
                        confidence=1.0
                    )
                )

            # -------------------------
            # Merchants
            # -------------------------

            for merchant in (
                self.merchant.extract(
                    text
                )
            ):

                entities.append(
                    Entity(
                        entity_type="MERCHANT",
                        identifier=merchant,
                        confidence=1.0
                    )
                )

            # -------------------------
            # Banking-specific Person Extraction
            # -------------------------

            for person in (
                self.person.extract(
                    text
                )
            ):

                entities.append(
                    Entity(
                        entity_type="PERSON",
                        identifier=person.strip(),
                        confidence=0.9
                    )
                )

            # -------------------------
            # spaCy NER
            # -------------------------

            entities.extend(
                self.spacy.extract(
                    text
                )
            )

        # -------------------------
        # Deduplicate Entities
        # -------------------------

        unique_entities = {}

        for entity in entities:

            key = (
                entity.entity_type,
                entity.identifier.upper()
            )

            unique_entities[key] = entity

        return list(
            unique_entities.values()
        )
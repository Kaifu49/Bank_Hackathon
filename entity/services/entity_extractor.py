"""
EntityExtractor — extract typed entities from transaction narration/reference.

Entity types: UPI_ID, IFSC, BANK, ACCOUNT_NO, PHONE, PERSON, MERCHANT,
ORGANIZATION. Returns ALL mentions (one Entity per occurrence) so the resolver
can aggregate occurrence counts and aliases; the /entities endpoint dedups for
display.

spaCy NER is optional: if the model isn't installed the service still runs
(graceful degradation) using the deterministic extractors below.
"""

from models.entity import Entity

from services.upi_extractor import UPIExtractor
from services.ifsc_extractor import IFSCExtractor
from services.phone_extractor import PhoneExtractor
from services.account_extractor import AccountExtractor
from services.bank_extractor import BankExtractor
from services.organization_extractor import OrganizationExtractor
from services.merchant_extractor import MerchantExtractor
from services.person_extractor import PersonExtractor


class EntityExtractor:

    def __init__(self):
        self.upi = UPIExtractor()
        self.ifsc = IFSCExtractor()
        self.phone = PhoneExtractor()
        self.account = AccountExtractor()
        self.bank = BankExtractor()
        self.organization = OrganizationExtractor()
        self.merchant = MerchantExtractor()
        self.person = PersonExtractor()

        # Optional spaCy NER — degrade gracefully if unavailable.
        self.spacy = None
        try:
            from services.spacy_entity_extractor import SpacyEntityExtractor
            self.spacy = SpacyEntityExtractor()
        except Exception as exc:  # model not installed / import error
            print(f"[INFO] spaCy NER disabled ({exc}); using rule-based only.")

    def extract(self, transactions):
        entities = []

        for txn in transactions:
            narration = str(txn.get("narration", "") or "")
            reference = str(txn.get("reference_number", "") or "")
            text = (narration + " " + reference).strip()
            if not text:
                continue

            self._add(entities, "UPI_ID", self.upi.extract(text), 0.97)
            self._add(entities, "IFSC", self.ifsc.extract(text), 0.95)
            self._add(entities, "PHONE", self.phone.extract(text), 0.9)
            self._add(entities, "ACCOUNT_NO", self.account.extract(text), 0.9)
            self._add(entities, "BANK", self.bank.extract(text), 0.9)
            self._add(entities, "ORGANIZATION",
                      self.organization.extract(text), 0.85)
            self._add(entities, "MERCHANT", self.merchant.extract(text), 0.85)
            self._add(entities, "PERSON", self.person.extract(text), 0.7)

            if self.spacy is not None:
                try:
                    entities.extend(self.spacy.extract(text))
                except Exception:
                    pass

        return entities

    @staticmethod
    def _add(entities, etype, identifiers, confidence):
        for ident in identifiers:
            ident = (ident or "").strip()
            if ident:
                entities.append(
                    Entity(entity_type=etype, identifier=ident,
                           confidence=confidence)
                )

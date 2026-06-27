"""
Entity intelligence tests against REAL dataset narrations.
Extractors return strings (no pydantic); resolver tested via SimpleNamespace.
Run: python test_entity.py
"""
import sys, os
from types import SimpleNamespace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))

from upi_extractor import UPIExtractor           # noqa: E402
from ifsc_extractor import IFSCExtractor         # noqa: E402
from phone_extractor import PhoneExtractor       # noqa: E402
from account_extractor import AccountExtractor   # noqa: E402
from bank_extractor import BankExtractor         # noqa: E402
from person_extractor import PersonExtractor     # noqa: E402
from entity_resolver import EntityResolver       # noqa: E402

upi, ifsc, phone = UPIExtractor(), IFSCExtractor(), PhoneExtractor()
acct, bank, person = AccountExtractor(), BankExtractor(), PersonExtractor()

results = []


def check(label, got, exp):
    ok = got == exp
    results.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {label}: got={got}")
    if not ok:
        print(f"        expected={exp}")


# ---- extractors on real narrations ----
n1 = "UPI/533910415430/CR/FARA/BARB/ashok@okicici/UPI"
n2 = "meera@okicici/RADHA REKHA SAXENA"
n3 = "IMPS-OPM/510714100618/SHAFIQ/YESB0000419/8578"
n4 = "RTGS/ICICR42025050200522710/RG ENTERPRISE/ICIC0000011"
n5 = "Beneficiary A/C 50100412345678 IFSC HDFC0001234"
n6 = "banker@idfcfirstbank.com please contact"
n7 = "PHONE NO :91******6553"
n8 = "received from MOBILE 9876543210 ref"

check("UPI excludes email", upi.extract(n6), [])
check("UPI from n1", upi.extract(n1), ["ashok@okicici"])
check("UPI from n2", upi.extract(n2), ["meera@okicici"])
check("IFSC from n3", ifsc.extract(n3), ["YESB0000419"])
check("IFSC from n5", ifsc.extract(n5), ["HDFC0001234"])
check("Bank via IFSC n3", bank.extract(n3), ["YES BANK"])
check("Bank via IFSC n4", bank.extract(n4), ["ICICI BANK"])
check("Account w/ context n5", acct.extract(n5), ["50100412345678"])
check("No bare-number account n1", acct.extract(n1), [])
check("Masked phone -> none", phone.extract(n7), [])
check("Phone w/ context", phone.extract(n8), ["9876543210"])
check("Person after VPA n2", person.extract(n2), ["RADHA REKHA SAXENA"])


# ---- resolver: type-aware, cross-mention aggregation ----
def E(t, i, c=0.9):
    return SimpleNamespace(entity_type=t, identifier=i, confidence=c)

ents = [
    E("UPI_ID", "ashok@okicici"), E("UPI_ID", "ASHOK@okicici"),   # same -> merge
    E("UPI_ID", "meera@okicici"),
    E("IFSC", "YESB0000419"), E("IFSC", "YESB0000419"),           # merge, count 2
    E("PERSON", "RADHA REKHA SAXENA"), E("PERSON", "Radha Rekha Saxena"),  # merge
    E("ACCOUNT_NO", "50100412345678"),
]
canon = EntityResolver().resolve(ents)
by_type = {}
for c in canon:
    by_type.setdefault(c["entity_type"], []).append(c)

upi_ids = by_type.get("UPI_ID", [])
ashok = [c for c in upi_ids if c["canonical"].lower() == "ashok@okicici"]
check("UPI merged count", len(upi_ids), 2)
check("ashok occurrence_count=2", ashok[0]["occurrence_count"] if ashok else 0, 2)
check("ashok has 2 aliases", len(ashok[0]["aliases"]) if ashok else 0, 2)
check("IFSC merged to 1", len(by_type.get("IFSC", [])), 1)
check("IFSC count=2", by_type["IFSC"][0]["occurrence_count"], 2)
check("PERSON merged to 1", len(by_type.get("PERSON", [])), 1)

print()
if all(results):
    print(f"ALL ENTITY TESTS PASS ({sum(results)}/{len(results)})")
else:
    print(f"FAILURES ({sum(results)}/{len(results)} passed)")
    sys.exit(1)

"""
EntityResolver — group raw entity mentions into canonical entities.

Type-aware and deterministic:
  * Identifier types (UPI_ID, IFSC, ACCOUNT_NO, PHONE, BANK) resolve by exact
    normalized identity — no ML needed, and they merge across statements (a UPI
    id seen in two uploads becomes one canonical entity).
  * Name types (PERSON, MERCHANT, ORGANIZATION) resolve by normalized-name
    equality. Optional embedding-based fuzzy merge is used IF
    sentence-transformers is installed, otherwise it's skipped — the service
    never hard-fails on a missing model.

Output per canonical entity:
  { entity_type, canonical, display_name, aliases[], confidence,
    occurrence_count }
The keys `canonical / aliases / entity_type / confidence` match the Rust
CanonicalEntity model; extra keys are ignored by the backend.
"""

from collections import defaultdict
import re

_EXACT_TYPES = {"UPI_ID", "IFSC", "ACCOUNT_NO", "PHONE", "BANK"}


def _norm_exact(etype, ident):
    s = ident.strip()
    if etype == "UPI_ID":
        return s.lower()
    if etype in ("PHONE", "ACCOUNT_NO"):
        return re.sub(r"\D", "", s)
    return s.upper()


def _norm_name(ident):
    return re.sub(r"\s+", " ",
                  re.sub(r"[^A-Za-z0-9 ]", " ", ident)).strip().upper()


class EntityResolver:

    def __init__(self):
        self._embedder = None  # lazily/optionally loaded

    def resolve(self, entities, fuzzy=False):
        groups = defaultdict(list)
        for e in entities:
            groups[e.entity_type].append(e)

        canonical = []
        for etype, ents in groups.items():
            if etype in _EXACT_TYPES:
                canonical.extend(self._resolve_exact(etype, ents))
            else:
                canonical.extend(self._resolve_names(etype, ents, fuzzy))
        canonical.sort(key=lambda c: c["occurrence_count"], reverse=True)
        return canonical

    # -- exact identifier resolution -------------------------------------

    def _resolve_exact(self, etype, ents):
        buckets = defaultdict(list)
        for e in ents:
            buckets[_norm_exact(etype, e.identifier)].append(e)
        return [self._make(etype, members) for members in buckets.values()]

    # -- name resolution -------------------------------------------------

    def _resolve_names(self, etype, ents, fuzzy):
        buckets = defaultdict(list)
        for e in ents:
            buckets[_norm_name(e.identifier)].append(e)
        clusters = list(buckets.values())
        if fuzzy:
            clusters = self._fuzzy_merge(clusters)
        return [self._make(etype, members) for members in clusters]

    def _fuzzy_merge(self, clusters):
        embedder = self._get_embedder()
        if embedder is None or len(clusters) < 2:
            return clusters
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            reps = [c[0].identifier for c in clusters]
            emb = embedder.encode(reps)
            merged, used = [], set()
            for i in range(len(clusters)):
                if i in used:
                    continue
                group = list(clusters[i])
                used.add(i)
                for j in range(i + 1, len(clusters)):
                    if j in used:
                        continue
                    if cosine_similarity([emb[i]], [emb[j]])[0][0] >= 0.85:
                        group.extend(clusters[j])
                        used.add(j)
                merged.append(group)
            return merged
        except Exception:
            return clusters

    def _get_embedder(self):
        if self._embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                self._embedder = False
        return self._embedder or None

    # -- helpers ---------------------------------------------------------

    def _make(self, etype, members):
        freq = defaultdict(int)
        for m in members:
            freq[m.identifier] += 1
        canonical = max(freq, key=lambda k: (freq[k], len(k)))
        aliases = sorted({m.identifier for m in members})
        confidence = round(max(m.confidence for m in members), 3)
        return {
            "entity_type": etype,
            "canonical": canonical,
            "display_name": canonical,
            "aliases": aliases,
            "confidence": confidence,
            "occurrence_count": len(members),
        }

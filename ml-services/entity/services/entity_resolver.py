from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

import numpy as np


class EntityResolver:

    def __init__(self):

        print(
            "Loading Entity Resolution Model..."
        )

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print(
            "Model Loaded"
        )

    def resolve(
        self,
        entities,
        threshold=0.85
    ):

        if not entities:
            return []

        identifiers = [

            entity.identifier

            for entity in entities
        ]

        embeddings = (
            self.model.encode(
                identifiers
            )
        )

        canonical = []

        visited = set()

        for i in range(
            len(identifiers)
        ):

            if i in visited:
                continue

            cluster = [
                identifiers[i]
            ]

            visited.add(i)

            for j in range(
                i + 1,
                len(identifiers)
            ):

                if j in visited:
                    continue

                similarity = (
                    cosine_similarity(
                        [embeddings[i]],
                        [embeddings[j]]
                    )[0][0]
                )

                if similarity >= threshold:

                    cluster.append(
                        identifiers[j]
                    )

                    visited.add(j)

            canonical.append({

                "canonical":
                    cluster[0],

                "aliases":
                    cluster
            })

        return canonical
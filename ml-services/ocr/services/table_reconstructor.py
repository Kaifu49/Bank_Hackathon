class TableReconstructor:

    def reconstruct(
        self,
        grouped_rows
    ):

        reconstructed = []

        for row in grouped_rows:

            reconstructed.append(
                [
                    cell["text"]
                    for cell in row
                ]
            )

        return reconstructed
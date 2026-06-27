from collections import defaultdict


class RowGrouper:

    def group_rows(
        self,
        ocr_results,
        tolerance=15
    ):

        rows = defaultdict(list)

        for item in ocr_results:

            bbox = item["bbox"]

            y_center = (
                bbox[0][1] +
                bbox[2][1]
            ) / 2

            row_key = (
                round(
                    y_center / tolerance
                ) * tolerance
            )

            rows[row_key].append(
                item
            )

        grouped_rows = []

        for _, row_items in sorted(
            rows.items()
        ):

            row_items.sort(
                key=lambda x:
                x["bbox"][0][0]
            )

            grouped_rows.append(
                row_items
            )

        return grouped_rows
"""CSV parsing utility for student import."""

import csv
import io


def parse_csv_rows(content: str) -> list[dict]:
    """Parse CSV content into list of student dicts.

    Args:
        content: UTF-8 decoded CSV text (BOM should already be stripped).

    Returns:
        List of dicts with keys: nombre, apellido, correo.

    Raises:
        ValueError: If the CSV has no header, has the wrong column count,
            or is completely empty.
    """
    if content is None or not content.strip():
        raise ValueError("CSV content is empty")

    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    if not rows:
        raise ValueError("CSV has no rows")

    header = rows[0]
    if not header or header[0].strip().lower() != "nombre":
        raise ValueError("CSV header is missing or invalid")

    result: list[dict] = []
    for row_index, row in enumerate(rows[1:], start=2):
        if len(row) != 3:
            raise ValueError(
                f"Row {row_index} has {len(row)} columns, expected 3"
            )
        result.append(
            {
                "nombre": row[0],
                "apellido": row[1],
                "correo": row[2],
            }
        )

    return result

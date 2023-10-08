from typing import Optional
from pathlib import Path


def build_itineraries_file(
    n: Optional[int],
    full_itineraries_file,
    data_dir: Path,
) -> Path:
    """Build itineraries file with n itineraries,
    or the whole dataset if n is None."""
    if n is None:
        return full_itineraries_file
    from subprocess import run

    output_file = data_dir / f"itineraries_{n}.csv"
    with open(output_file, "w") as out:
        run(
            [
                "head",
                "-n",
                str(n + 1), # Add 1 to offset header
                str(full_itineraries_file),
            ],
            shell=False,
            check=True,
            stdout=out,
        )
    return output_file

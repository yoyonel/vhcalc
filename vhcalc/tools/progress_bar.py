from typing import Optional, Tuple

from rich import get_console
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TransferSpeedColumn,
)

from vhcalc.tools.rich_colums import TimeElapsedOverRemainingColumn


def configure_progress_bar(
    filename: str, total: int, console: Optional[Console] = None
) -> Tuple[Progress, TaskID]:
    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeElapsedOverRemainingColumn(),
        console=console or get_console(),
    )
    task_id = progress.add_task(
        "build&export images hashes", filename=filename, start=True
    )
    progress.update(task_id, total=total)
    return progress, task_id

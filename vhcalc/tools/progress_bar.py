from datetime import timedelta
from typing import Optional, Tuple

from rich import get_console
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    Task,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.text import Text


class TimeElapsedOverRemainingColumn(TimeRemainingColumn):
    """Renders remaining on elapsed time."""

    def render(self, task: Task) -> Text:
        """Show times elapsed/remaining."""
        elapsed_delta = timedelta(seconds=int(task.elapsed or -1))
        remaining = super().render(task)
        return Text(f"{str(elapsed_delta)}/{remaining}", style="progress.remaining")


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

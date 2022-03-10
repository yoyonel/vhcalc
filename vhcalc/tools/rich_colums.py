from datetime import timedelta

from rich.progress import Task, TimeRemainingColumn
from rich.text import Text


class TimeElapsedOverRemainingColumn(TimeRemainingColumn):
    """Renders remaining on elapsed time."""

    def render(self, task: Task) -> Text:
        """Show times elapsed/remaining."""
        elapsed_delta = timedelta(seconds=int(task.elapsed or -1))
        remaining = super().render(task)
        return Text(f"{str(elapsed_delta)}/{remaining}", style="progress.remaining")

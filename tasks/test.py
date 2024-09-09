from invoke import task

from tasks.common import USE_PTY, VENV_PREFIX


@task(default=True)
def run(ctx, allow_no_tests=False):
    """Run test cases"""
    result = ctx.run(f"{VENV_PREFIX} pytest", pty=USE_PTY, warn=True)
    if allow_no_tests and result.exited == 5:
        exit(0)
    exit(result.exited)


@task
def cov(ctx):
    """Run test coverage check"""
    # some doctests are present in vhcalc directory
    ctx.run(f"{VENV_PREFIX} pytest --cov=vhcalc --cov-append vhcalc/ tests/", pty=USE_PTY)


@task
def tox(ctx):
    """Run tox"""
    ctx.run(f"{VENV_PREFIX} tox", pty=USE_PTY, warn=True)

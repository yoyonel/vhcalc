from invoke import task

from tasks.common import VENV_PREFIX


@task
def clean(ctx):
    """Remove virtual environement"""
    # ctx.run("poetry env remove 3.9", warn=True)
    ctx.run("rm -rf .venv", warn=True)
    # ["No source for code" message in Coverage.py](https://stackoverflow.com/a/3123157)
    ctx.run("rm -rf .coverage")


@task
def init(ctx):
    """Install production dependencies"""
    ctx.run("uv sync --no-dev")


@task
def setup_pre_commit_hook(ctx):
    """Setup pre-commit hook to automate check before git commit and git push"""
    ctx.run("git init")
    ctx.run(
        f"{VENV_PREFIX} pre-commit install -t pre-commit & "
        f"{VENV_PREFIX} pre-commit install -t pre-push & "
        f"{VENV_PREFIX} pre-commit install -t commit-msg &"
        f"{VENV_PREFIX} pre-commit autoupdate"
    )


@task(optional=["no-pre-commit"])
def init_dev(ctx, no_pre_commit=False):
    """Install development dependencies and setup pre-commit hooks"""
    ctx.run("uv sync")
    if not no_pre_commit:
        setup_pre_commit_hook(ctx)


@task
def from_scratch(ctx):
    """build from scratch"""
    clean(ctx)
    ctx.run("uv lock")
    init_dev(ctx)
    ctx.run("inv test.cov")
    ctx.run("inv style")
    ctx.run("inv secure")
    ctx.run("inv doc.build")
    ctx.run("inv build.docker")
    ctx.run("cat tests/data/big_buck_bunny_trailer_480p.mkv | vhcalc | md5sum")

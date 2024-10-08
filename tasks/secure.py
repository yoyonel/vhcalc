from invoke import task

from tasks.common import USE_PTY, VENV_PREFIX


@task
def check_package(ctx):
    """Check package security"""
    ctx.run("poetry run safety check", warn=True)


@task
def bandit(ctx):
    """Check common software vulnerabilities (Use it as reference only)"""
    ctx.run(f"{VENV_PREFIX} bandit -r -iii -lll --ini .bandit", pty=USE_PTY)


@task(pre=[check_package, bandit], default=True)
def run(ctx):
    """Check security check throguh safety and bandit"""
    pass

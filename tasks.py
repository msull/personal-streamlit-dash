from contextlib import contextmanager
from pathlib import Path

from invoke import task, Context


class Paths:
    here = Path(__file__).parent
    repo_root = here

    @staticmethod
    @contextmanager
    def cd(c: Context, p: Path):
        with c.cd(str(p)):
            yield


@task
def compile_requirements(c, install=False):
    with Paths.cd(c, Paths.repo_root):
        c.run("pip-compile --resolver=backtracking -v -o requirements.txt")
        if install:
            c.run("pip install -r requirements.txt")
            c.run("pip install -r requirements.dev.txt")


@task
def run_streamlit(c):
    with Paths.cd(c, Paths.repo_root / "src"):
        c.run(
            "PYTHONPATH=../shared-src python -m streamlit run Home.py",
            pty=True,
        )


@task
def dc_up(c):
    with Paths.cd(c, Paths.repo_root):
        c.run('docker-compose up --build --detach')

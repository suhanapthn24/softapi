import typer
from pathlib import Path
from enum import Enum
from typing import Optional

from .scaffold.fastapi_basic import write_fastapi_basic

app = typer.Typer(help="softapi CLI – scaffold backends without boilerplate")


class DBChoice(str, Enum):
    sqlite = "sqlite"
    postgres = "postgres"


@app.command("new")
def new(
    path: str = typer.Argument(..., help="Path to create the project in (e.g., myapp/)"),
    fastapi: bool = typer.Option(False, "--fastapi", help="Use FastAPI template"),
    jwt: bool = typer.Option(False, "--jwt", help="Include JWT auth routes"),
    db: DBChoice = typer.Option(DBChoice.sqlite, "--db", help="Database: sqlite or postgres"),
    name: Optional[str] = typer.Option(None, "--name", help="Project name used in README/docs"),
    alembic: bool = typer.Option(False, "--alembic", help="Include Alembic migrations boilerplate"),
    docker: bool = typer.Option(False, "--docker", help="Include Dockerfile and docker-compose.yml"),
    colab: bool = typer.Option(False, "--colab", help="Include Colab runner with ngrok"),
):
    """
    Create a new project scaffold.
    """
    if not fastapi:
        typer.secho("Currently only --fastapi is supported.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    target = Path(path).resolve()
    if target.exists() and any(target.iterdir()):
        typer.secho(f"Directory {target} is not empty.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)

    project_name = name or Path(path).name

    # Scaffold files
    write_fastapi_basic(
        target,
        project_name=project_name,
        include_jwt=jwt,
        db=db.value,
        include_docker=docker,
        include_alembic=alembic,
        include_colab=colab,
    )

    typer.secho(f"✅ Created FastAPI project at: {target}", fg=typer.colors.GREEN)

    # Next steps (printed clearly and cross-platform)
    next_cmds = [
        f"cd {target}",
        "cp .env.example .env    # Windows (PowerShell): copy .env.example .env",
        "python -m venv .venv",
        "# Windows (PowerShell): .\\.venv\\Scripts\\Activate.ps1",
        "# Windows (cmd.exe):    .\\.venv\\Scripts\\activate.bat",
        "# macOS/Linux:          source .venv/bin/activate",
        "pip install -r requirements.txt",
        "uvicorn app.main:app --reload",
        "# alternatively (factory): uvicorn app.main:create_app --factory --reload",
    ]
    typer.echo("\nNext:\n  " + "\n  ".join(next_cmds))


if __name__ == "__main__":
    app()

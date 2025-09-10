import typer
from pathlib import Path
from .scaffold.fastapi_basic import write_fastapi_basic

app = typer.Typer(help="softapi CLI – scaffold FastAPI apps without boilerplate")

@app.command("new")
def new(path: str, name: str = "softapi"):
    """Create a new FastAPI project in PATH."""
    target = Path(path).resolve()
    if target.exists() and any(target.iterdir()):
        typer.secho(f"Directory {target} is not empty.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    target.mkdir(parents=True, exist_ok=True)
    write_fastapi_basic(target, project_name=name)
    typer.secho(f"Created FastAPI project at: {target}", fg=typer.colors.GREEN)
    typer.echo("Next:\n  1) cd {0}\n  2) cp .env.example .env\n  3) pip install -r requirements.txt\n  4) uvicorn app.main:app --reload".format(target))

if __name__ == "__main__":
    app()
"""Copy the bundled synthetic demo; never inspect user history or run a model."""

from pathlib import Path


def prepare(output):
    output = Path(output).expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("Choose a new demo directory; existing paths are never overwritten")
    source = Path(__file__).resolve().parents[2] / "assets/demo"
    contents = {name: (source / name).read_bytes() for name in ("START.md", "history.md")}
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    for name, content in contents.items():
        with (output / name).open("xb") as f:
            f.write(content)
    return {"output": str(output), "synthetic": True, "personal_history_read": False,
            "model_run": False, "next_step": "Give START.md and history.md to your agent with Second Look enabled."}

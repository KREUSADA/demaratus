import pathlib

from redbot.core.utils import chat_formatting as cf

def format_traceback(exc) -> str:
    boxit = lambda x, y: cf.box(f"{x}: {y}", lang="yaml")
    return boxit(exc.__class__.__name__, exc)

def reformat_dict(fields: dict) -> dict:
    out = {}
    for f in fields:
        out.update(f)
    return out

def cleanup_code(content):
    # From redbot.core.dev_commands, thanks will :P
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])
    return content.strip("` \n")

with open(pathlib.Path(__file__).parent / "assets.yaml") as fp:
    asset = cf.box("".join(fp.readlines()), lang=fp.name.split('.')[-1])
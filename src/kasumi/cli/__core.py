import json
import os
import re
import shutil
import urllib.parse

import cowsay
import requests
import tqdm
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="Kasumi",
    no_args_is_help=True
)
console = Console()

@app.command(hidden=True, deprecated=True)
def moo():
    print(cowsay.get_output_string('cow', 'Hello, World!') + "\n")
    table = Table("[bold dodger_blue2]Surprised?[/bold dodger_blue2]")
    table.add_row("This is a temporary addition due to Typer's specifications.")
    table.add_row("We plan to remove it in the future, so I suggest you enjoy Super Cow Powers while you can :)")
    table.add_row("")
    table.add_row("Love from the author❤")
    console.print(table)

@app.command()
def init(dir: str=os.getcwd(), template: str=None, external_template: str=None):
    dir = r"C:\\Users\AmaseCocoa\Desktop\\test"
    if template is None:
        while True:
            table = Table("[bold dodger_blue2]Select Internal Template[/bold dodger_blue2]")
            table.add_column("ID", justify="right", style="cyan", no_wrap=True)
            table.add_column("Name", style="magenta")
            table.add_column("Theme's Description", justify="right", style="green")
            table.add_row("1", "default", "The most standard and smallest Kasumi template.")
            table.add_row("2", "with_gear", "Kasumi template using Gear")
            console.print(table)
            select = input("select: ")
            if select == "1":
                template = "default"
                break
            elif select == "2":
                template = "with_gear"
                break
            else:
                table = Table("[bold red]Error[/bold red]")
                table.add_row("The specified template does not exist.")
                console.print(table)
    if not external_template:
        template_dir = os.path.join(os.path.join(os.path.dirname(__file__), "__templates"), template)
        if os.path.isdir(template_dir):
            with open(os.path.join(template_dir, "manifest.json"), "r") as f:
                manifest = json.load(f)
                for file in manifest["files"]:
                    if isinstance(file, dict):
                        shutil.copytree(os.path.join(os.path.join(template_dir, file["dir"])), os.path.join(dir, file["dir"]))
                    else:
                        path = os.path.join(template_dir, file)
                        shutil.copy(path, dir)
        else:
            table = Table("[bold red]Error[/bold red]")
            table.add_row("The specified template does not exist.")
            console.print(table)
            raise
    else:
        pattern = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        if re.match(pattern, external_template):
            if not external_template.endswith("manifest.json"):
                manifest = urllib.parse.urljoin(external_template, "manifest.json")
            else:
                raise ValueError
            manifest = requests.get(external_template)
            manifest_jsonized = manifest.json()
            for file in manifest_jsonized["files"]:
                with open(os.path.join(dir, file), 'wb') as fp:
                    url = urllib.parse.urljoin(external_template, file)
                    with requests.get(url, stream=True) as req:
                        req.raise_for_status()
                        total = int(req.headers.get('content-length', 0))
                        with tqdm.tqdm(**{'desc': url,'total': total,'miniters': 1,'unit': 'B','unit_scale': True,'unit_divisor': 1024,}) as pb:
                            for chunk in req.iter_content(chunk_size=8192):
                                pb.update(len(chunk))
                                fp.write(chunk)
        else:
            with open(os.path.join(external_template, "manifest.json"), "r") as f:
                manifest = json.load(f)
                for file in manifest["files"]:
                    if isinstance(file, dict):
                        os.mkdir(os.path.join(dir, file["dir"]))
                        for filed in file["files"]:
                            shutil.copy(os.path.join(os.path.join(os.path.join(external_template, file["dir"]), filed), os.path.join(dir, file["dir"])))
                    else:
                        shutil.copy(os.path.join(external_template, file), dir)
    console.print("[bold green]Project initialization succeeded![/bold green]")
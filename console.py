from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

console = Console()

def rprint(text, status = "ok"):
	ok_style = "[green]"
	error_style = "[red]"
	
	match status:
			case "ok":
					console.print(f"{ok_style} {text}")
			case "error":
					console.print(f"{error_style} {text}")
			case _:
					console.print(f"{error_style} Please pass in a valid status.")
					
def print_logo():
	title = """
 __      ___     _              ____        _   
 \ \    / (_)   | |            |  _ \      | |  
  \ \  / / _  __| | ___  ___   | |_) | ___ | |_ 
   \ \/ / | |/ _` |/ _ \/ _ \  |  _ < / _ \| __|
    \  /  | | (_| |  __/ (_) | | |_) | (_) | |_ 
     \/   |_|\__,_|\___|\___/  |____/ \___/ \__|
  
  Generate AI Voiced videos faster... Made By Sparkles                                         
"""
	rprint(Panel(f"[green]{title}", style = "green"))

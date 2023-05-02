from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

console = Console()

ok_style = "[green]"
error_style = "[red]"
border_error = "[white on dark_green]"
border_info = "[white on red]"

def print_border(text, status = "ok", style = "[white on dark_green]"):
	""" Print info with white text on green background """
	match status:
		case "ok":
			rprint(f"{style} {text}")
		case _:
			rprint(f"{border_error} {text}")
	
	
def print_rule(text, status = "ok"):
	""" Print rich text to the terminal """
	
	match status:
			case "ok":
					console.rule(f"{ok_style} {text.title()}", style = "green")
			case _:
					console.rule(f"{error_style} {text.title()}", style = "red")

def show_func_status(func, text:str):
	""" Show a status when a function is running """
	with console.status(text.title()):
		value = func
		print_rule(f"Done With: {text}")
		return value

def show_status(text: str):
	""" Shows a status for a normal statement execution """
	with console.status(text.title()):
		rprint(f"{border_info} Done With: {text}")
	
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

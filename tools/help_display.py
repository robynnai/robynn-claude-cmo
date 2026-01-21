from rich.console import Console
from rich.panel import Panel

def display_help():
    console = Console()

    # ASCII Art matching the target screenshot - square block style
    logo = """█▀▀█ █▀▀█ █▀▀█ █  █
█▄▄▀ █  █ █▄▄▀  ▀▀ 
█  █ █▄▄█ █  █   █ 

       Your CMO in the Terminal"""
    console.print(Panel(logo, border_style="dim", padding=(0, 4)))

    console.print("[bold]USAGE[/bold]")
    console.print("    rory <command> [args]")
    console.print("[bold]COMMANDS[/bold]")
    console.print("    [green]research <company>[/green]        Research a company's marketing strategy")
    console.print("    [green]competitors <name>[/green]        Analyze competitor landscape")
    console.print("    [green]write <type>[/green]              Create content (linkedin, tweet, email, blog)")
    console.print("    [green]brief --for <type>[/green]        Create a marketing brief")
    console.print("    [green]status[/green]                    Check connection status")
    console.print("    [green]usage[/green]                     Check task usage this month")
    console.print("    [green]config <api_key>[/green]          Connect your Robynn account")
    console.print("    [green]sync[/green]                      Sync Brand Hub context")
    console.print("    [green]voice[/green]                     Preview brand voice settings")
    console.print("[bold]OPTIONS[/bold]")
    console.print("    --json                    Output in JSON format")
    console.print("[bold]EXAMPLES[/bold]")
    console.print("    rory \"Write a LinkedIn post about AI automation\"")
    console.print("    rory research Stripe")
    console.print("    rory competitors \"marketing automation\"")
    console.print("    rory write linkedin post about our new feature")
    console.print("    rory brief --for \"product launch campaign\"")
    console.print("[bold]SETUP[/bold]")
    console.print("    1. Get your API key at [underline]https://robynn.ai/settings/api-keys[/underline]")
    console.print("    2. Run: rory config <your_api_key>")
    console.print("    3. Verify: rory status")
    console.print("\nFor more help, visit [underline]https://robynn.ai/docs/rory[/underline]")
    console.print("[dim]───[/dim]\nWhat can I help you with today? Write content, research, or manage ads.")

if __name__ == "__main__":
    display_help()

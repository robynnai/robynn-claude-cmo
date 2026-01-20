from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

def display_help():
    console = Console()

    # ASCII Art
    ascii_art = """
 ██████╗    ██████╗   ██████╗   ██╗   ██╗
 ██╔══██╗  ██╔═══██╗  ██╔══██╗  ╚██╗ ██╔╝
 ██████╔╝  ██║   ██║  ██████╔╝   ╚████╔╝
 ██╔══██╗  ██║   ██║  ██╔══██╗    ╚██╔╝
 ██║  ██║  ╚██████╔╝  ██║  ██║     ██║
 ╚═╝  ╚═╝   ╚═════╝   ╚═╝  ╚═╝     ╚═╝
"""
    
    # Header with ASCII Art and Tagline
    console.print(ascii_art, style="bold white", justify="center")
    
    tagline = Text("CMO Agent\n", style="dim", justify="center")
    # Using brand orange #D2600F for "Robynn AI"
    tagline.append("powered by ", style="dim")
    tagline.append("Robynn AI", style="bold #D2600F")
    console.print(tagline, justify="center")
    console.print()

    # Getting Started Section
    console.print("[bold cyan]GETTING STARTED[/bold cyan]")
    console.print("1. Sign up at [underline blue]https://robynn.ai[/underline blue]")
    console.print("2. Navigate to [bold]Settings → Brand Hub[/bold] and configure:")
    console.print("   • Company name and description")
    console.print("   • Product features and differentiators")
    console.print("   • Brand voice and tone")
    console.print("3. Go to [bold]Settings → API Keys[/bold] and generate a key")
    console.print("4. Run: [bold green]rory config <your_api_key>[/bold green]")
    console.print("5. Verify: [bold green]rory status[/bold green]")
    console.print()

    # Usage Examples Table
    table = Table(title="USAGE EXAMPLES", show_header=True, header_style="bold magenta", box=None)
    table.add_column("Category", style="cyan")
    table.add_column("Commands", style="white")

    table.add_row(
        "Content Creation",
        "rory write linkedin-post about our new AI feature\n"
        "rory write tweet announcing our Series A\n"
        "rory write blog-outline on AI in marketing\n"
        "rory write email cold outreach for enterprise"
    )
    table.add_row("", "") # Spacer
    table.add_row(
        "Research",
        "rory research Stripe\n"
        "rory competitors Notion\n"
        "rory \"find VP Marketing contacts at fintech startups\""
    )
    table.add_row("", "") # Spacer
    table.add_row(
        "Ads Management",
        "rory \"show my Google Ads performance last 30 days\"\n"
        "rory \"create LinkedIn campaign for product launch\""
    )
    table.add_row("", "") # Spacer
    table.add_row(
        "Status & Config",
        "rory status\n"
        "rory usage\n"
        "rory sync"
    )

    console.print(Panel(table, border_style="dim"))
    
    console.print("\n[dim]Learn more: [underline]https://robynn.ai/docs/rory[/underline][/dim]", justify="center")

if __name__ == "__main__":
    display_help()

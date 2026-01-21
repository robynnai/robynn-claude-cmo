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
    
    tagline = Text("Your CMO in the Terminal\n", style="dim", justify="center")
    tagline.append("powered by ", style="dim")
    tagline.append("Robynn AI", style="bold #D2600F")
    console.print(tagline, justify="center")
    console.print()

    # Quick Start Section
    console.print("[bold cyan]QUICK START[/bold cyan]")
    console.print()
    console.print("  [bold green]rory init <api_key>[/bold green]    Fastest: paste your API key directly")
    console.print("                         Works everywhere (Claude Code, Desktop, terminal)")
    console.print()
    console.print("  [bold green]rory init[/bold green]              Interactive wizard (terminal only)")
    console.print("                         Opens browser → sign up → paste key")
    console.print()
    console.print("  [dim]Get your key:[/dim] [underline]https://robynn.ai/settings/api-keys[/underline]")
    console.print()

    # Commands Table
    cmd_table = Table(title="COMMANDS", show_header=True, header_style="bold magenta", box=None)
    cmd_table.add_column("Command", style="green", min_width=28)
    cmd_table.add_column("Description", style="white")

    # Account & Setup
    cmd_table.add_row("[bold cyan]Account & Setup[/bold cyan]", "")
    cmd_table.add_row("  init", "Interactive setup wizard (opens browser)")
    cmd_table.add_row("  init <api_key>", "Configure with API key directly")
    cmd_table.add_row("  login", "Alias for init")
    cmd_table.add_row("  config <api_key>", "Save API key (same as init <key>)")
    cmd_table.add_row("  logout", "Remove saved API key")
    cmd_table.add_row("  uninstall", "Remove the Rory plugin entirely")
    cmd_table.add_row("", "")

    # Status & Info
    cmd_table.add_row("[bold cyan]Status & Info[/bold cyan]", "")
    cmd_table.add_row("  status", "Check connection and brand hub status")
    cmd_table.add_row("  usage", "View remaining tasks and tier info")
    cmd_table.add_row("  sync", "Verify Brand Hub connection")
    cmd_table.add_row("  voice", "Preview brand voice settings")
    cmd_table.add_row("  help", "Show this help message")
    cmd_table.add_row("", "")

    # Content Creation
    cmd_table.add_row("[bold cyan]Content Creation[/bold cyan]", "")
    cmd_table.add_row("  write <type> [topic]", "Create marketing content")
    cmd_table.add_row("", "[dim]Types: linkedin-post, tweet, blog-outline, email[/dim]")
    cmd_table.add_row("  brief --for <topic>", "Generate a marketing brief")
    cmd_table.add_row("", "")

    # Research
    cmd_table.add_row("[bold cyan]Research[/bold cyan]", "")
    cmd_table.add_row("  research <company>", "Deep-dive company research")
    cmd_table.add_row("  competitors <company>", "Competitive intelligence analysis")
    cmd_table.add_row("", "")

    # Free-form
    cmd_table.add_row("[bold cyan]Free-form Queries[/bold cyan]", "")
    cmd_table.add_row("  \"<any request>\"", "Ask anything in natural language")

    console.print(Panel(cmd_table, border_style="dim"))

    # Examples Section
    console.print()
    console.print("[bold cyan]EXAMPLES[/bold cyan]")
    console.print()
    console.print("  [dim]# Setup[/dim]")
    console.print("  rory init                              [dim]# Interactive wizard (in terminal)[/dim]")
    console.print("  rory init rb_abc123...                 [dim]# Direct setup with API key[/dim]")
    console.print()
    console.print("  [dim]# Content[/dim]")
    console.print("  rory write linkedin-post about our new AI feature")
    console.print("  rory write tweet announcing our Series A")
    console.print("  rory write email cold outreach for enterprise")
    console.print("  rory brief --for product launch campaign")
    console.print()
    console.print("  [dim]# Research[/dim]")
    console.print("  rory research Stripe")
    console.print("  rory competitors Notion")
    console.print("  rory \"find VP Marketing contacts at fintech startups\"")
    console.print()
    console.print("  [dim]# Ads[/dim]")
    console.print("  rory \"show my Google Ads performance last 30 days\"")
    console.print("  rory \"create LinkedIn campaign for product launch\"")
    console.print()

    # Options
    console.print("[bold cyan]OPTIONS[/bold cyan]")
    console.print("  --json                 Output results in JSON format")
    console.print("  --help, -h             Show this help message")
    console.print()

    # Pricing
    console.print("[bold cyan]PRICING[/bold cyan]")
    pricing_table = Table(show_header=True, header_style="bold", box=None)
    pricing_table.add_column("Tier", style="cyan")
    pricing_table.add_column("Limit", style="white")
    pricing_table.add_column("Price", style="green")
    pricing_table.add_row("Anonymous", "5 tasks/day", "Free")
    pricing_table.add_row("Free", "20 tasks/month", "Free")
    pricing_table.add_row("Pro", "500 tasks/day", "See robynn.ai/pricing")
    console.print(pricing_table)
    console.print()

    # Footer
    console.print("[dim]─" * 50 + "[/dim]")
    console.print("[dim]Documentation:[/dim] [underline blue]https://robynn.ai/docs/rory[/underline blue]")
    console.print("[dim]Support:[/dim]       [underline blue]support@robynn.ai[/underline blue]")
    console.print("[dim]Get API Key:[/dim]   [underline blue]https://robynn.ai/settings/api-keys[/underline blue]")
    console.print()

if __name__ == "__main__":
    display_help()

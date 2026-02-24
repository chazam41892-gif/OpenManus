"""
OpenManus Registration/Setup Wizard

Guides users through setting up their OpenManus configuration so they can
get started quickly with their chosen LLM provider.
"""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PROJECT_ROOT / "config"
CONFIG_FILE = CONFIG_DIR / "config.toml"


PROVIDER_TEMPLATES = {
    "1": {
        "name": "OpenAI",
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
        "api_type": "",
        "api_version": "",
        "vision_model": "gpt-4o",
    },
    "2": {
        "name": "Anthropic",
        "model": "claude-3-7-sonnet-20250219",
        "base_url": "https://api.anthropic.com/v1/",
        "api_type": "",
        "api_version": "",
        "vision_model": "claude-3-7-sonnet-20250219",
    },
    "3": {
        "name": "PPIO",
        "model": "deepseek/deepseek-v3-0324",
        "base_url": "https://api.ppinfra.com/v3/openai",
        "api_type": "ppio",
        "api_version": "",
        "vision_model": "qwen/qwen2.5-vl-72b-instruct",
    },
    "4": {
        "name": "Azure OpenAI",
        "model": "gpt-4o",
        "base_url": "",
        "api_type": "azure",
        "api_version": "2024-08-01-preview",
        "vision_model": "gpt-4o",
    },
    "5": {
        "name": "Ollama (local)",
        "model": "llama3.2",
        "base_url": "http://localhost:11434/v1",
        "api_type": "ollama",
        "api_version": "",
        "vision_model": "llama3.2-vision",
    },
}


def print_banner():
    print("\n" + "=" * 60)
    print("  Welcome to the OpenManus Setup Wizard")
    print("  Get registered and start using your AI agent!")
    print("=" * 60 + "\n")


def prompt(message, default=None, secret=False):
    """Prompt the user for input, optionally with a default value."""
    if default:
        display = f"{message} [{default}]: "
    else:
        display = f"{message}: "

    if secret:
        import getpass
        value = getpass.getpass(display)
    else:
        value = input(display).strip()

    if not value and default:
        return default
    return value


def choose_provider():
    """Let the user choose their LLM provider."""
    print("Choose your LLM provider:\n")
    for key, info in PROVIDER_TEMPLATES.items():
        print(f"  {key}. {info['name']}")
    print()

    while True:
        choice = input("Enter your choice (1-5): ").strip()
        if choice in PROVIDER_TEMPLATES:
            return PROVIDER_TEMPLATES[choice]
        print("Invalid choice. Please enter a number between 1 and 5.")


def build_config(provider, api_key, model, base_url, api_version, vision_model, vision_api_key):
    """Build the TOML configuration string."""
    lines = ["# Global LLM configuration"]
    lines.append("[llm]")
    lines.append(f'model = "{model}"')
    lines.append(f'base_url = "{base_url}"')
    lines.append(f'api_key = "{api_key}"')
    lines.append("max_tokens = 4096")
    lines.append("temperature = 0.0")
    if provider["api_type"]:
        lines.append(f'api_type = "{provider["api_type"]}"')
    if api_version:
        lines.append(f'api_version = "{api_version}"')
    lines.append("")
    lines.append("[llm.vision]")
    lines.append(f'model = "{vision_model}"')
    lines.append(f'base_url = "{base_url}"')
    lines.append(f'api_key = "{vision_api_key}"')
    lines.append("max_tokens = 8192")
    lines.append("temperature = 0.0")
    if provider["api_type"]:
        lines.append(f'api_type = "{provider["api_type"]}"')
    if api_version:
        lines.append(f'api_version = "{api_version}"')
    lines.append("")
    lines.append("# MCP (Model Context Protocol) configuration")
    lines.append("[mcp]")
    lines.append('server_reference = "app.mcp.server"')
    lines.append("")
    lines.append("# Optional Runflow configuration")
    lines.append("[runflow]")
    lines.append("use_data_analysis_agent = false")
    return "\n".join(lines) + "\n"


def main():
    print_banner()

    if CONFIG_FILE.exists():
        print(f"A configuration file already exists at:\n  {CONFIG_FILE}\n")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != "y":
            print("\nSetup cancelled. Your existing configuration was not changed.")
            sys.exit(0)

    print("This wizard will help you set up your OpenManus configuration.\n")

    # Choose provider
    provider = choose_provider()
    print(f"\nSelected provider: {provider['name']}\n")

    # Gather details
    api_key = prompt("Enter your API key", secret=True)
    if not api_key:
        print("API key cannot be empty. Please run register.py again.")
        sys.exit(1)

    model = prompt("Model name", default=provider["model"])
    base_url = prompt("API base URL", default=provider["base_url"])
    api_version = ""
    if provider["api_type"] == "azure":
        api_version = prompt("API version", default=provider["api_version"])

    print("\nVision model configuration (press Enter to use same API key):")
    vision_model = prompt("Vision model name", default=provider["vision_model"])
    vision_api_key_input = prompt("Vision model API key (leave blank to reuse your API key)")
    vision_api_key = vision_api_key_input if vision_api_key_input else api_key

    # Write config
    config_content = build_config(
        provider, api_key, model, base_url, api_version, vision_model, vision_api_key
    )

    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(config_content, encoding="utf-8")

    print(f"\n✓ Configuration saved to: {CONFIG_FILE}")
    print("\nYou are now registered and ready to use OpenManus!")
    print("Run the following command to start:\n")
    print("  python main.py\n")


if __name__ == "__main__":
    main()

"""Result formatting for text and JSON output."""

import json
from dataclasses import dataclass, field, asdict
from enum import IntEnum
from typing import Dict, List, Optional


class ExitCode(IntEnum):
    """Exit codes for Ansible integration."""
    SUCCESS = 0           # All components installed successfully
    PARTIAL_FAILURE = 1   # Some components failed
    COMPLETE_FAILURE = 2  # All components failed or critical error
    INVALID_CONFIG = 3    # Invalid configuration/arguments


@dataclass
class InstallResult:
    """Tracks installation results for all components.

    Attributes:
        components: Dict mapping component names to success status
        errors: List of error messages
        warnings: List of warning messages
        changed: Whether any changes were made to the system
        dry_run: Whether this was a dry-run execution
        profile: Name of the profile used
    """
    components: Dict[str, bool] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    changed: bool = False
    dry_run: bool = False
    profile: Optional[str] = None

    def add_component(self, name: str, success: bool, error: Optional[str] = None):
        """Record a component installation result.

        Args:
            name: Component name (vim, tmux, zsh, etc.)
            success: Whether installation succeeded
            error: Optional error message if failed
        """
        self.components[name] = success
        if success:
            self.changed = True
        if error:
            self.errors.append(f"{name}: {error}")

    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)

    def add_error(self, message: str):
        """Add a general error message."""
        self.errors.append(message)

    @property
    def failed(self) -> bool:
        """Check if any component failed."""
        return any(not success for success in self.components.values())

    @property
    def all_failed(self) -> bool:
        """Check if all components failed."""
        if not self.components:
            return False
        return all(not success for success in self.components.values())

    def get_exit_code(self) -> ExitCode:
        """Determine appropriate exit code based on results."""
        if self.all_failed:
            return ExitCode.COMPLETE_FAILURE
        if self.failed:
            return ExitCode.PARTIAL_FAILURE
        return ExitCode.SUCCESS

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'changed': self.changed,
            'failed': self.failed,
            'dry_run': self.dry_run,
            'profile': self.profile,
            'components': self.components,
            'errors': self.errors,
            'warnings': self.warnings,
            'exit_code': int(self.get_exit_code()),
        }


class OutputFormatter:
    """Formats installation results for different output modes."""

    def __init__(self, format_type: str = 'text', quiet: bool = False):
        """Initialize formatter.

        Args:
            format_type: Output format ('text' or 'json')
            quiet: Suppress non-essential output in text mode
        """
        self.format_type = format_type
        self.quiet = quiet

    def format_result(self, result: InstallResult) -> str:
        """Format the installation result.

        Args:
            result: InstallResult instance

        Returns:
            Formatted string (text or JSON)
        """
        if self.format_type == 'json':
            return self._format_json(result)
        return self._format_text(result)

    def _format_json(self, result: InstallResult) -> str:
        """Format result as JSON."""
        return json.dumps(result.to_dict(), indent=2)

    def _format_text(self, result: InstallResult) -> str:
        """Format result as human-readable text."""
        lines = []

        if result.dry_run:
            lines.append("[DRY RUN] No changes were made")
            lines.append("")

        if result.profile:
            lines.append(f"Profile: {result.profile}")

        # Component results
        if result.components:
            lines.append("")
            lines.append("Components:")
            for name, success in result.components.items():
                status = "OK" if success else "FAILED"
                lines.append(f"  {name}: {status}")

        # Warnings
        if result.warnings and not self.quiet:
            lines.append("")
            lines.append("Warnings:")
            for warning in result.warnings:
                lines.append(f"  - {warning}")

        # Errors
        if result.errors:
            lines.append("")
            lines.append("Errors:")
            for error in result.errors:
                lines.append(f"  - {error}")

        # Summary
        lines.append("")
        if result.failed:
            failed_count = sum(1 for s in result.components.values() if not s)
            total = len(result.components)
            lines.append(f"Installation completed with {failed_count}/{total} failures")
        else:
            lines.append("Installation completed successfully")

        return '\n'.join(lines)

    def format_profiles(self, profiles: list) -> str:
        """Format list of available profiles.

        Args:
            profiles: List of (name, description) tuples

        Returns:
            Formatted string
        """
        if self.format_type == 'json':
            return json.dumps([{'name': n, 'description': d} for n, d in profiles], indent=2)

        lines = ["Available profiles:", ""]
        for name, description in profiles:
            lines.append(f"  {name:10} - {description}")
        return '\n'.join(lines)

    def format_dry_run_action(self, action: str) -> str:
        """Format a dry-run action message.

        Args:
            action: Description of what would be done

        Returns:
            Formatted string
        """
        if self.format_type == 'json':
            return ""  # JSON output collects all at end
        if not self.quiet:
            return f"[DRY RUN] Would: {action}"
        return ""

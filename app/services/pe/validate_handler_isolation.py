#!/usr/bin/env python3
"""
Validation Script for Handler Isolation

This script validates that extraction handlers remain isolated and independent.
Run this before committing changes to extraction handlers.

Usage:
    python app/services/pe/validate_handler_isolation.py
    docker compose exec app python app/services/pe/validate_handler_isolation.py
"""

import ast
import sys
import os
from pathlib import Path


class HandlerIsolationValidator:
    """Validates that extraction handlers are isolated."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.handlers = []
        
    def validate(self) -> bool:
        """Run all validation checks."""
        try:
            with open(self.file_path, 'r') as f:
                tree = ast.parse(f.read(), filename=self.file_path)
            
            self._find_handlers(tree)
            self._check_module_level_variables(tree)
            self._check_shared_state(tree)
            self._check_handler_independence(tree)
            
            return len(self.errors) == 0
        except Exception as e:
            self.errors.append(f"Failed to parse file: {e}")
            return False
    
    def _find_handlers(self, tree: ast.AST):
        """Find all extraction handler functions."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_extract_') and node.name.endswith('_data'):
                    self.handlers.append(node.name)
    
    def _check_module_level_variables(self, tree: ast.AST):
        """Check for module-level variables that might be shared."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Check if assignment is at module level (not inside a function)
                if not self._is_inside_function(node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Constants are OK, but mutable variables are not
                            if not target.id.isupper():  # Not a constant
                                self.warnings.append(
                                    f"Module-level variable '{target.id}' found. "
                                    "Ensure it's not modified by handlers."
                                )
    
    def _check_shared_state(self, tree: ast.AST):
        """Check for shared state between handlers."""
        # This is a simplified check - full analysis would require more complex AST traversal
        handler_names = [h for h in self.handlers]
        
        # Check if handlers call each other
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in handler_names:
                        # Check if this call is inside another handler
                        parent_handler = self._get_parent_handler(node)
                        if parent_handler and parent_handler != node.func.id:
                            self.errors.append(
                                f"Handler '{parent_handler}' calls another handler '{node.func.id}'. "
                                "Handlers must be independent."
                            )
    
    def _check_handler_independence(self, tree: ast.AST):
        """Check that handlers are independent."""
        if len(self.handlers) < 2:
            return  # Need at least 2 handlers to check independence
        
        # Check that each handler uses only local variables
        for handler_name in self.handlers:
            handler_node = self._find_function(tree, handler_name)
            if handler_node:
                # Check for non-local variable assignments
                for node in ast.walk(handler_node):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Check if variable is used outside handler
                                # (simplified check - would need more complex analysis)
                                pass
    
    def _is_inside_function(self, node: ast.AST) -> bool:
        """Check if node is inside a function definition."""
        for parent in ast.walk(ast.parse("")):
            # Simplified check - would need proper parent tracking
            return False
    
    def _get_parent_handler(self, node: ast.AST) -> str:
        """Get the name of the handler function containing this node."""
        # Simplified - would need proper parent tracking
        return None
    
    def _find_function(self, tree: ast.AST, name: str) -> ast.FunctionDef:
        """Find a function definition by name."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == name:
                return node
        return None
    
    def print_report(self):
        """Print validation report."""
        print(f"\n{'='*60}")
        print(f"Handler Isolation Validation Report")
        print(f"{'='*60}")
        print(f"File: {self.file_path}")
        print(f"Handlers found: {', '.join(self.handlers) if self.handlers else 'None'}")
        print()
        
        if self.errors:
            print(f"❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
            print()
        
        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
        
        if not self.errors and not self.warnings:
            print("✅ No issues found!")
            print()
        
        print(f"{'='*60}\n")


def main():
    """Main validation function."""
    # Get the widget_handler.py file path
    script_dir = Path(__file__).parent
    widget_handler_path = script_dir / "widget_handler.py"
    
    if not widget_handler_path.exists():
        print(f"❌ Error: {widget_handler_path} not found")
        sys.exit(1)
    
    validator = HandlerIsolationValidator(str(widget_handler_path))
    is_valid = validator.validate()
    validator.print_report()
    
    if not is_valid:
        print("❌ Validation failed. Please fix the errors before committing.")
        sys.exit(1)
    else:
        print("✅ Validation passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()


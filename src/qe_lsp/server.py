
"""
Quantum ESPRESSO Language Server Protocol implementation
"""

from __future__ import annotations

import re
from typing import Any, Optional

from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    HoverParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    SymbolKind,
    TextDocumentPositionParams,
)
from pygls.server import LanguageServer
from pygls.workspace import Document

from .data import get_parameter_doc
from .parser import QEParser, TokenType, parse

server = LanguageServer("qe-lsp", "0.1.0")


def _get_word_at_position(doc: Document, position: Position) -> tuple[str, Range]:
    """Get the word at the given position."""
    lines = doc.source.split("\n")
    if position.line >= len(lines):
        return "", Range(position, position)
    
    line = lines[position.line]
    # Find word boundaries
    start = position.character
    end = position.character
    
    # Expand left
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] in "_-"):
        start -= 1
    
    # Expand right
    while end < len(line) and (line[end].isalnum() or line[end] in "_-"):
        end += 1
    
    word = line[start:end]
    word_range = Range(
        Position(line=position.line, character=start),
        Position(line=position.line, character=end)
    )
    return word, word_range


def _get_namelist_at_position(doc: Document, position: Position) -> str | None:
    """Determine which namelist the position is in."""
    lines = doc.source.split("\n")[:position.line + 1]
    current_namelist = None
    
    for i, line in enumerate(lines):
        line_lower = line.strip().lower()
        if line_lower.startswith("&") and not line_lower.startswith("&end"):
            current_namelist = line_lower[1:].split()[0]
        elif line_lower == "&end":
            # Check if this &end is before our position
            if i < position.line:
                current_namelist = None
    
    return current_namelist


@server.feature("textDocument/completion")
def completion(params: CompletionParams | TextDocumentPositionParams) -> CompletionList | None:
    """Provide completion items."""
    doc = server.workspace.get_text_document(params.text_document.uri)
    position = params.position
    
    # Get current word and namelist context
    word, _ = _get_word_at_position(doc, position)
    namelist = _get_namelist_at_position(doc, position)
    
    items = []
    
    # If inside a namelist, offer parameter completions
    if namelist:
        from .parser import QEParser
        valid_params = QEParser.VALID_PARAMS.get(namelist, [])
        
        for param in valid_params:
            if word.lower() in param.lower():
                items.append(CompletionItem(
                    label=param,
                    kind=CompletionItemKind.Property,
                    detail=f"Parameter in &{namelist}",
                    insert_text=f"{param} = ",
                ))
    else:
        # Offer namelist and card completions
        namelists = ["control", "system", "electrons", "ions", "cell"]
        for nl in namelists:
            if word.lower() in nl.lower():
                items.append(CompletionItem(
                    label=f"&{nl}",
                    kind=CompletionItemKind.Class,
                    detail="Namelist",
                    insert_text=f"&{nl}\n\n/&end",
                    insert_text_format=2,  # Snippet
                ))
        
        cards = ["ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS", "CELL_PARAMETERS"]
        for card in cards:
            if word.upper() in card or word.lower() in card.lower():
                items.append(CompletionItem(
                    label=card,
                    kind=CompletionItemKind.Interface,
                    detail="Card",
                ))
    
    return CompletionList(is_incomplete=False, items=items)


@server.feature("textDocument/hover")
def hover(params: HoverParams | TextDocumentPositionParams) -> Hover | None:
    """Provide hover information."""
    doc = server.workspace.get_text_document(params.text_document.uri)
    position = params.position
    
    word, _ = _get_word_at_position(doc, position)
    if not word:
        return None
    
    # Check if we're in a namelist
    namelist = _get_namelist_at_position(doc, position)
    
    if namelist:
        # Look for parameter documentation
        doc_text = get_parameter_doc(namelist, word)
        if doc_text:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**{word}** (in &{namelist})\n\n{doc_text}"
                )
            )
    
    # Check for namelist documentation
    if word.lower() in ["control", "system", "electrons", "ions", "cell"]:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=f"**{word}** namelist\n\nQuantum ESPRESSO input namelist."
            )
        )
    
    # Check for card documentation
    if word.upper() in ["ATOMIC_SPECIES", "ATOMIC_POSITIONS", "K_POINTS", "CELL_PARAMETERS"]:
        from .data import get_card_doc
        doc_text = get_card_doc(word)
        if doc_text:
            return Hover(
                contents=MarkupContent(
                    kind=MarkupKind.Markdown,
                    value=f"**{word}** card\n\n{doc_text}"
                )
            )
    
    return None


@server.feature("textDocument/diagnostic")
def diagnostic(params: Any) -> list[Diagnostic]:
    """Provide diagnostics for the document."""
    doc = server.workspace.get_text_document(params.text_document.uri)
    
    # Parse the document
    result = parse(doc.source)
    
    diagnostics = []
    for error in result.errors:
        severity = DiagnosticSeverity.Error if error.severity == "error" else DiagnosticSeverity.Warning
        diagnostics.append(Diagnostic(
            range=Range(
                Position(line=error.line - 1, character=error.column - 1),
                Position(line=error.line - 1, character=error.column)
            ),
            message=error.message,
            severity=severity,
            source="qe-lsp"
        ))
    
    return diagnostics


@server.feature("textDocument/documentSymbol")
def document_symbol(params: DocumentSymbolParams) -> list[DocumentSymbol]:
    """Provide document symbols (outline)."""
    doc = server.workspace.get_text_document(params.text_document.uri)
    result = parse(doc.source)
    
    symbols = []
    
    # Add namelists
    for name, namelist in result.namelists.items():
        children = []
        for param_name, param in namelist.parameters.items():
            children.append(DocumentSymbol(
                name=param_name,
                detail=str(param.value),
                kind=SymbolKind.Property,
                range=Range(
                    Position(line=param.line - 1, character=0),
                    Position(line=param.line - 1, character=100)
                ),
                selection_range=Range(
                    Position(line=param.line - 1, character=param.column - 1),
                    Position(line=param.line - 1, character=param.column + len(param_name) - 1)
                )
            ))
        
        symbols.append(DocumentSymbol(
            name=f"&{name}",
            kind=SymbolKind.Class,
            range=Range(
                Position(line=namelist.line_start - 1, character=0),
                Position(line=namelist.line_end - 1, character=10)
            ),
            selection_range=Range(
                Position(line=namelist.line_start - 1, character=0),
                Position(line=namelist.line_start - 1, character=len(name) + 1)
            ),
            children=children
        ))
    
    # Add cards
    for name, card in result.cards.items():
        symbols.append(DocumentSymbol(
            name=name,
            kind=SymbolKind.Interface,
            range=Range(
                Position(line=card.line_start - 1, character=0),
                Position(line=card.line_end - 1, character=100)
            ),
            selection_range=Range(
                Position(line=card.line_start - 1, character=0),
                Position(line=card.line_start - 1, character=len(name))
            )
        ))
    
    return symbols


def main() -> None:
    """Start the language server."""
    server.start_io()


if __name__ == "__main__":
    main()

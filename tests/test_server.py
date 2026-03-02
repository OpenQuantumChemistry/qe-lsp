"""Tests for Quantum ESPRESSO LSP server."""

import pytest
from unittest.mock import MagicMock, patch

from qe_lsp.server import (
    server,
    main,
    _get_word_at_position,
    _get_namelist_at_position,
    completion,
    hover,
    diagnostic,
    document_symbol,
)


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_word_at_position(self):
        """Test getting word at position."""
        doc = MagicMock()
        doc.source = "ecutwfc = 60"
        word, rng = _get_word_at_position(doc, MagicMock(line=0, character=0))
        assert word == "ecutwfc"

    def test_get_word_at_position_middle(self):
        """Test getting word from middle of word."""
        doc = MagicMock()
        doc.source = "ecutwfc = 60"
        word, rng = _get_word_at_position(doc, MagicMock(line=0, character=3))
        assert word == "ecutwfc"

    def test_get_word_at_position_empty(self):
        """Test getting word from empty line."""
        doc = MagicMock()
        doc.source = "\\n"
        word, rng = _get_word_at_position(doc, MagicMock(line=0, character=0))
        assert word == ""

    def test_get_namelist_at_position(self):
        """Test getting namelist at position."""
        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
/"""
        namelist = _get_namelist_at_position(doc, MagicMock(line=1, character=0))
        assert namelist == "control"

    def test_get_namelist_at_position_outside(self):
        """Test getting namelist when outside."""
        doc = MagicMock()
        doc.source = """&control
/
calculation = 'scf'"""
        namelist = _get_namelist_at_position(doc, MagicMock(line=2, character=0))
        assert namelist is None


class TestQEServer:
    """Test QE LSP server."""

    def test_server_exists(self):
        """Test server instance exists."""
        assert server is not None
        assert server.name == "qe-lsp"
        assert server.version == "0.1.0"


class TestCompletion:
    """Test completion feature."""

    @patch.object(server, 'workspace')
    def test_completion_in_namelist(self, mock_workspace):
        """Test completion inside namelist."""
        doc = MagicMock()
        doc.source = """&control
calc
/"""
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=1, character=4)
        
        result = completion(params)
        assert result is not None

    @patch.object(server, 'workspace')
    def test_completion_outside_namelist(self, mock_workspace):
        """Test completion outside namelist."""
        doc = MagicMock()
        doc.source = "con"
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=0, character=3)
        
        result = completion(params)
        assert result is not None


class TestHover:
    """Test hover feature."""

    @patch.object(server, 'workspace')
    def test_hover_on_parameter(self, mock_workspace):
        """Test hover on parameter."""
        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
/"""
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=1, character=0)
        
        result = hover(params)
        assert result is not None

    @patch.object(server, 'workspace')
    def test_hover_empty_word(self, mock_workspace):
        """Test hover with empty word."""
        doc = MagicMock()
        doc.source = "\\n"
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        params.position = MagicMock(line=0, character=0)
        
        result = hover(params)
        assert result is None


class TestDiagnostic:
    """Test diagnostic feature."""

    @patch.object(server, 'workspace')
    def test_diagnostic_valid_input(self, mock_workspace):
        """Test diagnostic with valid input."""
        doc = MagicMock()
        doc.source = """&control
/
&system
ibrav = 1
nat = 1
ntyp = 1
ecutwfc = 30
/
&electrons
/"""
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        
        result = diagnostic(params)
        assert isinstance(result, list)

    @patch.object(server, 'workspace')
    def test_diagnostic_missing_namelist(self, mock_workspace):
        """Test diagnostic with missing namelist."""
        doc = MagicMock()
        doc.source = "&control\\n/"
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        
        result = diagnostic(params)
        assert len(result) > 0  # Should have errors


class TestDocumentSymbol:
    """Test document symbol feature."""

    @patch.object(server, 'workspace')
    def test_document_symbol(self, mock_workspace):
        """Test document symbol extraction."""
        doc = MagicMock()
        doc.source = """&control
calculation = 'scf'
/
&system
ibrav = 1
/
&electrons
/"""
        mock_workspace.get_text_document.return_value = doc
        
        params = MagicMock()
        params.text_document.uri = "test://test.in"
        
        result = document_symbol(params)
        assert isinstance(result, list)
        # Should have symbols for namelists
        assert len(result) >= 3


class TestMain:
    """Test main entry point."""

    @patch('qe_lsp.server.server.start_io')
    def test_main(self, mock_start):
        """Test main function."""
        main()
        mock_start.assert_called_once()

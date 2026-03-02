# QE-LSP

A Language Server Protocol (LSP) implementation for [Quantum ESPRESSO](https://www.quantum-espresso.org/) input files.

## Features

- **Syntax Highlighting**: Full support for namelists and cards
- **Auto-completion**: 
  - Namelist names (e.g., `&control`, `&system`)
  - Parameters within namelists
  - Valid values for parameters
  - Card names (e.g., `ATOMIC_SPECIES`, `K_POINTS`)
- **Hover Documentation**: 
  - Parameter descriptions with types and defaults
  - Possible values for enumerated parameters
  - Card format documentation with examples
- **Diagnostics**:
  - Syntax error detection
  - Unknown namelist/card warnings
  - Missing required parameter detection
  - Unknown parameter warnings
- **Document Symbols**: File structure outline with namelists, parameters, and cards

## Installation

### From PyPI (coming soon)

```bash
pip install qe-lsp
```

### From Source

```bash
git clone https://github.com/newtontech/qe-lsp.git
cd qe-lsp
pip install -e ".[dev]"
```

## Usage

### Standalone

```bash
qe-lsp
```

The server communicates via stdin/stdout using the LSP protocol.

### VS Code Extension

1. Install the QE-LSP extension (coming soon)
2. Open any `.in` file
3. The language server will automatically start

### Neovim (nvim-lspconfig)

```lua
require'lspconfig'.qe_lsp.setup{
  cmd = {'qe-lsp'},
  filetypes = {'qe', 'pwscf'},
}
```

### Emacs (lsp-mode)

```elisp
(use-package lsp-mode
  :hook (qe-mode . lsp)
  :commands lsp
  :config
  (add-to-list 'lsp-language-id-configuration '(qe-mode . "qe"))
  (lsp-register-client
   (make-lsp-client :new-connection (lsp-stdio-connection "qe-lsp")
                    :major-modes '(qe-mode)
                    :server-id 'qe-lsp)))
```

## Supported Quantum ESPRESSO Versions

This LSP server supports input file syntax for Quantum ESPRESSO v7.x and earlier versions.

### Supported Namelists

- `&control` - General control parameters
- `&system` - System description
- `&electrons` - Electronic structure parameters
- `&ions` - Ionic relaxation/MD parameters
- `&cell` - Variable-cell relaxation parameters

### Supported Cards

- `ATOMIC_SPECIES` - Atomic species and pseudopotentials
- `ATOMIC_POSITIONS` - Atomic positions in the unit cell
- `K_POINTS` - K-point grid for Brillouin zone sampling
- `CELL_PARAMETERS` - Unit cell vectors
- `OCCUPATIONS` - Occupation numbers
- `CONSTRAINTS` - Constraints for ionic coordinates
- `ATOMIC_FORCES` - External forces on atoms
- `ATOMIC_VELOCITIES` - Initial velocities for MD
- And more...

## Examples

See the `examples/` directory for sample input files:

- `scf.in` - Self-consistent field calculation
- `relax.in` - Ionic relaxation
- `vc-relax.in` - Variable-cell relaxation

## Development

### Setup

```bash
git clone https://github.com/newtontech/qe-lsp.git
cd qe-lsp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_parser.py

# Run with coverage report
pytest --cov=src/qe_lsp --cov-report=term-missing
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Type checking
mypy src

# Linting
flake8 src tests

# Security checks
bandit -r src

# Run all pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
qe-lsp/
├── src/qe_lsp/
│   ├── __init__.py      # Package exports
│   ├── parser.py        # QE input file parser
│   ├── data.py          # Parameter documentation
│   └── server.py        # LSP server implementation
├── tests/
│   ├── conftest.py      # Test fixtures
│   ├── test_parser.py   # Parser tests
│   ├── test_data.py     # Data module tests
│   └── test_server.py   # LSP server tests
├── examples/            # Example input files
├── docs/                # Additional documentation
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

### Adding New Parameters

To add documentation for new parameters:

1. Edit `src/qe_lsp/data.py`
2. Add the parameter to the appropriate namelist dictionary
3. Follow the existing format:

```python
"new_param": {
    "description": "Description of the parameter",
    "type": "string",  # or "integer", "real", "logical"
    "default": "default_value",  # optional
    "values": ["'option1'", "'option2'"],  # for enumerated types
    "required": False,
}
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run code quality checks (`pre-commit run --all-files`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Roadmap

- [x] Basic parser for namelists and cards
- [x] Hover documentation
- [x] Auto-completion
- [x] Diagnostics
- [x] Document symbols
- [ ] Go to definition (pseudopotential files)
- [ ] Code actions (quick fixes)
- [ ] Formatting support
- [ ] Additional QE packages (PHonon, EPW, etc.)
- [ ] Multi-root workspace support

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Quantum ESPRESSO](https://www.quantum-espresso.org/) - The amazing DFT package
- [pygls](https://pygls.readthedocs.io/) - Python LSP framework
- [lsprotocol](https://github.com/microsoft/lsprotocol) - LSP types

## Support

- 💬 [Discussions](https://github.com/newtontech/qe-lsp/discussions)
- 🐛 [Issue Tracker](https://github.com/newtontech/qe-lsp/issues)

---

Made with ❤️ for the computational chemistry community.

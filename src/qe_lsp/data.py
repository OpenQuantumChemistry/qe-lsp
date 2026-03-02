
"""Quantum ESPRESSO parameter documentation and data.

This module contains documentation for QE parameters used in hover
tooltips and completion items.
"""

from __future__ import annotations


# Parameter documentation for hover tooltips
PARAMETER_DOCS: dict[str, dict[str, str]] = {
    "control": {
        "calculation": """Type of calculation to perform.

Values:
  - 'scf': Self-consistent field (default)
  - 'nscf': Non-self-consistent field
  - 'bands': Band structure calculation
  - 'relax': Geometry relaxation
  - 'md': Molecular dynamics
  - 'vc-relax': Variable-cell relaxation
  - 'vc-md': Variable-cell molecular dynamics""",
        "title": "Title of the calculation for documentation purposes.",
        "verbosity": "Level of output verbosity (low, medium, high).",
        "restart_mode": "How to start the calculation (from_scratch, restart).",
        "nstep": "Maximum number of ionic steps (default: 1).",
        "tstress": "Calculate stress tensor (.true. or .false.).",
        "tprnfor": "Print forces (.true. or .false.).",
        "dt": "Time step for molecular dynamics (in Rydberg atomic units).",
        "outdir": "Directory for temporary output files.",
        "prefix": "Prefix for output files.",
        "pseudo_dir": "Directory containing pseudopotential files.",
        "etot_conv_thr": "Energy convergence threshold (in Ry).",
        "forc_conv_thr": "Force convergence threshold (in Ry/Bohr).",
        "disk_io": "Level of disk I/O (high, medium, low, none).",
    },
    "system": {
        "ibrav": "Bravais lattice index (0-14).",
        "nat": "Number of atoms in the unit cell.",
        "ntyp": "Number of types of atoms.",
        "nbnd": "Number of electronic bands to calculate.",
        "ecutwfc": "Kinetic energy cutoff for wavefunctions (in Ry).",
        "ecutrho": "Kinetic energy cutoff for charge density (in Ry).",
        "tot_charge": "Total charge of the system (default: 0).",
        "tot_magnetization": "Total magnetization of the system.",
        "occupations": "Occupation distribution (smearing, tetrahedra, fixed).",
        "smearing": "Smearing method for metals (gaussian, methfessel-paxton).",
        "degauss": "Smearing width (in Ry).",
        "nspin": "Spin polarization (1, 2, or 4).",
        "noncolin": "Perform non-collinear calculation (.true. or .false.).",
        "lspinorb": "Include spin-orbit coupling (.true. or .false.).",
    },
    "electrons": {
        "electron_maxstep": "Maximum number of SCF iterations (default: 100).",
        "scf_must_converge": "Stop if SCF does not converge (.true. or .false.).",
        "conv_thr": "SCF convergence threshold (in Ry).",
        "mixing_mode": "Charge mixing method (plain, TF, local-TF).",
        "mixing_beta": "Mixing factor (default: 0.7).",
        "mixing_ndim": "Number of iterations used in mixing (default: 8).",
        "diagonalization": "Diagonalization method (david, cg).",
        "startingpot": "Initial potential (atomic, file).",
        "startingwfc": "Initial wavefunctions (atomic, atomic+random, file, random).",
    },
    "ions": {
        "ion_dynamics": "Ion dynamics algorithm (bfgs, damp, verlet).",
        "ion_temperature": "Temperature control method.",
        "tempw": "Ionic temperature (in Kelvin).",
        "tolp": "Convergence threshold for ionic minimization.",
        "delta_t": "Time step for ionic dynamics.",
        "nraise": "Raise temperature every nraise steps.",
    },
    "cell": {
        "cell_dynamics": "Cell dynamics algorithm (none, sd, bfgs).",
        "press": "Target pressure (in KBar).",
        "wmass": "Fictitious cell mass (in atomic units).",
        "cell_factor": "Factor for unit cell scaling.",
        "press_conv_thr": "Pressure convergence threshold (in KBar).",
    },
}


def get_parameter_doc(namelist: str, param: str) -> str | None:
    """Get documentation for a parameter."""
    return PARAMETER_DOCS.get(namelist.lower(), {}).get(param.lower())

# Card documentation
CARD_DOCS: dict[str, str] = {
    "ATOMIC_SPECIES": """Defines atomic species and pseudopotentials.

Format:
  ATOMIC_SPECIES
  label  mass  pseudo_file""",
    "ATOMIC_POSITIONS": """Defines atomic positions in the unit cell.

Format:
  ATOMIC_POSITIONS { alat | bohr | angstrom | crystal }
  label  x  y  z  [if_pos(1) if_pos(2) if_pos(3)]""",
    "K_POINTS": """Defines the k-point grid.

Format:
  K_POINTS { automatic | gamma | crystal }""",
    "CELL_PARAMETERS": """Defines the unit cell vectors.

Format:
  CELL_PARAMETERS { alat | bohr | angstrom }
  v1(1) v1(2) v1(3)
  v2(1) v2(2) v2(3)
  v3(1) v3(2) v3(3)""",
}


def get_card_doc(card: str) -> str | None:
    """Get documentation for a card.

    Args:
        card: The card name (e.g., 'ATOMIC_SPECIES')

    Returns:
        Documentation string or None if not found.
    """
    return CARD_DOCS.get(card.upper())

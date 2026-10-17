# Signal Processing Framework

A desktop signal-processing application built with Python 3.11+, PySide6, NumPy, and Matplotlib. It is designed for academic coursework and allows users to generate, visualize, and manipulate discrete-time signals while keeping the mathematics explicit and reproducible.

## Features

- Load discrete-time signals from TXT files
- Export signals to TXT files
- Generate sine and cosine signals with configurable amplitude, phase, frequency, sampling rate, and duration
- Plot one or two signals simultaneously in the same workspace
- Switch between discrete and continuous-style visualization
- Perform signal operations including addition, subtraction, scalar multiplication, shifting, and folding
- Uniformly quantize samples by specifying either the number of bits or quantization levels
- Keep original signals unchanged while producing new processed results
- Use a dark-themed professional desktop interface

## Technology Stack

- Python 3.11+
- PySide6
- NumPy
- Matplotlib
- SciPy is not required for the core implementation
- pytest

## Installation

Open Windows PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the Application

```powershell
python main.py
```

## Run the Tests

```powershell
python -m pytest -v
```

## TXT File Format

The application loads and exports signals using the following format:

```text
N
sample_index sample_value
sample_index sample_value
...
```

Example:

```text
5
-2 1.5
-1 2.0
0 3.5
1 2.0
2 1.5
```

## Discrete and Continuous Visualization

- Discrete representation uses a stem plot with markers and labels for sample indices.
- Continuous representation uses a smooth interpolated or analytic curve for generated sinusoidal signals.
- The application makes a clear distinction between sampled data and a continuous-time mathematical reconstruction.

## Sampling Theorem

For a sinusoid with frequency f, the sampling frequency must satisfy:

$F_s > 2|f|$

This framework validates that condition before generating sinusoidal signals and warns the user if the rate is insufficient.

## Implemented Operations

The application currently supports:

- Addition: $y[n] = x_1[n] + x_2[n] + \dots$
- Scalar multiplication: $y[n] = A x[n]$
- Subtraction: $y[n] = x_1[n] - x_2[n]$
- Delay: $y[n] = x[n-k]$
- Advance: $y[n] = x[n+k]$
- Folding: $y[n] = x[-n]$
- Quantization: map each sample to the midpoint of one of the requested uniform levels

The implementation uses aligned sample indices and treats missing index values as zero when combining signals.

## Project Structure

```text
DSP/
├── app/
│   ├── __init__.py
│   ├── main_window.py
│   ├── theme.py
│   ├── dialogs/
│   │   ├── __init__.py
│   │   ├── about_dialog.py
│   │   ├── operation_dialogs.py
│   │   └── signal_generation_dialog.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── signal_model.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── signal_generation.py
│   │   ├── signal_io.py
│   │   └── signal_operations.py
│   └── widgets/
│       ├── __init__.py
│       ├── signal_list_widget.py
│       └── signal_plot_widget.py
├── tests/
│   ├── test_signal_generation.py
│   ├── test_signal_io.py
│   └── test_signal_operations.py
├── .gitignore
├── main.py
├── README.md
├── requirements.txt
└──
```

## Known Limitations

- The GUI is designed for desktop use; it is not intended for mobile environments.
- Continuous visualization is approximate for loaded discrete signals because the original analog waveform is not known.
- Very large sample counts are intentionally limited to keep the interface responsive.

## Notes

This project is intentionally modular so new signal-processing tasks can be added without altering the core signal model or the GUI shell.

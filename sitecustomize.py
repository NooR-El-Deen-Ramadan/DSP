import os

# Restrict BLAS thread counts to avoid out-of-memory failures on low-memory
# workstations and CI runners while importing NumPy/Matplotlib.
for _var_name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ.setdefault(_var_name, "1")

# Team rascalsdontdreamofgreedychoiceproperty

## Instructions to run
- Create python virtual environment with venv
- Install requirements with `pip install -r requirements.txt`
- Run the benchmarks with `pytest benchmark/benchmark.py`
- Alternatively, to see the outputs of the solvers, go into the respective folders in `app` and run with `python <filename>`

## Benchmarking command-line-options
- cnf-files: provide a list of .cnf files for the DPLL benchmark
- sudoku-file: provide a .csv for the sudoku benchmark
- battleship-file: provide a .csv for the battleship benchmark
- intensity[quick, full]: limit the iterations with quick; run all tests with full

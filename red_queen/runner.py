"""
This module contains the Runner class, which is responsible for
running benchmarks on a given backend using a given compiler.
"""

# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

# QASMBench Benchmark Suite:
# A low-level OpenQASM benchmark suite for NISQ evaluation and simulation.

# 06/04/2020 by Ang Li from High-Performance-Computing Group,
# ACMD, PCSD, Pacific Northwest National Laboratory (PNNL),
# Richland, WA, 99354, USA.


# Copyright © 2020, Battelle Memorial Institute

# 1.Battelle Memorial Institute (hereinafter Battelle) hereby grants permission
# to any person or entity lawfully obtaining a copy of this software and associated
# documentation files (hereinafter “the Software”) to redistribute and use the
# Software in source and binary forms, with or without modification.  Such person
# or entity may use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and may permit others to do so, subject to the
# following conditions:

# - Redistributions of source code must retain the above copyright notice, this list
# of conditions and the following disclaimers.

# - Redistributions in binary form must reproduce the above copyright notice, this list
# of conditions and the following disclaimer in the documentation and/or other materials
# provided with the distribution.

# - Other than as used herein, neither the name Battelle Memorial Institute or Battelle
# may be used in any form whatsoever without the express written consent of Battelle.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL BATTELLE OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The functions get_qubit depths, get_maximum_qubit_depths, and get_circuit_depths are from
# QASMBench's QMetric.py module and adapted to work with red-queen.
# The original source can be found at:
#
# https://github.com/pnnl/QASMBench/blob/master/metrics/QMetric.py

import sys
import os
import json
import time
import multiprocessing
import logging
import copy

from preprocessing import Preprocess
from utils import initialize_tket_pass_manager, FakeFlamingo
from progress_visualizer import ProgressVisualizer

import qiskit
from qiskit import transpile, QuantumCircuit
from qiskit import qasm2

# pylint: disable=import-error
from memory_profiler import memory_usage
import numpy as np

from pytket.qasm import circuit_to_qasm_str
from pytket.qasm import circuit_from_qasm

logger = logging.getLogger("my_logger")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logger.addHandler(console_handler)


class Runner:
    """
    Class for running benchmarks on a given backend using a given compiler.
    """

    def __init__(
        self,
        compiler_dict: dict,
        backend,
        num_runs: int,
        second_compiler_readout: str,
    ):
        """
        :param compiler_dict: dictionary of compiler info --> {"compiler": "COMPILER_NAME",
            "version": "VERSION NUM", "optimization_level": OPTIMIZATION_LEVEL}
        :param backend: name of backend to be used --> "BACKEND_NAME"
        :param num_runs: number of times to run each benchmark
        """

        self.compiler_dict = compiler_dict
        self.backend = backend
        self.num_runs = num_runs

        self.full_benchmark_list = None
        self.metric_data = {"metadata: ": self.compiler_dict, "backend": self.backend}
        self.metric_list = [
            "total_time (seconds)",
            "parsing/build_time (seconds)",
            "transpile_time (seconds)",
            "depth (gates)",
            "memory_footprint (MiB)",
        ]
        self.second_compiler_readout = second_compiler_readout
        self.progress_visualizer = None

        self.preprocess_benchmarks()

    def get_qasm_benchmark(self, qasm_name):
        benchmarking_path = os.path.join(
            os.path.dirname(__file__), "benchmarking", "benchmarks"
        )
        with open(
            os.path.join(benchmarking_path, qasm_name), "r", encoding="utf-8"
        ) as file:
            qasm = file.read()
        return qasm

    def list_files(self, directory):
        return [
            file
            for file in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, file))
        ]

    def delete_ds_store(self, directory):
        ds_store_path = os.path.join(directory, ".DS_Store")
        if os.path.exists(ds_store_path):
            os.remove(ds_store_path)

    def preprocess_benchmarks(self):
        """
        Preprocess benchmarks before running them.
        """
        benchmarking_path = os.path.join(
            os.path.dirname(__file__), "benchmarking", "benchmarks"
        )
        benchmarks = self.list_files(benchmarking_path)
        self.full_benchmark_list = []
        
        # Initialize progress visualizer
        self.progress_visualizer = ProgressVisualizer(
            total_benchmarks=len([b for b in benchmarks if b != ".DS_Store"]),
            num_runs=self.num_runs,
            compiler_info=self.compiler_dict
        )
        
        for benchmark in benchmarks:
            if benchmark == ".DS_Store":
                continue
            qasm = self.get_qasm_benchmark(benchmark)
            print(f"Converting {benchmark} to high-level circuit...")

            start_time = time.perf_counter()
            if self.compiler_dict["compiler"] == "pytket":
                circuit = circuit_from_qasm(os.path.join(benchmarking_path, benchmark))
            elif self.compiler_dict["compiler"] == "qiskit":
                circuit = QuantumCircuit.from_qasm_str(qasm)
            build_time = time.perf_counter()
            self.full_benchmark_list.append({benchmark: circuit})
            self.metric_data[benchmark] = {
                "total_time (seconds)": [],
                "parsing/build_time (seconds)": [build_time - start_time],
                "transpile_time (seconds)": [],
                "depth (gates)": [],
                "memory_footprint (MiB)": [],
            }

    def run_benchmarks(self):
        """
        Run all benchmarks in full_benchmark_list.
        """
        if self.progress_visualizer:
            self.progress_visualizer.start_benchmarking()
        
        for benchmark in self.full_benchmark_list:
            benchmark_name = list(benchmark.keys())[0]
            
            if self.progress_visualizer:
                self.progress_visualizer.start_benchmark(benchmark_name)

            for run_num in range(self.num_runs):
                if self.progress_visualizer:
                    self.progress_visualizer.start_run(run_num + 1)
                
                self.run_benchmark(benchmark)

            self.calculate_aggregate_statistics(benchmark)
            
            if self.progress_visualizer:
                self.progress_visualizer.complete_benchmark(
                    benchmark_name, 
                    self.metric_data[benchmark_name]
                )
        
        if self.progress_visualizer:
            self.progress_visualizer.print_summary()
            
        self.save_results()

    def save_results(self):
        results_dir = os.path.join(os.path.dirname(__file__), "results")

        # Check if the directory exists and create it if it doesn't
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)

        self.delete_ds_store("results")
        run_number = len(self.list_files("results")) + 1

        if self.second_compiler_readout == "true":
            results_path = os.path.join(
                os.path.dirname(__file__),
                "results",
                f"results_run{run_number - 1}.json",
            )

            with open(results_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)
            data.append(self.metric_data)
            with open(results_path, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, indent=2)
        else:
            results_path = os.path.join(
                os.path.dirname(__file__), "results", f"results_run{run_number}.json"
            )
            with open(results_path, "w", encoding="utf-8") as json_file:
                json.dump([self.metric_data], json_file, indent=2)
        
        if self.progress_visualizer:
            self.progress_visualizer.info(f"Results saved to: {results_path}")

    def transpile_in_process(self, benchmark: QuantumCircuit, optimization_level: int):
        """
        Transpile a circuit in a separate process to get memory usage.

        :param benchmark: benchmark to be transpiled
        :param optimization_level: level of optimization to be used
        """
        backend = FakeFlamingo(qubits=200, target=self.backend, distance=11) #choose_backend(self.backend)  
        start_mem = memory_usage(max_usage=True)
        if self.compiler_dict["compiler"] == "pytket":
            tket_pm = initialize_tket_pass_manager(backend, optimization_level)
            tket_pm.apply(benchmark)
        else:
            transpile(
                benchmark, backend, optimization_level=optimization_level
            )

        end_mem = memory_usage(max_usage=True)
        memory = end_mem - start_mem
        return memory

    def profile_func(self, benchmark: QuantumCircuit):
        """
        Profile a function to get memory usage.

        :param benchmark: benchmark to be run
        """
        # To get accurate memory usage, need to multiprocess transpilation
        with multiprocessing.Pool(1) as pool:
            memory = pool.apply(
                self.transpile_in_process,
                (benchmark, self.compiler_dict["optimization_level"]),
            )
        return memory

    def run_benchmark(self, benchmark: dict):
        """
        Run a single benchmark.

        :param benchmark: Name and circuit of benchmark to be run
        """

        benchmark_name = list(benchmark.keys())[0]
        benchmark_circuit = list(benchmark.values())[0]

        #############################
        # MEMORY FOOTPRINT
        #############################

        # Add memory_footprint to dictionary corresponding to this benchmark
        if self.progress_visualizer:
            self.progress_visualizer.update_progress("📊 Calculating memory footprint...", "\033[96m")
        
        # Multiprocesss transpilation to get accurate memory usage
        # Must deepcopy benchmark_circuit to avoid compiling the same circuit multiple times
        memory = self.profile_func(copy.deepcopy(benchmark_circuit))
        self.metric_data[benchmark_name]["memory_footprint (MiB)"].append(memory)

        backend = backend = FakeFlamingo(qubits=200, target=self.backend, distance=11)

        #############################
        # TRANSPILATION TIME
        #############################

        if self.progress_visualizer:
            self.progress_visualizer.update_progress("⚡ Calculating transpilation time...", "\033[93m")
        
        # to get accurate time measurement, need to run transpilation without profiling
        benchmark_copy = copy.deepcopy(benchmark_circuit)
        if self.compiler_dict["compiler"] == "pytket":
            tket_pm = initialize_tket_pass_manager(
                backend, optimization_level=self.compiler_dict["optimization_level"]
            )
            start_time = time.perf_counter()
            tket_pm.apply(benchmark_copy)

        else:
            start_time = time.perf_counter()
            transpiled_circuit = transpile(
                benchmark_copy,
                backend=backend,
                optimization_level=self.compiler_dict["optimization_level"],
            )

        end_time = time.perf_counter()
        self.metric_data[benchmark_name]["transpile_time (seconds)"].append(
            end_time - start_time
        )
        self.metric_data[benchmark_name]["total_time (seconds)"].append(
            end_time
            - start_time
            + +self.metric_data[benchmark_name]["parsing/build_time (seconds)"][-1]
            + self.metric_data[benchmark_name]["transpile_time (seconds)"][-1]
        )

        #############################
        # DEPTH
        #############################

        if self.progress_visualizer:
            self.progress_visualizer.update_progress("🔍 Calculating circuit depth...", "\033[95m")
        if self.compiler_dict["compiler"] == "pytket":
            transpiled_circuit = benchmark_copy
            qasm_string = circuit_to_qasm_str(transpiled_circuit)
        else:
            # If the qiskit version is less than 1.0 use the old qasm method
            if int(qiskit.__version__[0]) < 1:
                qasm_string = transpiled_circuit.qasm()
            else:
                qasm_string = qasm2.dumps(transpiled_circuit)
        processed_qasm = Preprocess(qasm_string)
        depth = self.get_circuit_depth(processed_qasm)
        self.metric_data[benchmark_name]["depth (gates)"].append(depth)

    def get_circuit_depth(self, benchmark):
        self.get_qubit_depths(benchmark)
        _, depth = self.get_maximum_qubit_depth(benchmark)
        return depth

    def get_qubit_depths(self, benchmark):
        """
        Get depth of a specific qubit
        :return:
        """
        qubit_depth = {}
        for gate in benchmark.processed_qasm:
            op = benchmark.get_op(gate)
            if op not in benchmark.GATE_TABLE:
                print(
                    f"{op} not counted towards evaluation. Not a valid from default gate tables"
                )
                continue
            qubit_id = benchmark.get_qubit_id(gate)
            for qubit in qubit_id:
                if qubit not in qubit_depth:
                    qubit_depth[qubit] = 0
                qubit_depth[qubit] += 1
        return qubit_depth

    def get_maximum_qubit_depth(self, benchmark):
        """
        Get maximum qubit depth
        :return:
        """
        qubit_depths = self.get_qubit_depths(benchmark)
        max_value = max(qubit_depths.values())  # maximum value
        max_keys = [k for k, v in qubit_depths.items() if v == max_value][0]
        # getting all keys containing the `maximum`
        return max_keys, max_value

    def calculate_aggregate_statistics(self, benchmark):
        """
        Calculate aggregate statistics on metrics.
        """
        # For each metric, calculate mean, median, range, variance, standard dev
        benchmark_name = list(benchmark.keys())[0]
        self.metric_data[benchmark_name]["aggregate"] = {}
        for metric in self.metric_list:
            self.metric_data[benchmark_name]["aggregate"][metric] = {}
            self.metric_data[benchmark_name]["aggregate"][metric]["mean"] = np.mean(
                np.array(self.metric_data[benchmark_name][metric], dtype=float)
            )
            self.metric_data[benchmark_name]["aggregate"][metric]["median"] = np.median(
                np.array(self.metric_data[benchmark_name][metric], dtype=float)
            )
            self.metric_data[benchmark_name]["aggregate"][metric]["range"] = (
                np.min(np.array(self.metric_data[benchmark_name][metric], dtype=float)),
                np.max(np.array(self.metric_data[benchmark_name][metric], dtype=float)),
            )
            self.metric_data[benchmark_name]["aggregate"][metric]["variance"] = np.var(
                np.array(self.metric_data[benchmark_name][metric], dtype=float)
            )
            self.metric_data[benchmark_name]["aggregate"][metric][
                "standard_deviation"
            ] = np.std(np.array(self.metric_data[benchmark_name][metric], dtype=float))


if __name__ == "__main__":

    targets = ["heavy_hex", "all_to_all", "linear"]

    for target in targets:

        runner = Runner(
            {
                "compiler": str(sys.argv[1]),
                "version": str(sys.argv[2]),
                "optimization_level": int(sys.argv[3]),
            },
            target,
            int(sys.argv[5]),
            str(sys.argv[6]),
        )
        runner.run_benchmarks()

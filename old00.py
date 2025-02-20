
# pipeline_simulation.py
# import the m5 (gem5) library created when gem5 is built
import m5
import re
# import m5.stats

# import all of the SimObjects
from m5.objects import *
# from m5.stats import dump, reset, initSimStats
from m5.stats import *

# Add the common scripts to our path
# m5.util.addToPath("../../")
m5.util.addToPath("../gem5/configs/common")

# import the caches which we made
from caches import *

# import the SimpleOpts module
# from common import SimpleOpts
# from common import *
import SimpleOpts

# root = Root(full_system=False)


# Default to running 'hello', use the compiled ISA to find the binary
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
# default_binary = os.path.join(
#     thispath,
#     "../../../",
#     "tests/test-progs/hello/bin/x86/linux/hello",
# )
default_binary = os.path.join(
    thispath,
    "../gem5/",
    "tests/test-progs/hello/bin/x86/linux/hello",
)
# m5.stats.init()
# m5.stats.enable()
print(thispath)

# Binary to execute
SimpleOpts.add_option("binary", nargs="?", default=default_binary)

# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()

# create the system we are going to simulate
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '2GHz'  # Set the system clock speed
system.clk_domain.voltage_domain = VoltageDomain()

# Memory configuration
system.mem_mode = 'timing'  # Use timing mode to simulate more realistic delays
# system.mem_ranges = [AddrRange('512MB')]  # Allocate memory range for the system
system.mem_ranges = [AddrRange('8GB')]  # Allocate memory range for the system

# CPU configuration
system.cpu = DerivO3CPU()  # Out-of-order CPU to show pipeline stages
system.cpu.numThreads = 1

# Create the interrupt controller for the CPU
system.cpu.createInterruptController()

# L1 and L2 caches for realistic memory behavior
system.cpu.icache = L1ICache(args)  # Instruction cache
system.cpu.dcache = L1DCache(args)  # Data cache
system.cpu.l2cache = L2Cache(args)  # L2 cache

# Connecting caches to CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2bus)

# Memory bus
system.membus = SystemXBar()

# Connecting caches to the memory bus
system.l2cache.connectMemSideBus(system.membus)
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# Connecting L2 cache to the memory bus
system.cpu.l2cache.connectCPUSideBus(system.membus)

# Memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()  # Simulate DDR3 memory
# system.mem_ctrl.range = system.mem_ranges[0]
# system.mem_ctrl.port = system.membus.master
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Load the binary payload
# binary_path = 'configs/example/hello'  # Path to the 'hello' binary
binary_path = 'hello'  # Path to the 'hello' binary
# system.workload = SEWorkload.init_compatible(binary_path)
system.workload = SEWorkload.init_compatible(default_binary)

# Set up the process for the binary execution
process = Process()
# process.cmd = [binary_path]  # Command to run the 'hello' binary
process.cmd = [args.binary]
system.cpu.workload = process  # Assign the process to the CPU
system.cpu.createThreads()  # Create thread(s) for the workload

# Root system
root = Root(full_system=False, system=system)

# Instantiate and start the simulation
m5.instantiate()
print("Starting gem5 simulation...")

# Run the simulation
exit_event = m5.simulate()

# Output the simulation result
print(f"Exiting at tick {m5.curTick()} because {exit_event.getCause()}")

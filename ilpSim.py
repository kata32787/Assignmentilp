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

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
# system.clk_domain.clock = "750MHz"
system.clk_domain.clock = "3GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("512MiB")]  # Create an address range

# Create a simple CPU
system.cpu = DerivO3CPU()

# Create a branch predictor
system.cpu.branchPred = BranchPredictor()

# Configure superscalar parameters
system.cpu.fetchWidth = 8  # Fetch up to 8 instructions per cycle
system.cpu.decodeWidth = 8  # Decode up to 8 instructions per cycle
system.cpu.renameWidth = 8  # Rename up to 8 instructions per cycle
system.cpu.dispatchWidth = 8  # Dispatch up to 8 instructions per cycle
system.cpu.issueWidth = 8  # Issue up to 8 instructions per cycle
system.cpu.commitWidth = 8  # Commit up to 8 instructions per cycle

# Enable multithreading
system.cpu.numThreads = 2  # Set the number of threads (e.g., 2 threads)

# Create an L1 instruction and data cache
system.cpu.icache = L1ICache(args)
system.cpu.dcache = L1DCache(args)

# Connect the instruction and data caches to the CPU
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

# Hook the CPU ports up to the l2bus
system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

# Create an L2 cache and connect it to the l2bus
system.l2cache = L2Cache(args)
system.l2cache.connectCPUSideBus(system.l2bus)

# Create a memory bus
system.membus = SystemXBar()

# Connect the L2 cache to the membus
system.l2cache.connectMemSideBus(system.membus)

# create the interrupt controller for the CPU
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

system.workload = SEWorkload.init_compatible(args.binary)



# ===================================================================================   Single thread config start
# ===================================================================================

# # Create a process for a simple "Hello World" application
# process = Process()
# # Set the command
# # cmd is a list which begins with the executable (like argv)
# print([args.binary])
# process.cmd = [args.binary]


# # Set the cpu to use the process as its workload and create thread contexts
# system.cpu.workload = process

# ===================================================================================   Single thread config end
# ===================================================================================


# ===================================================================================   Multi threading config start
# ===================================================================================

# Create processes for each thread
process1 = Process()
process1.cmd = [args.binary]  # Use the same binary for both threads
# process1.cwd = os.getcwd()  # Set the working directory

process2 = Process()
process2.cmd = [args.binary]  # Use the same binary for both threads
# process2.cwd = os.getcwd()  # Set the working directory

# Assign the processes to the CPU's workload
system.cpu.workload = [process1, process2]  # Assign multiple processes

# ===================================================================================   Multi threading config end
# ===================================================================================

system.cpu.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

m5.stats.reset() # Reset statistics after dumping

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

# print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
print("=== Cache Stats ===")

print("=== Dumping Cache Statistics ===")
m5.stats.dump()  # Dump all collected statistics

# root = Root(full_system=False, system=system)

# Function to parse stats.txt and extract cache hits and misses
def parse_stats(filename):
    stats = {}
    with open(filename, 'r') as file:
        for line in file:
            match = re.match(r'(^.*\bhits\b.*|\bmisses\b.*):\s*(\d+)', line)
            if match:
                key = match.group(1).strip()
                value = int(match.group(2))
                stats[key] = value
    return stats

# Parse the stats.txt file
# stats = parse_stats('stats.txt')

# print(vars(system.cpu.icache))
print(' ')

m5.stats.reset() # Reset statistics after dumping

print(f"End of Simulation!")

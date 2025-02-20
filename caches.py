
import m5
from m5.objects import Cache

# Add the common scripts to our path
# m5.util.addToPath("../../")
m5.util.addToPath("../gem5/configs/common")

# import SimpleOpts
# from common import SimpleOpts
import SimpleOpts

# Some specific options for caches
# For all options see src/mem/cache/BaseCache.py


class L1Cache(Cache):
    """Simple L1 Cache with default values"""

    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20

    def __init__(self, options=None):
        super().__init__()
        # self.addStat("overallHits")  # Enable hits tracking
        # self.addStat("overallMisses")  # Enable misses tracking
        pass

    def connectBus(self, bus):
        """Connect this cache to a memory-side bus"""
        self.mem_side = bus.cpu_side_ports

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU-side port
        This must be defined in a subclass"""
        raise NotImplementedError


class L1ICache(L1Cache):
    """Simple L1 instruction cache with default values"""

    # Set the default size
    size = "16KiB"

    SimpleOpts.add_option(
        "--l1i_size", help=f"L1 instruction cache size. Default: {size}"
    )

    def __init__(self, opts=None):
        super().__init__(opts)
        if not opts or not opts.l1i_size:
            return
        self.size = opts.l1i_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU icache port"""
        self.cpu_side = cpu.icache_port


class L1DCache(L1Cache):
    """Simple L1 data cache with default values"""

    # Set the default size
    size = "64KiB"

    SimpleOpts.add_option(
        "--l1d_size", help=f"L1 data cache size. Default: {size}"
    )

    def __init__(self, opts=None):
        super().__init__(opts)
        if not opts or not opts.l1d_size:
            return
        self.size = opts.l1d_size

    def connectCPU(self, cpu):
        """Connect this cache's port to a CPU dcache port"""
        self.cpu_side = cpu.dcache_port


class L2Cache(Cache):
    """Simple L2 Cache with default values"""

    # Default parameters
    size = "256KiB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12

    SimpleOpts.add_option("--l2_size", help=f"L2 cache size. Default: {size}")

    def __init__(self, opts=None):
        super().__init__()
        if not opts or not opts.l2_size:
            return
        self.size = opts.l2_size

    def connectCPUSideBus(self, bus):
        self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
        self.mem_side = bus.cpu_side_ports

# print("\n=== Cache Statistics ===")
# print(f"L1 Instruction Cache Hits: {system.cpu.icache.stats.hits.value}")
# print(f"L1 Instruction Cache Misses: {system.cpu.icache.stats.misses.value}")
# print(f"L1 Data Cache Hits: {system.cpu.dcache.stats.hits.value}")
# print(f"L1 Data Cache Misses: {system.cpu.dcache.stats.misses.value}")
# print(f"L2 Cache Hits: {system.l2cache.stats.hits.value}")
# print(f"L2 Cache Misses: {system.l2cache.stats.misses.value}")

# --l1i_size=8KiB --l1d_size=16KiB --l2_size=128KiB
# --l1i_size=64KiB --l1d_size=128KiB --l2_size=1MB
# --l1i_size=32KiB --l1d_size=64KiB --l2_size=512KiB
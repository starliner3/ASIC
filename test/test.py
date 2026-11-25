# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset (button not pressed)
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

    # After reset the dice should show 1
    assert int(dut.uo_out.value) == 1, "dice should start at 1 after reset"

    # Hold the roll button: the dice should cycle 1..6 and wrap
    dut._log.info("Rolling")
    dut.ui_in.value = 1
    await ClockCycles(dut.clk, 5)  # let the button signal settle

    seen = []
    for _ in range(14):
        await ClockCycles(dut.clk, 1)
        seen.append(int(dut.uo_out.value))

    for value in seen:
        assert 1 <= value <= 6, f"dice showed {value}, expected 1 to 6"
    for previous, current in zip(seen, seen[1:]):
        assert current == previous % 6 + 1, f"{previous} should be followed by {previous % 6 + 1}, got {current}"
    assert set(seen) == {1, 2, 3, 4, 5, 6}, "all six faces should appear"

    # Release the button: the dice should stop and hold its value
    dut._log.info("Released")
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 5)  # let the release pass through the synchroniser
    held = int(dut.uo_out.value)
    assert 1 <= held <= 6

    await ClockCycles(dut.clk, 20)
    assert int(dut.uo_out.value) == held, "dice should hold its value after release"

/*
 * Copyright (c) 2024 starliner3
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // The button comes from outside and isn't in step with the clock,
    // so pass it through two flip-flops before using it.
    reg [1:0] btn_sync;
    always @(posedge clk) begin
        btn_sync <= {btn_sync[0], ui_in[0]};
    end
    wire roll = btn_sync[1];

    // The dice value, 1 to 6
    reg [2:0] count;
    always @(posedge clk) begin
        if (!rst_n)
            count <= 3'd1;           // reset: start at 1
        else if (roll) begin         // button held: keep counting
            if (count == 3'd6)
                count <= 3'd1;       // wrap from 6 back to 1
            else
                count <= count + 1;
        end
        // button released: nothing assigned, so count holds its value
    end

    // Dice value goes out on uo[2:0], the other 5 pins are 0
    assign uo_out = {5'b0, count};

    // The bidirectional pins aren't used
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, ui_in[7:1], uio_in, 1'b0};

endmodule

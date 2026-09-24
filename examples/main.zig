const std = @import("std");

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const args = try std.process.argsAlloc(gpa.allocator());
    defer std.process.argsFree(gpa.allocator(), args);

    if (args.len < 2) {
        std.debug.print("usage: {s} NAME\n", .{args[0]});
        return error.MissingArgument;
    }
    const stdout = std.io.getStdOut().writer();
    try stdout.print("Hello, {s}!\n", .{args[1]});
}

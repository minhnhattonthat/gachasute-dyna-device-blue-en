-- Log every event-script op the interpreter runs: "OP <op> <pc> <newpc> <ret>" once per distinct (pc, newpc).
-- Hooks the dispatch loop (docs/re/debug.md): 0x0801E5EC calls handler(&pc) with pc in [sp]; 0x0801E5F0 is the
-- return (r0 = nonzero to yield). Use beside warp.lua to learn opcode lengths and jumps (tools/script.py checks
-- its parse against these logs: every logged pc must be an op boundary).
--   emu.py ROM --out DIR --script tools/debug/warp.lua --script tools/lua/opstep.lua --var "SCENE='x'"
local MEM = emu.memType.gbaMemory
local cur_pc, cur_op = nil, nil
local seen = {}
L.on_exec(0x0801E5EC, 0x0801E5EC, function()
  local sp = emu.getState()["cpu.r13"]
  cur_pc = emu.read32(sp, MEM)
  cur_op = emu.read16(cur_pc, MEM)
end)
L.on_exec(0x0801E5F0, 0x0801E5F0, function()
  if not cur_pc then return end
  local s = emu.getState()
  local np = emu.read32(s["cpu.r13"], MEM)
  local key = cur_pc * 4096 + (np - cur_pc + 2048)
  if not seen[key] then
    seen[key] = true
    L.log(string.format("OP %d %08X %08X %d", cur_op, cur_pc, np, s["cpu.r0"]))
  end
  cur_pc = nil
end)

-- Probe: from a savestate, poke story flags (POKES = "95=3 75=1"), log every script start and mode change, and play
-- ROUTE. Used to find which flags the ending/day-end dispatcher (0x080522D4) reads; docs/re/debug.md.
--   emu.py ROM --state-in work/states/menu_quit.mss --out work/qa/probe --script tools/debug/probe_flags.lua
--          --var "POKES='95=3'" --var "PROUTE='6 a;600 -'" --frames 1200
local MEM = emu.memType.gbaMemory
local FLAGS = 0x0200A300
local function set_flag(n, v)
  local a = FLAGS + (n >> 2)
  local sh = (n & 3) * 2
  local b = emu.read(a, MEM)
  emu.write(a, (b & ~(3 << sh) & 0xFF) | ((v & 3) << sh), MEM)
end
local poked = false
L.on_frame(function(n)
  if not poked then
    poked = true
    for k, v in (POKES or ""):gmatch("(%d+)=(%d+)") do set_flag(tonumber(k), tonumber(v)) end
    for step in (PROUTE or "60 -"):gmatch("[^;]+") do
      local f, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
      L.press(spec, tonumber(f))
    end
  end
  if n % 30 == 0 then
    local m = emu.read32(0x03001AD0, MEM)
    if m ~= LASTMODE then L.log(string.format("MODE %d f%d", m, n)); LASTMODE = m end
  end
end)
L.on_exec(0x0801A9D4, 0x0801A9D4, function()
  local s = emu.getState()
  L.log(string.format("SCRIPT %d lr=%08X room=%d f%d", s["cpu.r1"], s["cpu.r14"] or 0,
    emu.read16(0x02001C54, MEM), L.frame))
end)
L.on_exec(0x080522D4, 0x080522D4, function()
  L.log(string.format("RESUME f%d", L.frame))
  for k, v in (RESUME_POKES or ""):gmatch("(%d+)=(%d+)") do set_flag(tonumber(k), tonumber(v)) end
end)
L.on_exec(0x08013488, 0x08013488, function() L.log(string.format("TEXT %08X f%d", emu.getState()["cpu.r0"], L.frame)) end)

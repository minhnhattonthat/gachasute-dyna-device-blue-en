-- Log every call of the game's LZSS decompressor (0x08005680): frame, source, destination.
--   emu.py ROM --out DIR --frames N --script tools/lua/lzss_log.lua
local shown = false
L.on_exec(0x08005680, 0x08005680, function()
  local st = emu.getState()
  if not shown then
    local ks = {}
    for k, _ in pairs(st) do
      if string.find(k, "cpu") then ks[#ks + 1] = k end
    end
    table.sort(ks)
    L.log("keys: " .. table.concat(ks, " ", 1, math.min(#ks, 40)))
    shown = true
  end
  local r0 = st["cpu.r0"] or st["cpu.r[0]"] or st["cpu.R0"]
  local r1 = st["cpu.r1"] or st["cpu.r[1]"] or st["cpu.R1"]
  L.log(string.format("f%d lzss src=%s dst=%s", L.frame,
    r0 and string.format("%08X", r0) or "?", r1 and string.format("%08X", r1) or "?"))
end)

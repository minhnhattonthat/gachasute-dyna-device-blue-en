-- Dump work RAM (0x02000000-0x0203FFFF) and IWRAM to DUMP_PREFIX.ewram / .iwram on frame DUMP_AT (default 0 =
-- never) and when warp.lua logs HOLD done. Run beside warp.lua:  --var "DUMP_PREFIX='work/qa/x/ram'" --var "DUMP_AT=2400"
local MEM = emu.memType.gbaMemory
local prefix = DUMP_PREFIX or "ram"
local function dump()
  local f = io.open(prefix .. ".ewram", "wb")
  for a = 0x02000000, 0x0203FFFF do f:write(string.char(emu.read(a, MEM, false))) end
  f:close()
  f = io.open(prefix .. ".iwram", "wb")
  for a = 0x03000000, 0x03007FFF do f:write(string.char(emu.read(a, MEM, false))) end
  f:close()
  L.log("RAMDUMP " .. prefix .. " f" .. L.frame)
end
L.on_frame(function(n)
  if DUMP_AT and n == DUMP_AT then dump() end
end)

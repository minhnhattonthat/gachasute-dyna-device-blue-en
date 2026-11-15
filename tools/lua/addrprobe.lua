-- Address-lookup probe: on each call of the field setter 0x0800E12C (r0 = field, r1 = text) from the postal-code
-- lookup 0x0803B75C, log the field number and the 64 text bytes; on each call of the lookup builder, log the
-- matched town record address (0x0803B6DC returns it in r0, caught at 0x0803B790). Run beside warp.lua.
local MEM = emu.memType.gbaMemory
local function hex(a, n)
  local t = {}
  for i = 0, n - 1 do t[#t + 1] = string.format("%02X", emu.read(a + i, MEM, false)) end
  return table.concat(t)
end
local function reg(name)
  local s = emu.getState()
  return s["cpu.r" .. name] or s["cpu.registers.r" .. name] or 0
end
L.on_exec(0x0800E12C, 0x0800E12C, function()
  L.log(string.format("SETFIELD f=%d text=%s", reg(0), hex(reg(1), 64)))
end)
L.on_exec(0x0803B6DC, 0x0803B6DC, function()
  L.log(string.format("PARSE in=%s", hex(reg(0), 12)))
end)
L.on_exec(0x0803B790, 0x0803B790, function()
  local r0 = reg(0)
  L.log(string.format("RECORD %08X %s", r0, r0 ~= 0 and hex(r0, 23) or ""))
end)

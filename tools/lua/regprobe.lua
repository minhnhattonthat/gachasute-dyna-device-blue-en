-- String-register probe (phase 5 register widths): on every call of the text expander 0x0801328C, log the eight
-- registers at 0x02002BD4 + 8n once per distinct content:
--   REG n raw=<8 bytes hex> [-> <addr> <bytes hex up to NUL>]
-- A register holding a pointer (u32 at +0 in 0x02/0x03/0x08 space) is followed to its string. Run beside warp.lua.
local MEM = emu.memType.gbaMemory
local REGS = 0x02002BD4
local seen = {}
local function r8(a) return emu.read(a, MEM, false) end
local function r32(a) return emu.read32(a, MEM, false) end
local function bytes_at(a, n, stop0)
  local t = {}
  for i = 0, n - 1 do
    local b = r8(a + i)
    if stop0 and b == 0 then break end
    t[#t + 1] = string.format("%02X", b)
  end
  return table.concat(t)
end
L.on_exec(0x0801328C, 0x0801328C, function()
  for n = 0, 7 do
    local a = REGS + 8 * n
    local raw = bytes_at(a, 8, false)
    local line = string.format("REG %d raw=%s", n, raw)
    local p = r32(a)
    local hi = p >> 24
    if hi == 0x02 or hi == 0x03 or hi == 0x08 then
      line = line .. string.format(" -> %08X %s", p, bytes_at(p, 48, true))
    end
    if not seen[line] then seen[line] = true; L.log(line) end
  end
end)

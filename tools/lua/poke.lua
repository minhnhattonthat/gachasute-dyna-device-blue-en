-- Write bytes into memory every frame from POKE_FROM (default 0) to POKE_TO (default 400): QA of screens that
-- show saved data, e.g. the profile address (0x02000B44, tools/addrdb.py) on the PDA profile card.
--   --var "POKE_ADDR=0x02000B44" --var "POKE_HEX='546F6B796F00'"
local MEM = emu.memType.gbaMemory
local from, to = POKE_FROM or 0, POKE_TO or 400
local bytes = {}
for h in (POKE_HEX or ""):gmatch("%x%x") do bytes[#bytes + 1] = tonumber(h, 16) end
L.on_frame(function(n)
  if n < from or n > to then return end
  for i, b in ipairs(bytes) do emu.write(POKE_ADDR + i - 1, b, MEM) end
end)

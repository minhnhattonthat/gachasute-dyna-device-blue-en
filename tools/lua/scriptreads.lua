-- Log each PC that reads the event-script file (ROM 0x702BC4..0x747B34), with the lowest and highest
-- address it touched and the frame it first did, flushed every 60 frames.
--   emu.py ROM --out DIR --script tools/lua/scriptreads.lua [--var "LO=0x08702BC4"] [--var "HI=0x08747B34"]
local lo = LO or 0x08702BC4
local hi = HI or 0x08747B34
local seen = {}
local order = {}
L.on_read(lo, hi, function(addr)
  local pc = L.pc()
  local e = seen[pc]
  if not e then
    e = {min = addr, max = addr, first = L.frame, n = 0}
    seen[pc] = e
    order[#order + 1] = pc
  end
  e.n = e.n + 1
  if addr < e.min then e.min = addr end
  if addr > e.max then e.max = addr end
end)
L.on_frame(function(n)
  if n % 600 == 0 then
    for _, pc in ipairs(order) do
      local e = seen[pc]
      L.log(string.format("f%d pc=%08X first=f%d n=%d min=%08X max=%08X", n, pc, e.first, e.n, e.min, e.max))
    end
  end
end)

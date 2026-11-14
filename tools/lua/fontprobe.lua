-- Font probe (phase 5): which glyph sizes the text-object renderer 0x080049AC draws with, and the font
-- pointer table at 0x020001F0 (one u32 per size). Run beside warp.lua:
--   emu.py ROM --out DIR --script tools/debug/warp.lua --var "SCENE='intro'" --script tools/lua/fontprobe.lua
local sizes = {[0x08004A1A] = "size1 (16x16, 26 B/glyph)", [0x08004A84] = "size3 (8x8, 10 B/glyph)",
               [0x08004AC4] = "size4 (8x16, 18 B/glyph)"}
local count = {}
for a, name in pairs(sizes) do
  L.on_exec(a, a, function()
    count[name] = (count[name] or 0) + 1
  end)
end
local function rd32(a)
  return emu.read32(a, emu.memType.gbaMemory, false)
end
L.on_frame(function(n)
  if n % 600 == 0 then
    local t = {}
    for i = 0, 5 do t[#t + 1] = string.format("%08X", rd32(0x020001F0 + 4 * i)) end
    L.log(string.format("f%d fonttab %s", n, table.concat(t, " ")))
    for name, c in pairs(count) do L.log(string.format("f%d %s: %d", n, name, c)) end
  end
end)

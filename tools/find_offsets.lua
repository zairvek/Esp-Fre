-- FF Offset Finder - auto deteccion HP, solo lectura
gg.setVisible(false)

gg.alert("Paso 1: Asegurate de estar EN PARTIDA con HP completo.\nToca OK cuando estes listo.")

gg.clearResults()
gg.searchNumber("1;1000", gg.TYPE_FLOAT, false, gg.SIGN_BETWEEN, 0, -1)
local inicio = gg.getResultCount()
gg.toast("Capturados " .. inicio .. " valores. Ahora recibe dano...")

gg.alert("Recibe dano ahora.\nCuando tu HP cambie, toca OK.")

gg.searchNumber("", gg.TYPE_FLOAT, false, gg.SIGN_DECREASED, 0, -1)
local tras_dano = gg.getResultCount()
gg.toast("Despues del dano: " .. tras_dano .. " candidatos")

local rondas = 0
while tras_dano > 20 and rondas < 5 do
    gg.alert("Todavia " .. tras_dano .. " resultados.\nRecibe mas dano y toca OK.")
    gg.searchNumber("", gg.TYPE_FLOAT, false, gg.SIGN_DECREASED, 0, -1)
    tras_dano = gg.getResultCount()
    rondas = rondas + 1
end

local results = gg.getResults(math.min(tras_dano, 15))
local msg = "DIRECCIONES HP (" .. #results .. "):\n\n"
for i, r in ipairs(results) do
    msg = msg .. string.format("0x%X  =  %.1f\n", r.address, tonumber(r.value) or 0)
end
msg = msg .. "\nSaca foto y mandala."
gg.alert(msg)

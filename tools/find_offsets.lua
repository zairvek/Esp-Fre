-- FF Offset Finder — auto detección de HP, solo lectura
-- 1. Corré el script dentro de la partida
-- 2. Tocá OK cuando estés listo → recibí daño → tocá OK de nuevo
-- 3. Repetí hasta quedar con pocas direcciones

gg.setVisible(false)

-- Paso 1: capturar estado inicial (todos los floats entre 1 y 1000)
gg.alert("Paso 1: Vas a tomar una foto del estado actual.\nASSEGURATE de estar EN PARTIDA y con HP completo.\nTocá OK cuando estés listo.")

gg.clearResults()
gg.searchNumber("1;1000", gg.TYPE_FLOAT, false, gg.SIGN_BETWEEN, 0, -1)
local inicio = gg.getResultCount()
gg.toast("Capturados " .. inicio .. " valores. Ahora recibí daño...")

-- Paso 2: esperar que el usuario reciba daño
gg.alert("Recibí daño ahora.\nCuando tu HP cambie, tocá OK.")

-- Paso 3: refinar — valores que disminuyeron
gg.searchNumber("", gg.TYPE_FLOAT, false, gg.SIGN_DECREASED, 0, -1)
local tras_daño = gg.getResultCount()
gg.toast("Después del daño: " .. tras_daño .. " candidatos")

-- Repetir refinación si hay demasiados
local rondas = 0
while tras_daño > 20 and rondas < 5 do
    gg.alert("Todavía " .. tras_daño .. " resultados.\nRecibí más daño y tocá OK.")
    gg.searchNumber("", gg.TYPE_FLOAT, false, gg.SIGN_DECREASED, 0, -1)
    tras_daño = gg.getResultCount()
    rondas = rondas + 1
end

-- Mostrar resultados finales
local results = gg.getResults(math.min(tras_daño, 15))
local msg = "DIRECCIONES CANDIDATAS HP (" .. #results .. "):\n\n"
for i, r in ipairs(results) do
    msg = msg .. string.format("0x%X  =  %.1f\n", r.address, tonumber(r.value) or 0)
end
msg = msg .. "\nSacá foto a esta pantalla y mandala."
gg.alert(msg)

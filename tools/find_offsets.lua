-- FF Offset Finder — solo lectura, no modifica nada
-- Uso: cargar en GameGuardian mientras estás en partida

local function log(msg)
    gg.alert(tostring(msg))
end

local function buscarHP()
    local hp = gg.prompt({"Tu HP actual (ej: 200):"}, {[1]="200"}, {[1]="number"})
    if not hp then return end
    local val = tonumber(hp[1])

    gg.clearResults()
    gg.searchNumber(tostring(val), gg.TYPE_FLOAT, false, gg.SIGN_EQUAL, 0, -1)
    local count = gg.getResultCount()
    gg.alert("Encontrados: " .. count .. " resultados para " .. val ..
             "\n\nAhora recibí daño y tocá OK")
    return val
end

local function refinar(valAnterior)
    local nuevaHP = gg.prompt({"Tu HP ahora (después del daño):"}, {[1]="150"}, {[1]="number"})
    if not nuevaHP then return end
    local val = tonumber(nuevaHP[1])
    gg.searchNumber(tostring(val), gg.TYPE_FLOAT, false, gg.SIGN_EQUAL, 0, -1)
    local count = gg.getResultCount()
    gg.alert("Resultados refinados: " .. count)
    return val
end

local function mostrarDireccion()
    local count = gg.getResultCount()
    if count == 0 then
        gg.alert("Sin resultados. Reiniciá la búsqueda.")
        return
    end
    local results = gg.getResults(math.min(count, 10))
    local msg = "Primeras " .. #results .. " direcciones HP:\n"
    for i, r in ipairs(results) do
        msg = msg .. i .. ". " .. string.format("0x%X", r.address) .. " = " .. r.value .. "\n"
    end
    msg = msg .. "\nAnotá las que empiezan con la misma base alta (ej: 0x7F...)"
    gg.alert(msg)
end

local function menu()
    while true do
        local op = gg.choice(
            {"1. Buscar HP inicial",
             "2. Refinar (después de recibir daño)",
             "3. Ver direcciones encontradas",
             "4. Limpiar y salir"},
            nil,
            "FF Offset Finder — solo lectura")
        if not op or op == 4 then break end
        if op == 1 then buscarHP() end
        if op == 2 then refinar() end
        if op == 3 then mostrarDireccion() end
    end
end

menu()

-- FF Offset Finder v3 - klass_ptr + HP/maxHP offsets + referencias
-- Instrucciones: copiar a GG, correr EN PARTIDA
gg.setVisible(false)
gg.alert("FF OFFSET FINDER v3\n\nEstar EN PARTIDA con HP lleno.\nToca OK para comenzar.")

-- ===== PASO 1: capturar maxHP (200.0 en FF) =====
-- HP maximo base en Free Fire = 200. Con habilidades puede ser 200-230.
local MAXHP = "200"  -- cambiar si tu personaje tiene max HP diferente

gg.clearResults()
gg.searchNumber(MAXHP, gg.TYPE_FLOAT, false, gg.SIGN_EQUAL, 0, -1)
local n1 = gg.getResultCount()
if n1 == 0 then
    gg.alert("No encontre " .. MAXHP .. ".0. Verifica estar en partida con HP lleno."); return
end
gg.toast(n1 .. " valores " .. MAXHP .. ".0. Recibe dano ahora...")
gg.alert("Recibe DANO para que tu HP baje.\nToca OK cuando tu HP ya bajo.")

-- Mantener solo los que siguen siendo 200.0 (son los maxHP)
gg.searchNumber(MAXHP, gg.TYPE_FLOAT, false, gg.SIGN_EQUAL, 0, -1)
local n2 = gg.getResultCount()
local maxhp = gg.getResults(math.min(n2, 20))
gg.toast(#maxhp .. " candidatos maxHP")

if #maxhp < 2 then
    gg.alert("Solo " .. #maxhp .. " candidato(s).\nNecesito 2+ jugadores con HP lleno."); return
end

-- ===== PASO 2: votar por klass_ptr =====
-- Tecnica: en il2cpp, todos los FightingFighter comparten el mismo klass_ptr.
-- Para cada candidato maxHP, leemos hacia atras y contamos que puntero aparece
-- al mismo offset en la mayoria de los objetos.
local votes = {}  -- votes[back_offset][ptr_value] = count

for _, r in ipairs(maxhp) do
    for back = 8, 512, 8 do
        local addr = r.address - back
        local v = gg.getValues({{address = addr, flags = gg.TYPE_QWORD}})
        if v and v[1] then
            local ptr = tonumber(v[1].value) or 0
            if ptr > 65536 then
                if not votes[back] then votes[back] = {} end
                votes[back][ptr] = (votes[back][ptr] or 0) + 1
            end
        end
    end
end

-- Buscar el (offset, klass_ptr) con mas votos
local best_off, best_klass, best_cnt = nil, nil, 0
local need = math.max(2, math.ceil(#maxhp * 0.6))

for off, ptrs in pairs(votes) do
    for klass, cnt in pairs(ptrs) do
        if cnt >= need and cnt > best_cnt then
            best_off, best_klass, best_cnt = off, klass, cnt
        end
    end
end

if not best_off then
    gg.alert("Sin patron comun.\nTips: busca partida con 4+ enemigos en zona."); return
end

-- ===== PASO 3: encontrar HP actual (justo bajo cuando recibiste dano) =====
local base_hp_addr = maxhp[1].address
local hp_off, hp_val = nil, 0

for d = -64, 64, 4 do
    if d ~= 0 then
        local v = gg.getValues({{address = base_hp_addr + d, flags = gg.TYPE_FLOAT}})
        local val = v and v[1] and (tonumber(v[1].value) or 0) or 0
        if val > 1.1 and val < 999.0 then
            hp_off = best_off + d
            hp_val = val
            break
        end
    end
end

-- ===== RESULTADO PRINCIPAL =====
local msg = "===== OFFSETS ENCONTRADOS =====\n\n"
msg = msg .. string.format("FightingFighter klass_ptr:\n  0x%X\n\n", best_klass)
msg = msg .. string.format("maxHP offset en objeto: 0x%X\n", best_off)
if hp_off then
    msg = msg .. string.format("HP actual offset:       0x%X  (val=%.1f)\n", hp_off, hp_val)
end
msg = msg .. string.format("\nMatch en %d/%d candidatos\n", best_cnt, #maxhp)
msg = msg .. "\n[ SACALE FOTO A ESTO ]"
gg.alert(msg)

-- ===== PASO 4: buscar quien apunta al objeto (cadena de punteros) =====
-- El objeto base = maxHP_addr - best_off
local obj_base = base_hp_addr - best_off
gg.toast("Buscando referencias al objeto...")
gg.clearResults()
gg.searchNumber(tostring(obj_base), gg.TYPE_QWORD, false, gg.SIGN_EQUAL, 0, -1)
local refs = gg.getResultCount()

if refs == 0 then
    gg.alert("Nadie apunta directamente al objeto.\nEl manager usa una lista intermedia.\n\nUsaremos el klass_ptr del Paso 3."); return
end

local rlist = gg.getResults(math.min(refs, 8))
local rmsg = "Referencias al objeto\n(0x" .. string.format("%X", obj_base) .. "):\n"
rmsg = rmsg .. refs .. " total, mostrando " .. #rlist .. "\n\n"
for _, r in ipairs(rlist) do
    rmsg = rmsg .. string.format("0x%X\n", r.address)
end
rmsg = rmsg .. "\n[ SACALE FOTO A ESTO ]"
gg.alert(rmsg)

package com.esp.ff

// ── Cómo actualizar offsets ───────────────────────────────────────────────────
//
// 1. Dump il2cpp:
//    - Descargar il2CppDumper en PC (o Il2CppInspector)
//    - Extraer libGameAssembly.so + global-metadata.dat del APK
//    - Correr: Il2CppDumper.exe libGameAssembly.so global-metadata.dat output/
//    - Abrir output/dump.cs y buscar las clases que se usan abajo
//
// 2. TypeInfo offsets:
//    - Correr tools/frida_statics.js en Frida con el PID del juego
//    - Output: "FightingFighterManager TypeInfo: 0x1234ABCD" → eso va en PM_TYPE_INFO
//
// 3. Posición nativa:
//    - Usar GameGuardian para freezar posición XY y hacer pointer scan
//    - Buscar el offset que da la posición correcta (típicamente 0x54, 0x64 ó 0x90)
//
// ─────────────────────────────────────────────────────────────────────────────
//
// VERSIÓN DE REFERENCIA: OB49 / OB50 (actualizar en cada patch)
// Fuente: comunidad (pueden estar desactualizados — siempre verificar con dump fresco)
//
// ─────────────────────────────────────────────────────────────────────────────

const val FF_PACKAGE   = "com.dts.freefireth"   // MAX = "com.dts.freefiremax"
const val GAMEASSEMBLY = "libGameAssembly.so"

// Offset de static_fields dentro de Il2CppClass (arm64, Unity 2019.4)
const val IL2CPP_STATIC_FIELDS = 0xB8L

object Off {

    // ── TypeInfo offsets  (libBase + X = Il2CppClass*)  ──────────────────────
    // LLENAR con output de frida_statics.js o Il2CppDumper scripting
    // Clase objetivo: quien guarda la lista de jugadores + manager de cámara
    const val PM_TYPE_INFO     = 0x0L   // FILL: FightingFighterManager TypeInfo
    const val CAM_TYPE_INFO    = 0x0L   // FILL: BaseCameraController TypeInfo

    // ── Static field offsets dentro del StaticFields struct ───────────────────
    // dump.cs → "// Static fields:" → "// 0xXX"
    const val PM_STATIC_INSTANCE  = 0x0L   // FILL: m_pInstance del manager
    const val CAM_STATIC_INSTANCE = 0x0L   // FILL: singleton cámara

    // ── PlayerManager → lista de jugadores ────────────────────────────────────
    const val PM_PLAYER_LIST = 0x0L   // FILL: offset del List<FightingFighter>
    const val LIST_ITEMS     = 0x10L  // List<T>._items  (Unity estándar, no cambiar)
    const val LIST_SIZE      = 0x18L  // List<T>._size

    // ── Por jugador (clase FightingFighter o equivalente) ─────────────────────
    const val PLAYER_HP        = 0x0L   // FILL: float currentHp
    const val PLAYER_HP_MAX    = 0x0L   // FILL: float maxHp
    const val PLAYER_IS_ALIVE  = 0x0L   // FILL: bool isAlive
    const val PLAYER_IS_ENEMY  = 0x0L   // FILL: bool isEnemy (o 0 si usás PLAYER_TEAM)
    const val PLAYER_TEAM      = 0x0L   // FILL: int teamId (alternativa)
    const val PLAYER_NAME_PTR  = 0x0L   // FILL: System.String* (playerName)

    // Transform del jugador — elegir A o B según qué exista en dump.cs:
    const val PLAYER_TRANSFORM  = 0x0L  // A: campo Transform cachedado en el script
    const val PLAYER_POS_DIRECT = 0x0L  // B: Vector3 worldPosition directo (si existe)

    // ── Unity Component / Transform ───────────────────────────────────────────
    const val COMPONENT_NATIVE = 0x10L  // Component.m_CachedPtr (constante Unity arm64)

    // Offset del Vector3 de posición dentro del TransformAccess nativo.
    // Valores a probar si no funciona: 0x54, 0x64, 0x78, 0x90
    const val NATIVE_POS = 0x54L        // FILL/verificar con GG pointer scan

    // ── Cámara ────────────────────────────────────────────────────────────────
    const val CAM_YAW        = 0x0L   // FILL: float yaw  (ángulo horizontal)
    const val CAM_PITCH      = 0x0L   // FILL: float pitch (ángulo vertical)
    const val NATIVE_CAM_VP  = 0x0L   // FILL opcional: VP matrix float[16] para W2S preciso
}

from gclient.framework.entities.space                   import Space
from gclient.gameplay.logic_base.entities.combat_avatar import CombatAvatar
from gclient.framework.util.story_tick                  import StoryTick
import math
import json as _json_mod
import os   as _os_mod
import cc
import builtins as _b

# ── Cleanup previous run ──────────────────────────────────────────────────────
if hasattr(_b, '_esp_tick_fn') and _b._esp_tick_fn:
    try: StoryTick._instance.Remove(_b._esp_tick_fn)
    except: pass
    _b._esp_tick_fn = None

if hasattr(_b, '_esp_nodes'):
    for n in _b._esp_nodes:
        try: n.removeFromParent()
        except: pass
_b._esp_nodes = []

dispatcher = cc.Director.getInstance().getEventDispatcher()
if hasattr(_b, '_esp_listeners'):
    for l in _b._esp_listeners:
        try: dispatcher.removeEventListener(l)
        except: pass
_b._esp_listeners = []

# ── Init builtins flags (defaults — ImGui menu will override these) ───────────
if not hasattr(_b, '_DH_BOX'):      _b._DH_BOX      = True
if not hasattr(_b, '_DH_HP'):       _b._DH_HP       = True
if not hasattr(_b, '_DH_ARMOR'):    _b._DH_ARMOR    = True
if not hasattr(_b, '_DH_NAME'):     _b._DH_NAME     = True
if not hasattr(_b, '_DH_DIST'):     _b._DH_DIST     = True
if not hasattr(_b, '_DH_CHAMS'):        _b._DH_CHAMS        = False
if not hasattr(_b, '_DH_SKELETON'):     _b._DH_SKELETON     = False
if not hasattr(_b, '_DH_AIMBOT'):       _b._DH_AIMBOT       = False
if not hasattr(_b, '_DH_AIM_FOV'):     _b._DH_AIM_FOV      = 150.0
if not hasattr(_b, '_DH_AIM_SMOOTH'):  _b._DH_AIM_SMOOTH   = 8.0
if not hasattr(_b, '_DH_AIM_KEY'):     _b._DH_AIM_KEY      = 2
if not hasattr(_b, '_DH_AIM_ACTIVE'):  _b._DH_AIM_ACTIVE   = False
if not hasattr(_b, '_DH_AIM_FOV_SHOW'):_b._DH_AIM_FOV_SHOW = True
if not hasattr(_b, '_DH_AIM_VISCHECK'):_b._DH_AIM_VISCHECK = False  # visible only
if not hasattr(_b, '_DH_AIM_BONE'):    _b._DH_AIM_BONE     = 0      # 0=Head 1=Neck 2=Chest 3=Pelvis

# Weapon name + serialized skin list (written each tick, read by C++ every 2 frames)
if not hasattr(_b, '_DH_WPN_NAME_MAIN'):     _b._DH_WPN_NAME_MAIN     = '?'
if not hasattr(_b, '_DH_WPN_NAME_SUB'):      _b._DH_WPN_NAME_SUB      = '?'
if not hasattr(_b, '_DH_WPN_NAME_MELEE'):    _b._DH_WPN_NAME_MELEE    = '?'
if not hasattr(_b, '_DH_SKIN_SERIAL_MAIN'):  _b._DH_SKIN_SERIAL_MAIN  = ''
if not hasattr(_b, '_DH_SKIN_SERIAL_SUB'):   _b._DH_SKIN_SERIAL_SUB   = ''
if not hasattr(_b, '_DH_SKIN_SERIAL_MELEE'): _b._DH_SKIN_SERIAL_MELEE = ''
if not hasattr(_b, '_DH_SKIN_BRIDGE_DIRTY'): _b._DH_SKIN_BRIDGE_DIRTY = True  # write on first tick
if not hasattr(_b, '_DH_GUN_SAVED'):        _b._DH_GUN_SAVED         = {}    # {gun_id: (sid,name,kind,id)}
if not hasattr(_b, '_DH_SKIN_APPLY_CMD'):   _b._DH_SKIN_APPLY_CMD    = None  # set by C++ Apply button
if not hasattr(_b, '_DH_SKIN_MAIN'):        _b._DH_SKIN_MAIN        = 0
if not hasattr(_b, '_DH_SKIN_SUB'):         _b._DH_SKIN_SUB         = 0
if not hasattr(_b, '_DH_SKIN_APPLY'):       _b._DH_SKIN_APPLY       = False
if not hasattr(_b, '_DH_SKIN_APPLY_SUB'):   _b._DH_SKIN_APPLY_SUB   = False
if not hasattr(_b, '_DH_SKIN_PREV_MAIN'):   _b._DH_SKIN_PREV_MAIN   = False
if not hasattr(_b, '_DH_SKIN_NEXT_MAIN'):   _b._DH_SKIN_NEXT_MAIN   = False
if not hasattr(_b, '_DH_SKIN_PREV_SUB'):    _b._DH_SKIN_PREV_SUB    = False
if not hasattr(_b, '_DH_SKIN_NEXT_SUB'):    _b._DH_SKIN_NEXT_SUB    = False
if not hasattr(_b, '_DH_SKIN_LIST'):        _b._DH_SKIN_LIST        = []
if not hasattr(_b, '_DH_SKIN_LIST_SUB'):    _b._DH_SKIN_LIST_SUB    = []
if not hasattr(_b, '_DH_SKIN_IDX_MAIN'):    _b._DH_SKIN_IDX_MAIN    = 0
if not hasattr(_b, '_DH_SKIN_IDX_SUB'):     _b._DH_SKIN_IDX_SUB     = 0
if not hasattr(_b, '_DH_SKIN_LIST_DIRTY'):  _b._DH_SKIN_LIST_DIRTY  = True
if not hasattr(_b, '_DH_SKIN_GUN_MAIN'):    _b._DH_SKIN_GUN_MAIN    = -1  # tracked gun_id
if not hasattr(_b, '_DH_SKIN_GUN_SUB'):     _b._DH_SKIN_GUN_SUB     = -1
if not hasattr(_b, '_DH_SKIN_CUR_MAIN'):    _b._DH_SKIN_CUR_MAIN    = "Default"
if not hasattr(_b, '_DH_SKIN_CUR_SUB'):     _b._DH_SKIN_CUR_SUB     = "Default"
if not hasattr(_b, '_DH_SKIN_SAVED_MAIN'):  _b._DH_SKIN_SAVED_MAIN  = None
if not hasattr(_b, '_DH_SKIN_SAVED_SUB'):   _b._DH_SKIN_SAVED_SUB   = None
# Melee skin
if not hasattr(_b, '_DH_SKIN_LIST_MELEE'):  _b._DH_SKIN_LIST_MELEE  = []
if not hasattr(_b, '_DH_SKIN_IDX_MELEE'):   _b._DH_SKIN_IDX_MELEE   = 0
if not hasattr(_b, '_DH_SKIN_CUR_MELEE'):   _b._DH_SKIN_CUR_MELEE   = "Default"
if not hasattr(_b, '_DH_SKIN_SAVED_MELEE'): _b._DH_SKIN_SAVED_MELEE = None
if not hasattr(_b, '_DH_SKIN_PREV_MELEE'):  _b._DH_SKIN_PREV_MELEE  = False
if not hasattr(_b, '_DH_SKIN_NEXT_MELEE'):  _b._DH_SKIN_NEXT_MELEE  = False
if not hasattr(_b, '_DH_SKIN_GUN_MELEE'):   _b._DH_SKIN_GUN_MELEE   = -1
_b._DH_SKIN_LIST_DIRTY = True
if not hasattr(_b, '_DH_FOV'):      _b._DH_FOV      = False
if not hasattr(_b, '_DH_FOV_VAL'):  _b._DH_FOV_VAL  = 90.0

# ── Skin config persistence ───────────────────────────────────────────────────
_SKIN_CFG_PATH = 'C:/bs_skin_config.json'

def _save_skin_config():
    """Write _DH_GUN_SAVED to disk atomically. Called after any skin apply."""
    try:
        data = {}
        saved = getattr(_b, '_DH_GUN_SAVED', {})
        for gid, entry in saved.items():
            data[str(gid)] = list(entry)
        tmp = _SKIN_CFG_PATH + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            _json_mod.dump(data, f, ensure_ascii=False, indent=2)
        _os_mod.replace(tmp, _SKIN_CFG_PATH)
    except:
        pass

def _load_skin_config():
    """Read saved skins from disk into _DH_GUN_SAVED on cheat load."""
    try:
        with open(_SKIN_CFG_PATH, 'r', encoding='utf-8') as f:
            data = _json_mod.load(f)
        if not hasattr(_b, '_DH_GUN_SAVED') or not _b._DH_GUN_SAVED:
            _b._DH_GUN_SAVED = {}
        for gid_str, entry in data.items():
            gid = int(gid_str)
            if gid not in _b._DH_GUN_SAVED:
                _b._DH_GUN_SAVED[gid] = tuple(entry)
    except:
        pass  # file missing or corrupt — silent, no skins loaded

# Load saved skins immediately so the enforce loop can re-apply them
# on the first valid tick without any user action needed.
_load_skin_config()

# ── Enforce warmup counter ────────────────────────────────────────────────────
# On démarre à -180 (3 secondes @ 60fps) pour laisser le temps au jeu
# d'initialiser tous les weapon cases côté C++ avant le premier enforce.
# Sans ça, le premier tick exécute enforce immédiatement sur des objets
# potentiellement pas encore prêts → freeze/crash natif non catchable.
if not hasattr(_b, '_DH_ENFORCE_COUNTER'):
    _b._DH_ENFORCE_COUNTER = -180
else:
    # Re-load du script (ex: "re" dans le REPL) — reset le warmup aussi
    _b._DH_ENFORCE_COUNTER = -180

# ── Setup ─────────────────────────────────────────────────────────────────────
director = cc.Director.getInstance()
glview   = director.getOpenGLView()
scale_x  = glview.getScaleX()
scale_y  = glview.getScaleY()
dw       = director.getWinSize().width
dh       = director.getWinSize().height
scene    = director.getRunningScene()

def to_cocos(px, py):
    return px / scale_x, dh - (py / scale_y)

WHITE  = cc.Color4B(255, 255, 255, 255)
HP_BG  = cc.Color4B( 20,  20,  20, 220)
HP_HI  = cc.Color4B(  0, 210,  80, 255)
HP_MED = cc.Color4B(255, 170,   0, 255)
HP_LOW = cc.Color4B(235,  40,  40, 255)
C_WHT  = cc.Color3B(255, 255, 255)
AR_BG  = cc.Color4B( 20,  20,  20, 180)
AR_COL = cc.Color4B( 80, 160, 255, 255)

MAX_ENEMIES = 10
BAR_W = 2

# ── FOV circle DrawNode + ESP nodes ──────────────────────────────────────────
# Ces nodes Cocos2d-x DOIVENT être créés depuis le thread Cocos2d-x (esp_tick),
# pas depuis le thread RunPython (notre thread externe).
# Créer/addChild depuis un thread externe = corruption scène = crash natif
# non catchable par try/except ni par notre SEH.
# On initialise à None ici et on crée au premier tick dans esp_tick.
fov_draw    = None
draws       = []
labels      = []
dist_labels = []
skel_draws  = []
_nodes_ready = False  # flag : nodes créés et valides

# ── Skeleton bone connections ─────────────────────────────────────────────────
# Each tuple = (parent_bone, child_bone) drawn as a line segment.
# BloodStrike uses the "biped" naming convention.
SKEL_BONES = [
    # Spine chain
    ('biped Pelvis',    'biped Spine'),
    ('biped Spine',     'biped Spine1'),
    ('biped Spine1',    'biped Spine2'),
    ('biped Spine2',    'biped Neck'),
    ('biped Neck',      'biped Head'),
    # Left arm
    ('biped Spine2',    'biped L Clavicle'),
    ('biped L Clavicle','biped L UpperArm'),
    ('biped L UpperArm','biped L Forearm'),
    ('biped L Forearm', 'biped L Hand'),
    # Right arm
    ('biped Spine2',    'biped R Clavicle'),
    ('biped R Clavicle','biped R UpperArm'),
    ('biped R UpperArm','biped R Forearm'),
    ('biped R Forearm', 'biped R Hand'),
    # Left leg
    ('biped Pelvis',    'biped L Thigh'),
    ('biped L Thigh',   'biped L Calf'),
    ('biped L Calf',    'biped L Foot'),
    # Right leg
    ('biped Pelvis',    'biped R Thigh'),
    ('biped R Thigh',   'biped R Calf'),
    ('biped R Calf',    'biped R Foot'),
]
SKEL_COLOR = cc.Color4B(255, 255, 255, 200)

# ── Aimbot target bone map ────────────────────────────────────────────────────
# Index matches _DH_AIM_BONE values sent from the ImGui combo.
AIM_BONES = [
    'biped Head',     # 0 - Head
    'biped Neck',     # 1 - Neck
    'biped Spine2',   # 2 - Chest
    'biped Pelvis',   # 3 - Pelvis
]

# ── Chams cache + FOV state ───────────────────────────────────────────────────
_chams_cache   = set()
_prev_fov      = [False]
_fov_orig      = [None]
_fov_patched   = [False]

# ── Scene reference — mutable pour détecter les changements de scène ──────────
# On utilise une liste à 1 élément pour pouvoir la modifier depuis esp_tick
# sans 'global' (Python 2/3 compatible).
_current_scene  = [scene]
_py_log_tick    = [0]

def _rebuild_nodes(new_scene):
    """Recrée tous les DrawNodes/Labels sur la nouvelle scène."""
    global draws, labels, dist_labels, skel_draws, fov_draw, _nodes_ready
    try:
        fov_draw = cc.DrawNode.create()
        fov_draw.setLocalZOrder(99998)
        new_scene.addChild(fov_draw)
        _b._esp_nodes = [fov_draw]
    except:
        return

    new_draws       = []
    new_labels      = []
    new_dist_labels = []
    new_skel_draws  = []

    for i in range(MAX_ENEMIES):
        try:
            d = cc.DrawNode.create()
            d.setLocalZOrder(99999); d.setVisible(False)
            new_scene.addChild(d); new_draws.append(d); _b._esp_nodes.append(d)
        except:
            new_draws.append(None)

        try:
            lbl = cc.Label.createWithSystemFont("", "Arial", 11)
            lbl.setLocalZOrder(99999); lbl.setVisible(False)
            try: lbl.setColor(C_WHT)
            except: pass
            new_scene.addChild(lbl); new_labels.append(lbl); _b._esp_nodes.append(lbl)
        except:
            new_labels.append(None)

        try:
            dlbl = cc.Label.createWithSystemFont("", "Arial", 10)
            dlbl.setLocalZOrder(99999); dlbl.setVisible(False)
            try: dlbl.setColor(cc.Color3B(180, 220, 255))
            except: pass
            new_scene.addChild(dlbl); new_dist_labels.append(dlbl); _b._esp_nodes.append(dlbl)
        except:
            new_dist_labels.append(None)

        try:
            sd = cc.DrawNode.create()
            sd.setLocalZOrder(99998); sd.setVisible(False)
            new_scene.addChild(sd); new_skel_draws.append(sd); _b._esp_nodes.append(sd)
        except:
            new_skel_draws.append(None)

    draws       = new_draws
    labels      = new_labels
    dist_labels = new_dist_labels
    skel_draws  = new_skel_draws
    _current_scene[0] = new_scene
    _nodes_ready = True

def apply_fov(enable, fov_val):
    try:
        cam    = Space._instance.camera
        placer = cam.placer
        if enable:
            # Save original on first enable
            if not _fov_patched[0]:
                _fov_orig[0] = placer.AffiliatedFovTarget
                # No-op zoom methods so scoping doesn't override
                for m in ['OnZoomFov','OnZoomAdditiveFov',
                          'OnZoomAffiliatedFov','OnZoomAdditiveAffiliatedFov']:
                    if hasattr(placer, m):
                        setattr(placer, m, lambda *a: None)
                _fov_patched[0] = True
            placer.SetAffiliatedFov(fov_val)
        else:
            if _fov_patched[0]:
                # Restore zoom methods
                for m in ['OnZoomFov','OnZoomAdditiveFov',
                          'OnZoomAffiliatedFov','OnZoomAdditiveAffiliatedFov']:
                    try: delattr(placer, m)
                    except: pass
                # Restore original FOV
                if _fov_orig[0] is not None:
                    placer.SetAffiliatedFov(_fov_orig[0])
                _fov_patched[0] = False
    except: pass

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_bone(cam, ent, bone):
    try:
        sp = cam.GetScreenPointFromWorldPoint(ent.model.GetBoneWorldPosition(bone))
        if sp and sp.z != -1.0:
            return to_cocos(sp.x, sp.y)
    except: pass
    return None

def screen_dist(sx, sy):
    return math.hypot(sx - 960.0, sy - 540.0)

# ── Visibility check ──────────────────────────────────────────────────────────
# Uses Space.ClosestRaycast(cam_origin, head_pos, filter=23).
# filter=23 is the default collision mask used by the game's own
# IsObstacleBetweenTargetpos helper — it skips character bodies.
#
# When VISIBLE:    the ray hits local player body/terrain very close to cam
#                  → Distance < 2.0
# When OCCLUDED:   the ray hits a wall/obstacle between cam and target
#                  → Distance > 2.0  (distance to the blocking surface)
#
# Fail-open: any exception → assume visible (aimbot never silently disabled).
_VISCHECK_THRESHOLD = 2.0   # metres — tune if needed

def is_visible(space, ecam, ent, bone='biped Head'):
    try:
        origin = ecam.GetOrigin()
        head   = ent.model.GetBoneWorldPosition(bone)
        r      = space.ClosestRaycast(origin, head, 23)
        if not r or not r.IsHit:
            return True   # nothing hit → clear line of sight
        return r.Distance < _VISCHECK_THRESHOLD
    except:
        return True   # fail open

# ── Guard: détecte si l'espace de jeu est encore valide ───────────────────────
def _space_valid():
    try:
        s = Space._instance
        if s is None: return False
        o = s.owner
        if o is None: return False
        ca = getattr(o, 'combat_avatar', None)
        if ca is None: return False
        return True
    except:
        return False

# ── Main tick ─────────────────────────────────────────────────────────────────
def esp_tick(*args):
    global fov_draw, draws, labels, dist_labels, skel_draws, _nodes_ready
    _py_log_tick[0] += 1

    if not _space_valid():
        return

    try:
        DO_BOX      = getattr(_b, '_DH_BOX',      True)
        DO_HP       = getattr(_b, '_DH_HP',        True)
        DO_ARMOR    = getattr(_b, '_DH_ARMOR',     True)
        DO_NAME     = getattr(_b, '_DH_NAME',      True)
        DO_DIST     = getattr(_b, '_DH_DIST',      True)
        DO_CHAMS    = getattr(_b, '_DH_CHAMS',     False)
        DO_SKELETON = getattr(_b, '_DH_SKELETON',  False)
        DO_AIMBOT   = getattr(_b, '_DH_AIMBOT',    False)
        AIM_FOV     = getattr(_b, '_DH_AIM_FOV',    150.0)
        AIM_SMOOTH  = getattr(_b, '_DH_AIM_SMOOTH',  8.0)
        AIM_ACTIVE  = getattr(_b, '_DH_AIM_ACTIVE', False)
        AIM_VISCHECK= getattr(_b, '_DH_AIM_VISCHECK',False)
        AIM_BONE    = AIM_BONES[max(0, min(3, getattr(_b, '_DH_AIM_BONE', 0)))]
        DO_FOV      = getattr(_b, '_DH_FOV',       False)
        FOV_VAL     = getattr(_b, '_DH_FOV_VAL',   90.0)

        space = Space._instance
        if not space: return
        local = space.owner
        if not local: return
        cam   = space.camera

        current_scene = director.getRunningScene()
        if current_scene is not _current_scene[0]:
            _nodes_ready = False
            _current_scene[0] = current_scene
            return

        if not _nodes_ready:
            try:
                _rebuild_nodes(current_scene)
                _nodes_ready = True
            except:
                return

        try:
            _nodes_orphaned = (
                fov_draw.getParent() is None or
                (draws and draws[0] is not None and draws[0].getParent() is None)
            )
        except:
            _nodes_orphaned = True
        if _nodes_orphaned:
            _nodes_ready = False
            return

        SHOW_FOV = getattr(_b, '_DH_AIM_FOV_SHOW', True)
        try:
            _fov_alive = fov_draw is not None and fov_draw.getParent() is not None
        except:
            _fov_alive = False
        if _fov_alive:
            try: fov_draw.clear()
            except: pass
        else:
            _nodes_ready = False
            return
        if _fov_alive and DO_AIMBOT and SHOW_FOV:
            try:
                radius_cocos = AIM_FOV / scale_x
                cx_cocos = dw / 2
                cy_cocos = dh / 2
                import math as _math
                segs = 64
                pts = []
                for i in range(segs + 1):
                    a = 2 * _math.pi * i / segs
                    pts.append(cc.Vec2(cx_cocos + radius_cocos * _math.cos(a),
                                       cy_cocos + radius_cocos * _math.sin(a)))
                WHITE_FOV = cc.Color4B(255, 255, 255, 120)
                for i in range(segs):
                    fov_draw.drawLine(pts[i], pts[i+1], 1.0, WHITE_FOV)
            except: pass

        # ── Skin changer ─────────────────────────────────────────────────────
        # _gun_changed: True si un weapon case a changé CE tick.
        # Garanti accessible même si le bloc inner lève une exception.
        _gun_changed = False
        # Auto-detect weapon swap: rebuild if gun_id changed
        if local and local.combat_avatar:
            try:
                _wc_m = local.combat_avatar.GetMainGunWeaponCase()
                _wc_s = local.combat_avatar.GetSubGunWeaponCase()
                _gm = _wc_m.gun_id if _wc_m else -1
                _gs = _wc_s.gun_id if _wc_s else -1

                _gun_changed = False
                if _gm != _b._DH_SKIN_GUN_MAIN or _gs != _b._DH_SKIN_GUN_SUB:
                    _gun_changed = True
                    main_changed = (_gm != _b._DH_SKIN_GUN_MAIN)
                    sub_changed  = (_gs != _b._DH_SKIN_GUN_SUB)
                    _b._DH_SKIN_GUN_MAIN   = _gm
                    _b._DH_SKIN_GUN_SUB    = _gs
                    _b._DH_SKIN_LIST_DIRTY = True
                    # Reset enforce counter on weapon swap — give the new weapon case
                    # time to fully initialize C++-side before we call Change* on it.
                    # Without this, enforce runs on the NEW (not yet ready) wc
                    # or the OLD (already freed) wc = guaranteed crash.
                    _b._DH_ENFORCE_COUNTER = -120
                    if main_changed:
                        _b._DH_SKIN_SAVED_MAIN = None
                        _b._DH_SKIN_CUR_MAIN   = "Default"
                    if sub_changed:
                        _b._DH_SKIN_SAVED_SUB  = None
                        _b._DH_SKIN_CUR_SUB    = "Default"

                # ── Skin enforce ──────────────────────────────────────────────
                # Throttled every 120 ticks (~2s). Skipped entirely on the tick
                # a weapon change is detected (_gun_changed) — the old wc is
                # being freed that frame, any Change* call = native crash.
                if not hasattr(_b, '_DH_ENFORCE_COUNTER'): _b._DH_ENFORCE_COUNTER = -180
                _b._DH_ENFORCE_COUNTER += 1
                if _b._DH_ENFORCE_COUNTER >= 0 and not _gun_changed \
                        and hasattr(_b, '_DH_GUN_SAVED') and _b._DH_GUN_SAVED \
                        and _b._DH_ENFORCE_COUNTER % 120 == 0:
                    # Re-fetch fresh refs — never reuse wc refs from above
                    try: _wc_m_enf = local.combat_avatar.GetMainGunWeaponCase() if local and local.combat_avatar else None
                    except: _wc_m_enf = None
                    try: _wc_s_enf = local.combat_avatar.GetSubGunWeaponCase() if local and local.combat_avatar else None
                    except: _wc_s_enf = None
                    for _wc in [_wc_m_enf, _wc_s_enf]:
                        if not _wc: continue
                        try:
                            _gid = getattr(_wc, 'gun_id', None)
                            if not _gid or _gid not in _b._DH_GUN_SAVED: continue
                            _sid, _sname, _kind, _ = _b._DH_GUN_SAVED[_gid]
                            try:
                                _cur_skin  = getattr(_wc, 'skin_id',  0) or 0
                                _cur_guise = getattr(_wc, 'guise_id', 0) or 0
                            except:
                                continue  # objet invalide, skip
                            if _kind == 'guise' and _cur_guise != _sid:
                                _wc.ChangeWeaponSkin(0); _wc.ChangeWeaponGuise(_sid)
                                for _fn in ['RefreshKillUpgradeModel','RefreshGuiseEffect',
                                            'PlayStableRacerEffect','RefreshGuiseSkinAnimPose',
                                            'RefreshGuiseSkinAnimPoseForWeapon',
                                            'RefreshGuise3PEffectInCombat']:
                                    try: getattr(_wc, _fn)()
                                    except: pass
                            elif _kind == 'skin' and _cur_skin != _sid:
                                _wc.ChangeWeaponGuise(0); _wc.ChangeWeaponSkin(_sid)
                        except: pass

                # ── Melee weapon case ─────────────────────────────────────────
                # MeleeCase uses weapon_id instead of gun_id
                try:
                    _wc_melee = local.combat_avatar.GetMeleeWeaponCase()
                    _gmelee   = _wc_melee.weapon_id if _wc_melee else -1
                except:
                    _wc_melee = None
                    _gmelee   = -1

                if _gmelee != _b._DH_SKIN_GUN_MELEE:
                    _gun_changed = True
                    _b._DH_SKIN_GUN_MELEE   = _gmelee
                    _b._DH_SKIN_LIST_DIRTY  = True
                    _b._DH_SKIN_SAVED_MELEE = None
                    _b._DH_SKIN_CUR_MELEE   = "Default"

                # Melee enforce — same throttle + same _gun_changed guard as gun enforce.
                # _wc_melee fetched above is safe to reuse since weapon_id is stable
                # for the duration of the tick, but we skip if any weapon changed.
                try:
                    saved = getattr(_b, '_DH_SKIN_SAVED_MELEE', None)
                    if saved and _wc_melee and not _gun_changed \
                            and _b._DH_ENFORCE_COUNTER >= 0 \
                            and _b._DH_ENFORCE_COUNTER % 120 == 0:
                        sid, sname, skind, saved_wid = saved
                        try:
                            cur_wid = getattr(_wc_melee, 'weapon_id', None)
                        except:
                            cur_wid = None
                        if cur_wid and cur_wid == saved_wid:
                            try:
                                cur_guise = getattr(_wc_melee, 'guise_id', None) or 0
                            except:
                                cur_guise = sid  # assume already applied, skip
                            if skind == 'melee_guise' and cur_guise != sid:
                                try: _wc_melee.ChangeWeaponGuise(0)
                                except: pass
                                _wc_melee.ChangeWeaponGuise(sid)
                                for _mfn in ['RefreshGuiseEffect','RefreshModelSkin',
                                             'RefreshGuiseSkinAnimPoseForWeapon',
                                             'RefreshGuiseSkinAnimPoseForHand']:
                                    try: getattr(_wc_melee, _mfn)()
                                    except: pass
                except: pass
            except: pass

        if getattr(_b, '_DH_SKIN_LIST_DIRTY', True) and local and local.combat_avatar:
            try:
                import gclient.util.gun_skin_util as _sku
                def _safe(s):
                    try: return str(s).encode('ascii','replace').decode()
                    except: return "?"
                def _build(ca, wc_fn):
                    try:
                        w = getattr(ca, wc_fn)()
                        if not w: return []
                        gun_id = w.gun_id
                        lst = []

                        for item in _sku.GetAllGunSkinItemList(gun_id):
                            if getattr(item, 'is_origin_item', False): continue
                            if getattr(item, 'is_random_item', False): continue
                            sid = getattr(item, 'skin_id', None)
                            if not sid or sid <= 0: continue
                            ip   = getattr(item, 'item_proto', {}) or {}
                            name = _safe(ip.get('name', ip.get('skin_name', str(sid))))
                            lst.append((sid, name, 'skin'))

                        for item in _sku.GetGunGuiseItemAndMallGachaItemList(gun_id):
                            if getattr(item, 'is_origin_item', False): continue
                            if getattr(item, 'is_random_item', False): continue
                            gid = getattr(item, 'guise_id', None)
                            if not gid or gid <= 0: continue
                            ip   = getattr(item, 'item_proto', {}) or {}
                            name = _safe(ip.get('name', ip.get('skin_name', str(gid))))
                            lst.append((gid, name, 'guise'))

                        lst.sort(key=lambda x: x[1].lower())
                        return lst
                    except:
                        return []
                _b._DH_SKIN_LIST      = _build(local.combat_avatar, 'GetMainGunWeaponCase')
                _b._DH_SKIN_LIST_SUB  = _build(local.combat_avatar, 'GetSubGunWeaponCase')
                # Melee — uses GetAllMeleeSkinItemList(melee_weapon_id)
                # guise_id is directly on item.guise_id (no proto parsing needed)
                try:
                    def _build_melee(ca):
                        try:
                            wc = ca.GetMeleeWeaponCase()
                            if not wc: return []
                            body_proto   = wc.body_equip_proto or {}
                            melee_wpn_id = body_proto.get('melee_weapon_id', 1)
                            lst = []
                            for item in _sku.GetAllMeleeSkinItemList(melee_wpn_id):
                                try:
                                    guise_id = getattr(item, 'guise_id', None)
                                    if not guise_id or guise_id <= 0: continue
                                    ip   = getattr(item, 'item_proto', {}) or {}
                                    name = _safe(ip.get('name', str(guise_id)))
                                    lst.append((guise_id, name, 'melee_guise'))
                                except: pass
                            lst.sort(key=lambda x: x[1].lower())
                            return lst
                        except:
                            return []
                    _b._DH_SKIN_LIST_MELEE = _build_melee(local.combat_avatar)
                except:
                    _b._DH_SKIN_LIST_MELEE = []
                # Reset indexes
                _b._DH_SKIN_IDX_MAIN  = 0
                _b._DH_SKIN_IDX_SUB   = 0
                _b._DH_SKIN_IDX_MELEE = 0
                _b._DH_SKIN_LIST_DIRTY = False
                _b._DH_SKIN_BRIDGE_DIRTY = True   # trigger file bridge write
            except: pass

        # ── Build all-guns skin registry + write bridge file ─────────────────
        # ── Build ALL-GUNS skin bridge file ──────────────────────────────────
        # Scans ALL 44 known gun_ids (not just equipped weapons) using
        # equip_data for gun names and GetAllGunSkinItemList for skins.
        # Written once on load and on Refresh. C++ parses it for the skin UI.
        # Format: GUN:<gun_id>:<gun_name>\nSKIN:<sid>:<kind>:<name>\n...END\n
        #         MELEE:<weapon_id>:<name>\nMSKIN:<guise_id>:<name>\n...END\n
        if getattr(_b, '_DH_SKIN_BRIDGE_DIRTY', True) and local and local.combat_avatar:
            # Différer le scan de 300 ticks (~5s) — laisse le jeu finir d'init
            # ses weapon cases avant de faire 88+ appels Python→C++.
            # Sans délai, le premier tick peut freeze/crash le thread Python du jeu.
            if getattr(_b, '_DH_ENFORCE_COUNTER', -999) >= 300:
                try:
                    import gclient.util.gun_skin_util as _sku2
                    import os as _os2
                    wu    = _sku2.weapon_util
                    edata = _sku2.equip_data.data

                    def _safe2(s):
                        try: return str(s).encode('ascii','replace').decode().replace('\n','').replace(':','_')
                        except: return '?'

                    def _gun_name(gun_id):
                        try:
                            eid = wu.GetEquipIdByGun(gun_id)
                            return _safe2(edata[eid].get('name', f'gun_{gun_id}'))
                        except: return f'gun_{gun_id}'

                    ALL_GUN_IDS = [1,2,4,6,8,10,13,14,15,16,17,18,19,20,21,22,23,24,25,
                                   27,28,29,30,31,32,33,34,35,37,38,39,40,41,42,43,44,45,
                                   48,49,50,51,52,53,54]
                    lines = []

                    for gun_id in ALL_GUN_IDS:
                        try:
                            gun_name = _gun_name(gun_id)
                            skins = []
                            try:
                                for item in _sku2.GetAllGunSkinItemList(gun_id):
                                    sid = getattr(item, 'skin_id', None)
                                    if not sid or sid <= 0: continue
                                    ip   = getattr(item, 'item_proto', {}) or {}
                                    name = _safe2(ip.get('name', ip.get('skin_name', str(sid))))
                                    skins.append((sid, 'skin', name))
                            except: pass
                            try:
                                for item in _sku2.GetGunGuiseItemAndMallGachaItemList(gun_id):
                                    gid2 = getattr(item, 'guise_id', None)
                                    if not gid2 or gid2 <= 0: continue
                                    ip   = getattr(item, 'item_proto', {}) or {}
                                    name = _safe2(ip.get('name', ip.get('skin_name', str(gid2))))
                                    skins.append((gid2, 'guise', name))
                            except: pass
                            skins.sort(key=lambda x: x[2].lower())
                            if skins:
                                lines.append(f'GUN:{gun_id}:{gun_name}')
                                for sid, kind, name in skins:
                                    lines.append(f'SKIN:{sid}:{kind}:{name}')
                                lines.append('END')
                        except: pass

                    try:
                        ca     = local.combat_avatar
                        wc_mel = ca.GetMeleeWeaponCase()
                        if wc_mel:
                            bep          = wc_mel.body_equip_proto or {}
                            melee_wpn_id = bep.get('melee_weapon_id', 1)
                            weapon_id    = wc_mel.weapon_id
                            mel_name     = _safe2(bep.get('name', 'Melee'))
                            mskins = []
                            for item in _sku2.GetAllMeleeSkinItemList(melee_wpn_id):
                                try:
                                    guise_id = getattr(item, 'guise_id', None)
                                    if not guise_id or guise_id <= 0: continue
                                    ip   = getattr(item, 'item_proto', {}) or {}
                                    name = _safe2(ip.get('name', str(guise_id)))
                                    mskins.append((guise_id, name))
                                except: pass
                            mskins.sort(key=lambda x: x[1].lower())
                            if mskins:
                                lines.append(f'MELEE:{weapon_id}:{mel_name}')
                                for gid2, name in mskins:
                                    lines.append(f'MSKIN:{gid2}:{name}')
                                lines.append('END')
                    except: pass

                    content = '\n'.join(lines) + '\n'
                    tmp = 'C:/bs_skin_bridge.bin.tmp'
                    with open(tmp, 'w', encoding='utf-8') as f:
                        f.write(content)
                    _os2.replace(tmp, 'C:/bs_skin_bridge.bin')
                    _b._DH_SKIN_BRIDGE_DIRTY = False
                except: pass
        # ── Push weapon names + serialized skin lists to builtins ─────────────
        # C++ reads these every 2 frames via Python C API to populate dropdowns.
        try:
            if local and local.combat_avatar:
                ca = local.combat_avatar
                # Weapon names
                try:
                    wc_m = ca.GetMainGunWeaponCase()
                    _b._DH_WPN_NAME_MAIN = (wc_m.body_equip_proto or {}).get('name', '?') if wc_m else '?'
                except: _b._DH_WPN_NAME_MAIN = '?'
                try:
                    wc_s = ca.GetSubGunWeaponCase()
                    _b._DH_WPN_NAME_SUB = (wc_s.body_equip_proto or {}).get('name', '?') if wc_s else '?'
                except: _b._DH_WPN_NAME_SUB = '?'
                try:
                    wc_mel = ca.GetMeleeWeaponCase()
                    _b._DH_WPN_NAME_MELEE = (wc_mel.body_equip_proto or {}).get('name', '?') if wc_mel else '?'
                except: _b._DH_WPN_NAME_MELEE = '?'
                # Serialized skin name lists (newline-separated, index = position in list)
                _b._DH_SKIN_SERIAL_MAIN  = '\n'.join(e[1] for e in _b._DH_SKIN_LIST)      if _b._DH_SKIN_LIST       else ''
                _b._DH_SKIN_SERIAL_SUB   = '\n'.join(e[1] for e in _b._DH_SKIN_LIST_SUB)  if _b._DH_SKIN_LIST_SUB   else ''
                _b._DH_SKIN_SERIAL_MELEE = '\n'.join(e[1] for e in _b._DH_SKIN_LIST_MELEE) if _b._DH_SKIN_LIST_MELEE else ''
        except: pass

        # ── helper apply skin or guise ────────────────────────────────────────
        def _apply_skin(wc, entry, slot='main'):
            # entry format:
            #   guns:  (id, name, 'skin'|'guise')
            #   melee: (guise_id, name, 'melee_guise', guise_item_id)
            sid  = entry[0]
            name = entry[1]
            kind = entry[2]
            try:
                # Probe the object before doing anything — if it's stale this throws
                if slot == 'melee':
                    try: _ = wc.weapon_id
                    except: return  # weapon case destroyed, bail
                else:
                    try: _ = wc.gun_id
                    except: return  # weapon case destroyed, bail
                if kind == 'melee_guise':
                    # Reset first, then apply new guise
                    try:
                        wc.ChangeWeaponGuise(0)
                        try: wc.RefreshGuiseEffect()
                        except: pass
                        wc.ChangeWeaponGuise(sid)
                        for _fn in ['RefreshGuiseEffect','RefreshModelSkin',
                                    'RefreshGuiseSkinAnimPoseForWeapon','RefreshGuiseSkinAnimPoseForHand',
                                    'RefreshGuise3PEffectInCombat']:
                            try: getattr(wc, _fn)()
                            except: pass
                    except: pass
                elif kind == 'guise':
                    try:
                        wc.ChangeWeaponSkin(0)
                        wc.ChangeWeaponGuise(sid)
                        for _fn in ['RefreshKillUpgradeModel','RefreshGuiseEffect',
                                    'RefreshKillCounterForChangeGuise','PlayStableRacerEffect',
                                    'RefreshGuiseSkinAnimPose','RefreshGuise3PEffectInCombat']:
                            try: getattr(wc, _fn)()
                            except: pass
                    except: pass
                else:
                    try:
                        wc.ChangeWeaponGuise(0)
                        wc.ChangeWeaponSkin(sid)
                    except: pass

                if slot == 'main':
                    _b._DH_SKIN_CUR_MAIN   = name
                    _b._DH_SKIN_SAVED_MAIN = (sid, name, kind, wc.gun_id)
                    if not hasattr(_b, '_DH_GUN_SAVED'): _b._DH_GUN_SAVED = {}
                    _b._DH_GUN_SAVED[wc.gun_id] = (sid, name, kind, wc.gun_id)
                elif slot == 'melee':
                    _b._DH_SKIN_CUR_MELEE   = name
                    _b._DH_SKIN_SAVED_MELEE = (sid, name, kind, wc.weapon_id)
                else:
                    _b._DH_SKIN_CUR_SUB   = name
                    _b._DH_SKIN_SAVED_SUB = (sid, name, kind, wc.gun_id)
                    if not hasattr(_b, '_DH_GUN_SAVED'): _b._DH_GUN_SAVED = {}
                    _b._DH_GUN_SAVED[wc.gun_id] = (sid, name, kind, wc.gun_id)

                wid = getattr(wc, 'weapon_id', None) or getattr(wc, 'gun_id', '?')
                # Persist to disk every time a skin is applied
                _save_skin_config()
            except: pass

        # Prev/Next main
        if getattr(_b, '_DH_SKIN_NEXT_MAIN', False):
            _b._DH_SKIN_NEXT_MAIN = False
            lst = _b._DH_SKIN_LIST
            if lst and not _gun_changed:
                try:
                    wc = local.combat_avatar.GetMainGunWeaponCase()
                    # Guard: list was built for this gun_id — skip if weapon swapped
                    if wc and getattr(wc, 'gun_id', -1) == _b._DH_SKIN_GUN_MAIN:
                        _b._DH_SKIN_IDX_MAIN = (_b._DH_SKIN_IDX_MAIN + 1) % len(lst)
                        _apply_skin(wc, lst[_b._DH_SKIN_IDX_MAIN], 'main')
                except: pass

        if getattr(_b, '_DH_SKIN_PREV_MAIN', False):
            _b._DH_SKIN_PREV_MAIN = False
            lst = _b._DH_SKIN_LIST
            if lst and not _gun_changed:
                try:
                    wc = local.combat_avatar.GetMainGunWeaponCase()
                    if wc and getattr(wc, 'gun_id', -1) == _b._DH_SKIN_GUN_MAIN:
                        _b._DH_SKIN_IDX_MAIN = (_b._DH_SKIN_IDX_MAIN - 1) % len(lst)
                        _apply_skin(wc, lst[_b._DH_SKIN_IDX_MAIN], 'main')
                except: pass

        # Prev/Next sub
        if getattr(_b, '_DH_SKIN_NEXT_SUB', False):
            _b._DH_SKIN_NEXT_SUB = False
            lst = _b._DH_SKIN_LIST_SUB
            if lst and not _gun_changed:
                try:
                    wc = local.combat_avatar.GetSubGunWeaponCase()
                    if wc and getattr(wc, 'gun_id', -1) == _b._DH_SKIN_GUN_SUB:
                        _b._DH_SKIN_IDX_SUB = (_b._DH_SKIN_IDX_SUB + 1) % len(lst)
                        _apply_skin(wc, lst[_b._DH_SKIN_IDX_SUB], 'sub')
                except: pass

        if getattr(_b, '_DH_SKIN_PREV_SUB', False):
            _b._DH_SKIN_PREV_SUB = False
            lst = _b._DH_SKIN_LIST_SUB
            if lst and not _gun_changed:
                try:
                    wc = local.combat_avatar.GetSubGunWeaponCase()
                    if wc and getattr(wc, 'gun_id', -1) == _b._DH_SKIN_GUN_SUB:
                        _b._DH_SKIN_IDX_SUB = (_b._DH_SKIN_IDX_SUB - 1) % len(lst)
                        _apply_skin(wc, lst[_b._DH_SKIN_IDX_SUB], 'sub')
                except: pass

        # Prev/Next melee
        if getattr(_b, '_DH_SKIN_NEXT_MELEE', False):
            _b._DH_SKIN_NEXT_MELEE = False
            lst = _b._DH_SKIN_LIST_MELEE
            if lst and not _gun_changed:
                try:
                    wc = local.combat_avatar.GetMeleeWeaponCase()
                    if wc: _apply_skin(wc, lst[(_b._DH_SKIN_IDX_MELEE + 1) % len(lst)], 'melee')
                    _b._DH_SKIN_IDX_MELEE = (_b._DH_SKIN_IDX_MELEE + 1) % len(lst)
                except: pass

        if getattr(_b, '_DH_SKIN_PREV_MELEE', False):
            _b._DH_SKIN_PREV_MELEE = False
            lst = _b._DH_SKIN_LIST_MELEE
            if lst and not _gun_changed:
                try:
                    wc = local.combat_avatar.GetMeleeWeaponCase()
                    if wc: _apply_skin(wc, lst[(_b._DH_SKIN_IDX_MELEE - 1) % len(lst)], 'melee')
                    _b._DH_SKIN_IDX_MELEE = (_b._DH_SKIN_IDX_MELEE - 1) % len(lst)
                except: pass

        # Direct apply
        if getattr(_b, '_DH_SKIN_APPLY', False):
            _b._DH_SKIN_APPLY = False
            try:
                wc = local.combat_avatar.GetMainGunWeaponCase()
                if wc: wc.ChangeWeaponSkin(int(_b._DH_SKIN_MAIN))
            except: pass

        if getattr(_b, '_DH_SKIN_APPLY_SUB', False):
            _b._DH_SKIN_APPLY_SUB = False
            try:
                wc = local.combat_avatar.GetSubGunWeaponCase()
                if wc: wc.ChangeWeaponSkin(int(_b._DH_SKIN_SUB))
            except: pass

        # ── FOV ───────────────────────────────────────────────────────────────
        if DO_FOV != _prev_fov[0]:
            apply_fov(DO_FOV, FOV_VAL)
            _prev_fov[0] = DO_FOV
        elif DO_FOV:
            try:
                Space._instance.camera.placer.SetAffiliatedFov(FOV_VAL)
            except: pass

        # ── All-guns skin apply command (from C++ TabSkin Apply button) ────────
        # Command format: (gun_id, skin_id, kind, skin_name)  OR  melee tuple
        # C++ sends this via PyExec; we apply and save for persistence.
        # Guard: only process if Space is still valid (skin swap can arrive
        # on the same tick as a round-end / weapon-drop → stale wc crash)
        cmd = getattr(_b, '_DH_SKIN_APPLY_CMD', None)
        if cmd is not None and _space_valid():
            _b._DH_SKIN_APPLY_CMD = None
            try:
                gun_id, sid, kind, _sname = cmd
                # Resolve real skin name from skin lists if available
                sname = _sname
                try:
                    if kind == 'melee_guise':
                        for e in getattr(_b, '_DH_SKIN_LIST_MELEE', []):
                            if e[0] == sid: sname = e[1]; break
                    else:
                        for lst in [getattr(_b,'_DH_SKIN_LIST',[]), getattr(_b,'_DH_SKIN_LIST_SUB',[])]:
                            for e in lst:
                                if e[0] == sid: sname = e[1]; break
                except: pass
                if not hasattr(_b, '_DH_GUN_SAVED'): _b._DH_GUN_SAVED = {}

                if kind == 'melee_guise':
                    # Melee apply — re-fetch fresh ref to avoid stale pointer
                    try:
                        wc = local.combat_avatar.GetMeleeWeaponCase()
                    except:
                        wc = None
                    if wc:
                        try: wc_wid = getattr(wc, 'weapon_id', None)
                        except: wc_wid = None
                        if wc_wid:  # only apply if the object is still alive
                            wc.ChangeWeaponGuise(0)
                            try: wc.RefreshGuiseEffect()
                            except: pass
                            wc.ChangeWeaponGuise(sid)
                            for fn in ['RefreshGuiseEffect','RefreshModelSkin',
                                       'RefreshGuiseSkinAnimPoseForWeapon','RefreshGuiseSkinAnimPoseForHand',
                                       'RefreshGuise3PEffectInCombat']:
                                try: getattr(wc, fn)()
                                except: pass
                            _b._DH_GUN_SAVED[gun_id]  = (sid, sname, kind, wc_wid)
                            _b._DH_SKIN_CUR_MELEE     = sname
                            _b._DH_SKIN_SAVED_MELEE   = (sid, sname, kind, wc_wid)
                else:
                    # Gun apply — find the weapon case by gun_id
                    # Re-fetch fresh refs — never reuse weapon case refs from outer scope
                    wc = None
                    slot = 'main'
                    try: wc_m2 = local.combat_avatar.GetMainGunWeaponCase()
                    except: wc_m2 = None
                    try: wc_s2 = local.combat_avatar.GetSubGunWeaponCase()
                    except: wc_s2 = None
                    try:
                        if wc_m2 and getattr(wc_m2, 'gun_id', None) == gun_id:
                            wc = wc_m2; slot = 'main'
                        elif wc_s2 and getattr(wc_s2, 'gun_id', None) == gun_id:
                            wc = wc_s2; slot = 'sub'
                    except:
                        wc = None
                    if wc:
                        # Verify the wc is still usable before calling Change*
                        try: _ = wc.gun_id  # probe — throws if object destroyed
                        except: wc = None
                    if wc:
                        if kind == 'guise':
                            try:
                                wc.ChangeWeaponSkin(0)
                                wc.ChangeWeaponGuise(sid)
                                for fn in ['RefreshKillUpgradeModel','RefreshGuiseEffect',
                                           'RefreshKillCounterForChangeGuise','PlayStableRacerEffect',
                                           'RefreshGuiseSkinAnimPose','RefreshGuise3PEffectInCombat']:
                                    try: getattr(wc, fn)()
                                    except: pass
                            except: pass
                        else:
                            try:
                                wc.ChangeWeaponGuise(0)
                                wc.ChangeWeaponSkin(sid)
                            except: pass
                    # Always save — so enforce re-applies when the gun is re-equipped
                    _b._DH_GUN_SAVED[gun_id] = (sid, sname, kind, gun_id)
                    if slot == 'main':
                        _b._DH_SKIN_SAVED_MAIN = (sid, sname, kind, gun_id)
                        _b._DH_SKIN_CUR_MAIN   = sname
                    else:
                        _b._DH_SKIN_SAVED_SUB  = (sid, sname, kind, gun_id)
                        _b._DH_SKIN_CUR_SUB    = sname
                # Persist every successful apply
                _save_skin_config()
            except: pass
        elif cmd is not None:
            # Space invalide ce tick — requeue pour le prochain tick
            _b._DH_SKIN_APPLY_CMD = cmd

        # ── Save / Clear config commands (from C++ menu buttons) ─────────────
        if getattr(_b, '_DH_SKIN_CFG_SAVE', False):
            _b._DH_SKIN_CFG_SAVE = False
            _save_skin_config()

        if getattr(_b, '_DH_SKIN_CFG_CLEAR', False):
            _b._DH_SKIN_CFG_CLEAR = False
            _b._DH_GUN_SAVED = {}
            try:
                _os_mod.remove(_SKIN_CFG_PATH)
            except: pass

        ecam  = cam.engine_camera

        local_ca   = getattr(local, 'combat_avatar', None)
        my_faction = getattr(local_ca, 'faction', None)

        current_ids = set()
        best_ent    = None
        best_dist   = float('inf')
        best_sx     = best_sy = 0.0

        # Définie une seule fois par tick, capturée par la boucle entities
        _sbone_cache = {}
        def get_sbone(ent_ref, bone):
            key = (id(ent_ref), bone)
            if key in _sbone_cache:
                return _sbone_cache[key]
            try:
                sp = ecam.GetScreenPointFromWorldPoint(
                    ent_ref.model.GetBoneWorldPosition(bone))
                if sp and sp.z != -1.0:
                    result = to_cocos(sp.x, sp.y)
                else:
                    result = None
            except:
                result = None
            _sbone_cache[key] = result
            return result

        idx = 0
        for ent in space.entities.values():
            if idx >= MAX_ENEMIES: break
            try:
                if not isinstance(ent, CombatAvatar): continue
                if ent is local or ent is local_ca: continue
                if my_faction is not None and getattr(ent, 'faction', None) == my_faction: continue
                if getattr(ent, 'hp', 0) <= 0: continue

                eid = ent.id
                current_ids.add(eid)

                # Chams
                if DO_CHAMS and eid not in _chams_cache:
                    try:
                        ent.model.UseTechHighLightXray((255,50,50),(255,200,0),(255,0,0))
                        _chams_cache.add(eid)
                    except: pass
                elif not DO_CHAMS and eid in _chams_cache:
                    try:
                        ent.model.UseTechHighLightXray((0,0,0),(0,0,0),(0,0,0))
                        _chams_cache.discard(eid)
                    except: pass

                # Aimbot candidate
                if DO_AIMBOT and AIM_ACTIVE:
                    try:
                        sp = ecam.GetScreenPointFromWorldPoint(
                            ent.model.GetBoneWorldPosition(AIM_BONE))
                        if sp and sp.z != -1.0:
                            dist = screen_dist(sp.x, sp.y)
                            if dist < AIM_FOV and dist < best_dist:
                                # Visible check — skip occluded targets when enabled
                                if AIM_VISCHECK and not is_visible(space, ecam, ent, AIM_BONE):
                                    pass
                                else:
                                    best_dist = dist
                                    best_ent  = ent
                                    best_sx   = sp.x
                                    best_sy   = sp.y
                    except: pass

                # ESP
                head = get_bone(ecam, ent, 'biped Head')
                foot = get_bone(ecam, ent, 'biped LeftLeg') or get_bone(ecam, ent, 'biped RightLeg')
                d   = draws[idx]
                lbl = labels[idx]

                if head is None:
                    try:
                        if d is not None: d.setVisible(False)
                    except: pass
                    try:
                        if lbl is not None: lbl.setVisible(False)
                    except: pass
                    try:
                        if dist_labels[idx] is not None: dist_labels[idx].setVisible(False)
                    except: pass
                    try:
                        if skel_draws[idx] is not None: skel_draws[idx].setVisible(False)
                    except: pass
                    idx += 1; continue

                hx, hy = head
                if foot is None:
                    spine = get_bone(ecam, ent, 'biped Spine')
                    if spine: fy = hy - (hy - spine[1]) * 2.8
                    else:
                        try:
                            if d is not None: d.setVisible(False)
                        except: pass
                        try:
                            if lbl is not None: lbl.setVisible(False)
                        except: pass
                        try:
                            if dist_labels[idx] is not None: dist_labels[idx].setVisible(False)
                        except: pass
                        try:
                            if skel_draws[idx] is not None: skel_draws[idx].setVisible(False)
                        except: pass
                        idx += 1; continue
                else:
                    fy = foot[1]

                box_h = abs(hy - fy)
                box_w = box_h * 0.45
                cx    = hx
                x1 = cx - box_w/2;    x2 = cx + box_w/2
                y1 = fy - box_h*0.05; y2 = hy + box_h*0.08

                # Vérifier que le DrawNode est toujours vivant avant tout accès
                try:
                    _d_alive = d is not None and d.getParent() is not None
                except:
                    _d_alive = False

                if _d_alive:
                    try: d.clear()
                    except: pass

                    if DO_BOX:
                        try:
                            d.drawLine(cc.Vec2(x1,y1),cc.Vec2(x2,y1),1.0,WHITE)
                            d.drawLine(cc.Vec2(x2,y1),cc.Vec2(x2,y2),1.0,WHITE)
                            d.drawLine(cc.Vec2(x2,y2),cc.Vec2(x1,y2),1.0,WHITE)
                            d.drawLine(cc.Vec2(x1,y2),cc.Vec2(x1,y1),1.0,WHITE)
                        except: pass

                    if DO_HP:
                        try:
                            max_hp = getattr(ent, 'cur_maxhp', None)
                            if max_hp and max_hp > 0:
                                ratio  = max(0.0, min(1.0, ent.hp / max_hp))
                                hp_col = HP_HI if ratio > 0.6 else (HP_MED if ratio > 0.3 else HP_LOW)
                                bx1_ = x1-2-BAR_W; bx2_ = x1-2
                                h    = y2 - y1
                                ft   = y1 + h * ratio
                                # BG — 4 lines instead of drawSolidPoly (avoids temp Vec2 list UAF)
                                for _yy in (y1, y2):
                                    d.drawLine(cc.Vec2(bx1_,_yy), cc.Vec2(bx2_,_yy), 1.0, HP_BG)
                                d.drawLine(cc.Vec2(bx1_,y1), cc.Vec2(bx1_,y2), 1.0, HP_BG)
                                d.drawLine(cc.Vec2(bx2_,y1), cc.Vec2(bx2_,y2), 1.0, HP_BG)
                                # Filled bar — draw vertical lines pixel by pixel width
                                _bar_step = 1.0
                                _cur_x = bx1_
                                while _cur_x <= bx2_:
                                    d.drawLine(cc.Vec2(_cur_x, y1), cc.Vec2(_cur_x, ft), 1.0, hp_col)
                                    _cur_x += _bar_step
                        except: pass

                    if DO_ARMOR:
                        try:
                            max_armor = getattr(ent, 'base_maxarmor', None)
                            armor     = getattr(ent, 'armor', 0.0)
                            if max_armor and max_armor > 0 and armor > 0:
                                ratio  = max(0.0, min(1.0, armor / max_armor))
                                ax1 = x2+2; ax2_ = x2+2+BAR_W
                                h   = y2 - y1
                                ft  = y1 + h * ratio
                                for _yy in (y1, y2):
                                    d.drawLine(cc.Vec2(ax1,_yy), cc.Vec2(ax2_,_yy), 1.0, AR_BG)
                                d.drawLine(cc.Vec2(ax1,y1), cc.Vec2(ax1,y2), 1.0, AR_BG)
                                d.drawLine(cc.Vec2(ax2_,y1), cc.Vec2(ax2_,y2), 1.0, AR_BG)
                                _cur_x = ax1
                                while _cur_x <= ax2_:
                                    d.drawLine(cc.Vec2(_cur_x, y1), cc.Vec2(_cur_x, ft), 1.0, AR_COL)
                                    _cur_x += 1.0
                        except: pass

                    try: d.setVisible(True)
                    except: pass

                # ── Skeleton ──────────────────────────────────────────────────
                sd = skel_draws[idx]
                try:
                    _sd_alive = sd is not None and sd.getParent() is not None
                except:
                    _sd_alive = False

                if _sd_alive:
                    if DO_SKELETON:
                        try: sd.clear()
                        except: pass
                        drawn = False
                        try:
                            for (b1, b2) in SKEL_BONES:
                                p1 = get_sbone(ent, b1)
                                p2 = get_sbone(ent, b2)
                                if p1 and p2:
                                    sd.drawLine(cc.Vec2(p1[0], p1[1]),
                                                cc.Vec2(p2[0], p2[1]),
                                                1.2, SKEL_COLOR)
                                    drawn = True
                        except: pass
                        try: sd.setVisible(drawn)
                        except: pass
                    else:
                        try: sd.clear(); sd.setVisible(False)
                        except: pass

                if DO_NAME:
                    try:
                        _lbl_alive = lbl is not None and lbl.getParent() is not None
                    except:
                        _lbl_alive = False
                    if _lbl_alive:
                        try:
                            name = "?"
                            n = getattr(ent, 'name', None)
                            if n and isinstance(n, str) and len(n) > 0:
                                name = n
                            elif ent.master and getattr(ent.master, 'name', None):
                                name = str(ent.master.name)
                            lbl.setString(name)
                            lbl.setPositionX(cx)
                            lbl.setPositionY(y2+10)
                            lbl.setVisible(True)
                        except:
                            try: lbl.setVisible(False)
                            except: pass
                else:
                    try: lbl.setVisible(False)
                    except: pass

                # ── Distance label ────────────────────────────────────────────
                dlbl = dist_labels[idx]
                if DO_DIST:
                    try:
                        _dlbl_alive = dlbl is not None and dlbl.getParent() is not None
                    except:
                        _dlbl_alive = False
                    if _dlbl_alive:
                        try:
                            origin   = ecam.GetOrigin()
                            head_pos = ent.model.GetBoneWorldPosition('biped Head')
                            dist_m   = math.sqrt(
                                (head_pos.x - origin.x)**2 +
                                (head_pos.y - origin.y)**2 +
                                (head_pos.z - origin.z)**2)
                            dlbl.setString(f"{dist_m:.0f}m")
                            dlbl.setPositionX(cx)
                            dlbl.setPositionY(y1 - 14)
                            dlbl.setVisible(True)
                        except:
                            try: dlbl.setVisible(False)
                            except: pass
                else:
                    try: dlbl.setVisible(False)
                    except: pass

                idx += 1
            except:
                if idx < MAX_ENEMIES:
                    try:
                        if draws[idx] is not None:       draws[idx].setVisible(False)
                    except: pass
                    try:
                        if labels[idx] is not None:      labels[idx].setVisible(False)
                    except: pass
                    try:
                        if dist_labels[idx] is not None: dist_labels[idx].setVisible(False)
                    except: pass
                    try:
                        if skel_draws[idx] is not None:  skel_draws[idx].setVisible(False)
                    except: pass
                idx += 1

        # Clear stale chams
        for eid in (_chams_cache - current_ids):
            _chams_cache.discard(eid)

        for i in range(idx, MAX_ENEMIES):
            try:
                if draws[i] is not None:       draws[i].setVisible(False)
            except: pass
            try:
                if labels[i] is not None:      labels[i].setVisible(False)
            except: pass
            try:
                if dist_labels[i] is not None: dist_labels[i].setVisible(False)
            except: pass
            try:
                if skel_draws[i] is not None:  skel_draws[i].setVisible(False)
            except: pass

        # Aimbot — seulement si la touche est enfoncée
        if DO_AIMBOT and AIM_ACTIVE and best_ent is not None:
            try:
                import random as _rnd
                # Skip ~1 tick sur 8 aléatoirement — casse le pattern fixe 60fps
                if _rnd.randint(0, 7) == 0:
                    pass
                else:
                    placer = cam.placer
                    dpx =  (best_sx - 960.0)
                    dpy = -(best_sy - 540.0)

                    # smooth légèrement variable chaque tick (±10%)
                    t = 1.0 / (max(1.0, AIM_SMOOTH * _rnd.uniform(0.90, 1.10)) * 60.0)
                    dpx *= t
                    dpy *= t

                    # pixels → degrés (FOV 90° ≈ 960px)
                    yaw_deg   = dpx / 10.67
                    pitch_deg = dpy / 10.67

                    # Clamp anti-snap
                    MAX_DEG = 5.0
                    yaw_deg   = max(-MAX_DEG, min(MAX_DEG, yaw_deg))
                    pitch_deg = max(-MAX_DEG, min(MAX_DEG, pitch_deg))
                    placer.Rotate(yaw_deg, pitch_deg)
            except: pass
    except: pass

_b._esp_tick_fn = esp_tick
try:
    StoryTick._instance.Add(esp_tick, 0)
except:
    pass
print("[+] Cheat loaded — ImGui menu controls features via builtins._DH_* flags")

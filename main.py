import json
import os
import subprocess
import sys
import pygame

VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720

# When run as PyInstaller exe, use the folder containing the exe so data lives beside it
if getattr(sys, "frozen", False):
    LAUNCHER_DIR = os.path.dirname(sys.executable)
else:
    LAUNCHER_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(LAUNCHER_DIR, "data")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")
GAMES_PATH = os.path.join(DATA_DIR, "games.json")
RECENTS_PATH = os.path.join(DATA_DIR, "recents.json")

# All supported systems for filtering the library
OS_OPTIONS = ["windows", "mac", "linux", "chromeos"]


def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def detect_current_os():
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "mac"
    if os.environ.get("CHROMEOS") == "1" or os.path.exists("/dev/cros_usb"):
        return "chromeos"
    return "linux"


def create_window(settings):
    pygame.display.init()
    info = pygame.display.Info()

    base_w, base_h = VIRTUAL_WIDTH, VIRTUAL_HEIGHT
    base_scale = min(info.current_w / base_w, info.current_h / base_h)
    user_scale = float(settings.get("resolution_scale", 1.0))
    scale = max(0.5, min(base_scale * user_scale, 1.5))

    win_w, win_h = int(base_w * scale), int(base_h * scale)
    flags = pygame.RESIZABLE
    if settings.get("fullscreen", False):
        flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((win_w, win_h), flags)
    pygame.display.set_caption("My Game Launcher")

    return screen, scale


def point_in_rect(pos, rect):
    return rect.collidepoint(pos)


def run_game(game, launcher_dir):
    """Launch a game. path can be relative to launcher dir or absolute."""
    path = game.get("path") or game.get("script")
    if not path:
        return
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.join(launcher_dir, path))
    if not os.path.isfile(path):
        return
    try:
        subprocess.Popen([sys.executable, path], cwd=os.path.dirname(path))
    except Exception:
        pass


def add_to_recents(game_id):
    """Prepend game_id to recents list (most recent first), keep last 20."""
    recents = load_json(RECENTS_PATH, [])
    if game_id in recents:
        recents.remove(game_id)
    recents.insert(0, game_id)
    save_json(RECENTS_PATH, recents[:20])


def main():
    pygame.init()
    clock = pygame.time.Clock()

    default_settings = {
        "fullscreen": False,
        "theme": "dark",
        "resolution_scale": 1.0,
        "ui_os_filter": detect_current_os(),
        "mode": "player",
        "sound_enabled": True,
    }
    settings = load_json(SETTINGS_PATH, default_settings)
    games = load_json(GAMES_PATH, [])

    need_recreate_window = False
    screen, scale = create_window(settings)
    virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    current_mode = settings.get("mode", "player")
    os_filter = settings.get("ui_os_filter", detect_current_os())
    current_view = "games"  # "games", "recents", "settings"

    font_logo = pygame.font.SysFont("segoeui", 32, bold=True)
    font_menu = pygame.font.SysFont("segoeui", 24)
    font_body = pygame.font.SysFont("segoeui", 22)

    # Layout constants
    sidebar_width = 260
    top_bar_height = 64

    # Predefine sidebar menu items
    menu_items = [
        {"id": "games", "label": "Games"},
        {"id": "recents", "label": "Recents"},
        {"id": "settings", "label": "Settings"},
    ]

    # Input state for PIN prompt
    pin_active = False
    pin_entered = ""
    PIN_CODE = "1234"

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        win_w, win_h = screen.get_size()
        scale_x = VIRTUAL_WIDTH / win_w
        scale_y = VIRTUAL_HEIGHT / win_h
        v_mouse = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        # Recreate window if fullscreen was toggled
        if need_recreate_window:
            screen, scale = create_window(settings)
            need_recreate_window = False

        # Games available for current OS filter
        filtered_games = [g for g in games if os_filter in g.get("platforms", [])]
        # Recents: order by recents list, only include games in library and for this OS
        recents_ids = load_json(RECENTS_PATH, [])
        recent_games = []
        seen = set()
        for rid in recents_ids:
            if rid in seen:
                continue
            for g in games:
                if g.get("id") == rid and os_filter in g.get("platforms", []):
                    recent_games.append(g)
                    seen.add(rid)
                    break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.VIDEORESIZE and not settings.get("fullscreen", False):
                screen = pygame.display.set_mode((max(400, event.w), max(300, event.h)), pygame.RESIZABLE)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if pin_active:
                        pin_active = False
                        pin_entered = ""
                    else:
                        running = False
                elif pin_active:
                    if event.key == pygame.K_RETURN:
                        if pin_entered == PIN_CODE:
                            current_mode = "developer"
                            pin_active = False
                            pin_entered = ""
                        else:
                            pin_entered = ""
                    elif event.key == pygame.K_BACKSPACE:
                        pin_entered = pin_entered[:-1]
                    elif event.unicode.isdigit() and len(pin_entered) < 4:
                        pin_entered += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pin_active:
                    # clicks are ignored while PIN dialog is open
                    pass
                else:
                    # Sidebar item clicks (same rects as drawn menu items)
                    for idx, item in enumerate(menu_items):
                        item_rect = pygame.Rect(
                            0,
                            top_bar_height + 60 + idx * 56,
                            sidebar_width,
                            48,
                        )
                        if point_in_rect(v_mouse, item_rect):
                            current_view = item["id"]

                    # Settings view: Developer mode row + OS selector
                    if current_view == "settings":
                        dev_rect = pygame.Rect(
                            sidebar_width + 32,
                            top_bar_height + 120,
                            VIRTUAL_WIDTH - sidebar_width - 64,
                            56,
                        )
                        if point_in_rect(v_mouse, dev_rect):
                            if current_mode == "developer":
                                current_mode = "player"
                            else:
                                pin_active = True
                                pin_entered = ""
                        # OS selector: only in developer mode (same Y as drawn: 300)
                        if current_mode == "developer":
                            for idx, os_name in enumerate(OS_OPTIONS):
                                os_btn_w = 140
                                os_btn_x = sidebar_width + 32 + idx * (os_btn_w + 12)
                                os_btn_rect = pygame.Rect(os_btn_x, top_bar_height + 300, os_btn_w, 44)
                                if point_in_rect(v_mouse, os_btn_rect):
                                    os_filter = os_name
                                    break

                        # Fullscreen toggle row
                        fs_rect = pygame.Rect(sidebar_width + 32, top_bar_height + 360, VIRTUAL_WIDTH - sidebar_width - 64, 56)
                        if point_in_rect(v_mouse, fs_rect):
                            settings["fullscreen"] = not settings.get("fullscreen", False)
                            need_recreate_window = True
                            save_json(SETTINGS_PATH, settings)

                        # Sound toggle row
                        sound_rect = pygame.Rect(sidebar_width + 32, top_bar_height + 428, VIRTUAL_WIDTH - sidebar_width - 64, 56)
                        if point_in_rect(v_mouse, sound_rect):
                            settings["sound_enabled"] = not settings.get("sound_enabled", True)
                            save_json(SETTINGS_PATH, settings)

                    # Games view: Play button clicks
                    if current_view == "games":
                        row_h = 72
                        content_left = sidebar_width + 32
                        content_w = VIRTUAL_WIDTH - content_left - 32
                        play_w, play_h = 100, 36
                        for idx, g in enumerate(filtered_games):
                            row_y = top_bar_height + 88 + idx * row_h
                            play_rect = pygame.Rect(
                                content_left + content_w - play_w - 16,
                                row_y + (row_h - play_h) // 2,
                                play_w,
                                play_h,
                            )
                            if point_in_rect(v_mouse, play_rect):
                                run_game(g, LAUNCHER_DIR)
                                add_to_recents(g.get("id", ""))
                                break
                    # Recents view: Play button clicks
                    if current_view == "recents":
                        row_h = 72
                        content_left = sidebar_width + 32
                        content_w = VIRTUAL_WIDTH - content_left - 32
                        play_w, play_h = 100, 36
                        for idx, g in enumerate(recent_games):
                            row_y = top_bar_height + 88 + idx * row_h
                            play_rect = pygame.Rect(
                                content_left + content_w - play_w - 16,
                                row_y + (row_h - play_h) // 2,
                                play_w,
                                play_h,
                            )
                            if point_in_rect(v_mouse, play_rect):
                                run_game(g, LAUNCHER_DIR)
                                add_to_recents(g.get("id", ""))
                                break

        theme_dark = settings.get("theme", "dark") == "dark"
        bg_color = (18, 18, 22) if theme_dark else (240, 242, 247)
        top_bar = (10, 10, 18) if theme_dark else (255, 255, 255)
        sidebar_bg = (26, 26, 36) if theme_dark else (246, 247, 252)
        sidebar_active = (70, 120, 255) if theme_dark else (70, 120, 255)
        sidebar_hover = (40, 60, 120) if theme_dark else (220, 228, 250)
        text_main = (240, 240, 245) if theme_dark else (25, 25, 30)
        text_muted = (150, 150, 165) if theme_dark else (100, 100, 115)

        virtual_surface.fill(bg_color)

        # Top bar
        pygame.draw.rect(virtual_surface, top_bar, (0, 0, VIRTUAL_WIDTH, top_bar_height))
        logo_text = "My Game Launcher"
        logo_render = font_logo.render(logo_text, True, text_main)
        virtual_surface.blit(logo_render, (sidebar_width + 24, top_bar_height // 2 - logo_render.get_height() // 2))

        # Mode / OS info (top-right)
        mode_label = f"Mode: {current_mode.capitalize()}"
        mode_render = font_body.render(mode_label, True, text_muted)
        os_label = f"Target OS: {os_filter.capitalize()}"
        os_render = font_body.render(os_label, True, text_muted)
        virtual_surface.blit(
            mode_render,
            (VIRTUAL_WIDTH - mode_render.get_width() - 32, 14),
        )
        virtual_surface.blit(
            os_render,
            (VIRTUAL_WIDTH - os_render.get_width() - 32, 34),
        )

        # Sidebar
        pygame.draw.rect(
            virtual_surface,
            sidebar_bg,
            (0, top_bar_height, sidebar_width, VIRTUAL_HEIGHT - top_bar_height),
        )

        # Sidebar title
        small_logo = font_body.render("Library", True, text_muted)
        virtual_surface.blit(small_logo, (24, top_bar_height + 20))

        # Sidebar menu items
        for idx, item in enumerate(menu_items):
            y = top_bar_height + 60 + idx * 56
            item_rect = pygame.Rect(0, y, sidebar_width, 48)
            hovered = point_in_rect(v_mouse, item_rect)
            is_active = current_view == item["id"]

            if is_active:
                pygame.draw.rect(virtual_surface, sidebar_active, item_rect.inflate(-24, 0), border_radius=12)
            elif hovered:
                pygame.draw.rect(virtual_surface, sidebar_hover, item_rect.inflate(-24, 0), border_radius=12)

            label_color = (255, 255, 255) if (theme_dark and (is_active or hovered)) else text_main
            label = font_menu.render(item["label"], True, label_color)
            virtual_surface.blit(label, (32, y + 12))

        # Main content area
        content_rect = pygame.Rect(
            sidebar_width,
            top_bar_height,
            VIRTUAL_WIDTH - sidebar_width,
            VIRTUAL_HEIGHT - top_bar_height,
        )

        if current_view == "games":
            pygame.draw.rect(virtual_surface, bg_color, content_rect)
            title = font_body.render("Games", True, text_main)
            virtual_surface.blit(title, (sidebar_width + 32, top_bar_height + 24))
            row_h = 72
            content_left = sidebar_width + 32
            content_w = VIRTUAL_WIDTH - content_left - 32
            play_w, play_h = 100, 36
            card_bg = (30, 32, 42) if theme_dark else (255, 255, 255)
            for idx, g in enumerate(filtered_games):
                row_y = top_bar_height + 88 + idx * row_h
                row_rect = pygame.Rect(content_left, row_y, content_w, row_h - 8)
                pygame.draw.rect(virtual_surface, card_bg, row_rect, border_radius=10)
                name = g.get("name", g.get("id", "Unknown"))
                name_surf = font_body.render(name, True, text_main)
                virtual_surface.blit(name_surf, (content_left + 16, row_y + (row_h - name_surf.get_height()) // 2 - 4))
                play_rect = pygame.Rect(content_left + content_w - play_w - 16, row_y + (row_h - play_h) // 2, play_w, play_h)
                play_hover = point_in_rect(v_mouse, play_rect)
                play_color = (60, 140, 255) if play_hover else (70, 120, 255)
                pygame.draw.rect(virtual_surface, play_color, play_rect, border_radius=8)
                play_text = font_body.render("Play", True, (255, 255, 255))
                virtual_surface.blit(play_text, (play_rect.centerx - play_text.get_width() // 2, play_rect.centery - play_text.get_height() // 2))
            if not filtered_games:
                empty = font_body.render("No games for this system. Change Target OS in Settings.", True, text_muted)
                virtual_surface.blit(empty, (content_left, top_bar_height + 88))
        elif current_view == "recents":
            pygame.draw.rect(virtual_surface, bg_color, content_rect)
            title = font_body.render("Recents", True, text_main)
            virtual_surface.blit(title, (sidebar_width + 32, top_bar_height + 24))
            row_h = 72
            content_left = sidebar_width + 32
            content_w = VIRTUAL_WIDTH - content_left - 32
            play_w, play_h = 100, 36
            card_bg = (30, 32, 42) if theme_dark else (255, 255, 255)
            for idx, g in enumerate(recent_games):
                row_y = top_bar_height + 88 + idx * row_h
                row_rect = pygame.Rect(content_left, row_y, content_w, row_h - 8)
                pygame.draw.rect(virtual_surface, card_bg, row_rect, border_radius=10)
                name = g.get("name", g.get("id", "Unknown"))
                name_surf = font_body.render(name, True, text_main)
                virtual_surface.blit(name_surf, (content_left + 16, row_y + (row_h - name_surf.get_height()) // 2 - 4))
                play_rect = pygame.Rect(content_left + content_w - play_w - 16, row_y + (row_h - play_h) // 2, play_w, play_h)
                play_hover = point_in_rect(v_mouse, play_rect)
                play_color = (60, 140, 255) if play_hover else (70, 120, 255)
                pygame.draw.rect(virtual_surface, play_color, play_rect, border_radius=8)
                play_text = font_body.render("Play", True, (255, 255, 255))
                virtual_surface.blit(play_text, (play_rect.centerx - play_text.get_width() // 2, play_rect.centery - play_text.get_height() // 2))
            if not recent_games:
                empty = font_body.render("No recent games. Play something from Games!", True, text_muted)
                virtual_surface.blit(empty, (content_left, top_bar_height + 88))
        elif current_view == "settings":
            pygame.draw.rect(virtual_surface, bg_color, content_rect)
            title = font_body.render("Settings", True, text_main)
            virtual_surface.blit(title, (sidebar_width + 32, top_bar_height + 24))

            # Developer mode row
            dev_rect = pygame.Rect(
                sidebar_width + 32,
                top_bar_height + 120,
                VIRTUAL_WIDTH - sidebar_width - 64,
                56,
            )
            dev_hover = point_in_rect(v_mouse, dev_rect)
            row_bg = (40, 60, 120) if (theme_dark and dev_hover) else (230, 235, 248) if (not theme_dark and dev_hover) else (30, 32, 42) if theme_dark else (255, 255, 255)
            pygame.draw.rect(virtual_surface, row_bg, dev_rect, border_radius=12)

            dev_label = "Developer mode"
            dev_status = "On" if current_mode == "developer" else "Off"
            dev_text = font_body.render(dev_label, True, text_main)
            status_color = (90, 200, 120) if current_mode == "developer" else text_muted
            dev_status_text = font_body.render(dev_status, True, status_color)

            virtual_surface.blit(dev_text, (dev_rect.x + 16, dev_rect.y + 16))
            virtual_surface.blit(
                dev_status_text,
                (dev_rect.right - dev_status_text.get_width() - 16, dev_rect.y + 16),
            )

            hint = font_body.render("Click to toggle. PIN required to enable.", True, text_muted)
            virtual_surface.blit(hint, (sidebar_width + 32, top_bar_height + 190))

            # Target OS selector (developer only)
            if current_mode == "developer":
                os_label = font_body.render("Target OS (library filter):", True, text_main)
                virtual_surface.blit(os_label, (sidebar_width + 32, top_bar_height + 268))
                os_btn_w = 140
                for idx, os_name in enumerate(OS_OPTIONS):
                    os_btn_x = sidebar_width + 32 + idx * (os_btn_w + 12)
                    os_btn_rect = pygame.Rect(os_btn_x, top_bar_height + 300, os_btn_w, 44)
                    is_selected = os_filter == os_name
                    os_btn_color = (70, 120, 255) if is_selected else ((50, 54, 70) if theme_dark else (230, 232, 240))
                    pygame.draw.rect(virtual_surface, os_btn_color, os_btn_rect, border_radius=10)
                    os_cap = os_name.capitalize()
                    if os_name == "chromeos":
                        os_cap = "Chrome OS"
                    os_surf = font_body.render(os_cap, True, (255, 255, 255) if is_selected else text_main)
                    virtual_surface.blit(os_surf, (os_btn_rect.centerx - os_surf.get_width() // 2, os_btn_rect.centery - os_surf.get_height() // 2))
            else:
                os_hint = font_body.render("Target OS: Developer mode only.", True, text_muted)
                virtual_surface.blit(os_hint, (sidebar_width + 32, top_bar_height + 278))

            # Fullscreen toggle
            fs_rect = pygame.Rect(sidebar_width + 32, top_bar_height + 360, VIRTUAL_WIDTH - sidebar_width - 64, 56)
            fs_hover = point_in_rect(v_mouse, fs_rect)
            fs_bg = (40, 60, 120) if (theme_dark and fs_hover) else (230, 235, 248) if (not theme_dark and fs_hover) else (30, 32, 42) if theme_dark else (255, 255, 255)
            pygame.draw.rect(virtual_surface, fs_bg, fs_rect, border_radius=12)
            virtual_surface.blit(font_body.render("Fullscreen", True, text_main), (fs_rect.x + 16, fs_rect.y + 16))
            fs_status = "On" if settings.get("fullscreen") else "Off"
            virtual_surface.blit(font_body.render(fs_status, True, (90, 200, 120) if settings.get("fullscreen") else text_muted), (fs_rect.right - 50, fs_rect.y + 16))

            # Sound toggle
            sound_rect = pygame.Rect(sidebar_width + 32, top_bar_height + 428, VIRTUAL_WIDTH - sidebar_width - 64, 56)
            sound_hover = point_in_rect(v_mouse, sound_rect)
            sound_bg = (40, 60, 120) if (theme_dark and sound_hover) else (230, 235, 248) if (not theme_dark and sound_hover) else (30, 32, 42) if theme_dark else (255, 255, 255)
            pygame.draw.rect(virtual_surface, sound_bg, sound_rect, border_radius=12)
            virtual_surface.blit(font_body.render("Sound", True, text_main), (sound_rect.x + 16, sound_rect.y + 16))
            sound_status = "On" if settings.get("sound_enabled", True) else "Off"
            virtual_surface.blit(font_body.render(sound_status, True, (90, 200, 120) if settings.get("sound_enabled", True) else text_muted), (sound_rect.right - 40, sound_rect.y + 16))

        # PIN overlay dialog
        if pin_active:
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            virtual_surface.blit(overlay, (0, 0))

            dialog_w, dialog_h = 420, 220
            dialog_rect = pygame.Rect(
                (VIRTUAL_WIDTH - dialog_w) // 2,
                (VIRTUAL_HEIGHT - dialog_h) // 2,
                dialog_w,
                dialog_h,
            )
            pygame.draw.rect(virtual_surface, (20, 22, 30) if theme_dark else (250, 250, 252), dialog_rect, border_radius=12)

            title = font_body.render("Enter developer PIN", True, text_main)
            virtual_surface.blit(
                title,
                (dialog_rect.x + 24, dialog_rect.y + 24),
            )

            pin_box = pygame.Rect(
                dialog_rect.x + 24,
                dialog_rect.y + 80,
                dialog_w - 48,
                48,
            )
            pygame.draw.rect(virtual_surface, (35, 37, 50) if theme_dark else (235, 237, 245), pin_box, border_radius=10)

            masked = "•" * len(pin_entered)
            pin_text = font_body.render(masked or "1234", True, text_main if masked else text_muted)
            virtual_surface.blit(
                pin_text,
                (pin_box.x + 16, pin_box.y + 12),
            )

            help_text = font_body.render("Press Enter to confirm, Esc to cancel", True, text_muted)
            virtual_surface.blit(
                help_text,
                (dialog_rect.x + 24, dialog_rect.y + dialog_h - 40),
            )

        # Scale virtual surface to window
        win_w, win_h = screen.get_size()
        scaled = pygame.transform.smoothscale(virtual_surface, (win_w, win_h))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    settings["mode"] = current_mode
    settings["ui_os_filter"] = os_filter
    save_json(SETTINGS_PATH, settings)

    pygame.quit()


if __name__ == "__main__":
    main()



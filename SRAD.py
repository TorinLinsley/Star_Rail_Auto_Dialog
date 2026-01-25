from typing import Dict, Callable, Any, Optional, TypeAlias, Tuple
import pyautogui, keyboard, threading, time, sys, os, platform,cv2,ctypes
import pygetwindow as gw
import numpy as np

if ctypes.windll.shell32.IsUserAnAdmin() == 0:
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit(0)

ThreadingEvent: TypeAlias = threading.Event
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DETECT_INTERVAL = 0.02    # 检测间隔时间（秒）
OPERATE_INTERVAL = 0.2    # 操作间隔时间（秒）
SKIP_CLICK_INTERVAL = 0.7    # 跳过点击间隔时间（秒）
POPUP_BUFFER_DELAY = 0.1    # 弹出框缓冲延迟时间（秒）
CONSOLE_REFRESH_INTERVAL = 1    # 控制台刷新间隔时间（秒）

IMAGE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "1": {"path": os.path.join(CURRENT_DIR, "img", "1.png"), "confidence": 0.7},
    "2": {"path": os.path.join(CURRENT_DIR, "img", "2.png"), "confidence": 0.7},
    "once_again": {"path": os.path.join(CURRENT_DIR, "img", "once_again.png"), "confidence": 0.69},
    "assign_again": {"path": os.path.join(CURRENT_DIR, "img", "assign_again.png"), "confidence": 0.72},
    "cancel": {"path": os.path.join(CURRENT_DIR, "img", "cancel.png"), "confidence": 0.7},
    "confirm": {"path": os.path.join(CURRENT_DIR, "img", "confirm.png"), "confidence": 0.7},
    "dialog_history": {"path": os.path.join(CURRENT_DIR, "img", "dialog.png"), "confidence": 0.69},
    "enter_game": {"path": os.path.join(CURRENT_DIR, "img", "entergame.png"), "confidence": 0.69},
    "quit_level": {"path": os.path.join(CURRENT_DIR, "img", "quit_level.png"), "confidence": 0.69},
    "receive": {"path": os.path.join(CURRENT_DIR, "img", "receive.png"), "confidence": 0.69},
    "sound_settings": {"path": os.path.join(CURRENT_DIR, "img", "sound_settings.png"), "confidence": 0.69},
    "skip_dialog": {"path": os.path.join(CURRENT_DIR, "img", "skip_dialog.png"), "confidence": 0.69},
    "give_item": {"path": os.path.join(CURRENT_DIR, "img", "give_item.png"), "confidence": 0.69},
    "quit_ok": {"path": os.path.join(CURRENT_DIR, "img", "quit_ok.png"), "confidence": 0.69}
}

def get_game_window() -> Optional[gw.Window]:
    windows = gw.getWindowsWithTitle("崩坏：星穹铁道")
    return windows[0] if windows else None

def cv2_template_match(
    template_path: str,
    confidence_threshold: float,
    region: Optional[Tuple[int, int, int, int]] = None
) -> Optional[Tuple[int, int, int, int]]:
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    if template is None:
        return None
    template_h, template_w = template.shape[:2]
    
    game_window = get_game_window()
    if not game_window:
        return None
    window_w = game_window.right - game_window.left
    window_h = game_window.bottom - game_window.top
    
    base_w, base_h = 1440, 900
    scale_x = window_w / base_w
    scale_y = window_h / base_h
    
    scaled_template = cv2.resize(
        template,
        (int(template_w * scale_x), int(template_h * scale_y)),
        interpolation=cv2.INTER_AREA
    )
    scaled_h, scaled_w = scaled_template.shape[:2]
    
    screenshot = pyautogui.screenshot(region=region)
    screenshot_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
    
    result = cv2.matchTemplate(screenshot_gray, scaled_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val < confidence_threshold:
        return None
    
    left = max_loc[0] + (region[0] if region else 0)
    top = max_loc[1] + (region[1] if region else 0)
    return (left, top, scaled_w, scaled_h)

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

os.system("mode 57,35")
os.system("title 星铁自动剧情工具")

def test1(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    threads: list[threading.Thread] = [
        threading.Thread(target=test1_1, args=(stop_event, share_state)),
        threading.Thread(target=test1_2, args=(stop_event, share_state)),
        threading.Thread(target=test1_3, args=(stop_event, share_state)),
        threading.Thread(target=test1_4, args=(stop_event, share_state)),
        threading.Thread(target=test1_5, args=(stop_event, share_state)),
        threading.Thread(target=test1_6, args=(stop_event, share_state))
    ]

    for t in threads:
        t.daemon = True
        t.start()
    
    with share_state["lock"]:
        share_state["func_status"]["跳过剧情"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "跳过剧情分支线程已启动"
        }

    while not stop_event.is_set():
        time.sleep(OPERATE_INTERVAL)

    with share_state["lock"]:
        share_state["func_status"]["跳过剧情"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "跳过剧情分支线程已退出"
        }

def test1_1(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    while not stop_event.is_set():
        try:
            game_window = get_game_window()
            if game_window:
                with share_state["lock"]:
                    share_state["window_ready"] = True
                    base_skip_x_offset = 256
                    base_skip_y_offset = 50
                    base_w, base_h = 1440, 900
                    window_w = game_window.right - game_window.left
                    scale_x = window_w / base_w
                    
                    skip_btn_x = game_window.right - int(base_skip_x_offset * scale_x)
                    skip_btn_y = game_window.top + int(base_skip_y_offset * (game_window.height / base_h))
                    
                    share_state["skip_btn_x"] = skip_btn_x
                    share_state["skip_btn_y"] = skip_btn_y
                    share_state["func_status"]["跳过剧情"]["detail"] = f"窗口就绪，跳过按钮坐标：({share_state['skip_btn_x']}, {share_state['skip_btn_y']})"
                time.sleep(1)
            else:
                with share_state["lock"]:
                    share_state["window_ready"] = False
                    share_state["func_status"]["跳过剧情"]["detail"] = "未找到崩坏：星穹铁道窗口"
                time.sleep(0.5)
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过剧情"]["detail"] = f"异常：{str(e)[:50]}"
            time.sleep(0.5)

def test1_2(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
        if not window_ready:
            time.sleep(DETECT_INTERVAL)
            continue

        sound_found = False
        try:
            config = IMAGE_CONFIGS["sound_settings"]
            match_pos = cv2_template_match(config["path"], config["confidence"])
            if match_pos:
                sound_found = True
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过剧情"]["detail"] = f"声音识别异常：{str(e)[:50]}"

        with share_state["lock"]:
            share_state["sound_found"] = sound_found
            if sound_found:
                share_state["func_status"]["跳过剧情"]["detail"] = "已识别到声音设置按钮"

        time.sleep(DETECT_INTERVAL)

def test1_3(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    space_interval = 1/20
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
            sound_found = share_state["sound_found"]

        if window_ready and sound_found:
            try:
                keyboard.press_and_release('space')
                with share_state["lock"]:
                    share_state["func_status"]["跳过剧情"]["last_operate"] = "触发空格"
            except Exception as e:
                with share_state["lock"]:
                    share_state["func_status"]["跳过剧情"]["detail"] = f"空格触发异常：{str(e)[:50]}"
            time.sleep(space_interval)
        else:
            time.sleep(OPERATE_INTERVAL)

def test1_4(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
            sound_found = share_state["sound_found"]
            skip_x = share_state["skip_btn_x"]
            skip_y = share_state["skip_btn_y"]

        if window_ready and sound_found:
            try:
                pyautogui.click(skip_x, skip_y)
                with share_state["lock"]:
                    share_state["func_status"]["跳过剧情"]["last_operate"] = f"点击跳过按钮 ({skip_x}, {skip_y})"
            except Exception as e:
                with share_state["lock"]:
                    share_state["func_status"]["跳过剧情"]["detail"] = f"跳过按钮点击异常：{str(e)[:50]}"
            time.sleep(SKIP_CLICK_INTERVAL)
        else:
            time.sleep(OPERATE_INTERVAL)

def test1_5(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
        if not window_ready:
            time.sleep(DETECT_INTERVAL)
            continue

        confirm_pos = None
        try:
            config = IMAGE_CONFIGS["confirm"]
            confirm_pos = cv2_template_match(config["path"], config["confidence"])
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过剧情"]["detail"] = f"确认按钮识别异常：{str(e)[:50]}"

        if not confirm_pos:
            time.sleep(DETECT_INTERVAL)
            continue

        time.sleep(POPUP_BUFFER_DELAY)
        confirm_center = (confirm_pos[0] + confirm_pos[2]//2, confirm_pos[1] + confirm_pos[3]//2)
        try:
            pyautogui.click(confirm_center[0], confirm_center[1])
            with share_state["lock"]:
                share_state["func_status"]["跳过剧情"]["last_operate"] = f"点击确认按钮 ({confirm_center[0]}, {confirm_center[1]})"
                share_state["func_status"]["跳过剧情"]["detail"] = "已识别并点击确认按钮"
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过剧情"]["detail"] = f"确认按钮点击异常：{str(e)[:50]}"
        
        time.sleep(OPERATE_INTERVAL)

def test1_6(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    operate_interval = 0.2
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
        if not window_ready:
            time.sleep(operate_interval)
            continue

        img1_found = False
        try:
            config = IMAGE_CONFIGS["1"]
            if cv2_template_match(config["path"], config["confidence"]):
                img1_found = True
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过剧情"]["detail"] = f"数字1识别异常：{str(e)[:50]}"

        if img1_found:
            try:
                keyboard.press_and_release('1')
                with share_state["lock"]:
                    share_state["func_status"]["跳过剧情"]["last_operate"] = "触发数字1"
            except Exception as e:
                with share_state["lock"]:
                    share_state["func_status"]["跳过剧情"]["detail"] = f"数字1触发异常：{str(e)[:50]}"
        
        time.sleep(operate_interval)

def test2(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    threads: list[threading.Thread] = [
        threading.Thread(target=test2_1, args=(stop_event, share_state)),
        threading.Thread(target=test2_2, args=(stop_event, share_state))
    ]

    for t in threads:
        t.daemon = True
        t.start()
    
    with share_state["lock"]:
        share_state["func_status"]["跳过获得物品界面"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "跳过获得物品界面线程已启动"
        }

    operate_interval = 0.2
    while not stop_event.is_set():
        try:
            game_window = get_game_window()
            if game_window:
                window_width = game_window.right - game_window.left
                window_height = game_window.bottom - game_window.top
                
                target_x = game_window.left + (window_width / 2)
                target_y = game_window.bottom - (window_height * 0.05)
                
                with share_state["lock"]:
                    share_state["window_ready"] = True
                    share_state["give_item_target_x"] = target_x
                    share_state["give_item_target_y"] = target_y
                    share_state["func_status"]["跳过获得物品界面"]["detail"] = f"物品点击坐标：X={target_x:.1f}, Y={target_y:.1f}"
            else:
                with share_state["lock"]:
                    share_state["window_ready"] = False
                    share_state["func_status"]["跳过获得物品界面"]["detail"] = "未找到崩坏：星穹铁道窗口"
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过获得物品界面"]["detail"] = f"坐标计算异常：{str(e)[:50]}"

        time.sleep(operate_interval)

    with share_state["lock"]:
        share_state["func_status"]["跳过获得物品界面"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "跳过获得物品界面线程已退出"
        }

def test2_1(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    operate_interval = 0.2
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
        if not window_ready:
            time.sleep(operate_interval)
            continue

        give_item_found = False
        try:
            config = IMAGE_CONFIGS["give_item"]
            if cv2_template_match(config["path"], config["confidence"]):
                give_item_found = True
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["跳过获得物品界面"]["detail"] = f"物品图片识别异常：{str(e)[:50]}"

        with share_state["lock"]:
            share_state["give_item_found"] = give_item_found
            if give_item_found:
                share_state["func_status"]["跳过获得物品界面"]["detail"] = "已识别到获得物品界面"
        
        time.sleep(operate_interval)

def test2_2(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    operate_interval = 0.2
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
            give_item_found = share_state.get("give_item_found", False)
            target_x = share_state.get("give_item_target_x", 0)
            target_y = share_state.get("give_item_target_y", 0)

        if window_ready and give_item_found:
            try:
                pyautogui.click(target_x, target_y)
                with share_state["lock"]:
                    share_state["func_status"]["跳过获得物品界面"]["last_operate"] = f"点击物品界面 ({target_x:.1f}, {target_y:.1f})"
            except Exception as e:
                with share_state["lock"]:
                    share_state["func_status"]["跳过获得物品界面"]["detail"] = f"物品界面点击异常：{str(e)[:50]}"
        
        time.sleep(operate_interval)

def test3(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    threads: list[threading.Thread] = [
        threading.Thread(target=test3_1, args=(stop_event, share_state)),
        threading.Thread(target=test3_2, args=(stop_event, share_state))
    ]

    for t in threads:
        t.daemon = True
        t.start()
    
    with share_state["lock"]:
        share_state["func_status"]["点击进入游戏"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "点击进入游戏线程已启动"
        }

    while not stop_event.is_set():
        try:
            game_window = get_game_window()
            if game_window:
                center_x = (game_window.left + game_window.right) / 2
                center_y = (game_window.top + game_window.bottom) / 2

                with share_state["lock"]:
                    share_state["window_ready"] = True
                    share_state["enter_game_center_x"] = center_x
                    share_state["enter_game_center_y"] = center_y
                    share_state["func_status"]["点击进入游戏"]["detail"] = f"窗口中心坐标：X={center_x:.1f}, Y={center_y:.1f}"
            else:
                with share_state["lock"]:
                    share_state["window_ready"] = False
                    share_state["func_status"]["点击进入游戏"]["detail"] = "未找到崩坏：星穹铁道窗口"
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["点击进入游戏"]["detail"] = f"坐标计算异常：{str(e)[:50]}"

        time.sleep(OPERATE_INTERVAL)

    with share_state["lock"]:
        share_state["func_status"]["点击进入游戏"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "点击进入游戏线程已退出"
        }

def test3_1(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
        if not window_ready:
            time.sleep(OPERATE_INTERVAL)
            continue

        enter_game_found = False
        try:
            config = IMAGE_CONFIGS["enter_game"]
            if cv2_template_match(config["path"], config["confidence"]):
                enter_game_found = True
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["点击进入游戏"]["detail"] = f"进入游戏图片识别异常：{str(e)[:50]}"

        with share_state["lock"]:
            share_state["enter_game_found"] = enter_game_found
            if enter_game_found:
                share_state["func_status"]["点击进入游戏"]["detail"] = "已识别到进入游戏按钮"

        time.sleep(OPERATE_INTERVAL)

def test3_2(stop_event: ThreadingEvent, share_state: Dict[str, Any]) -> None:
    while not stop_event.is_set():
        with share_state["lock"]:
            window_ready = share_state["window_ready"]
            enter_game_found = share_state.get("enter_game_found", False)
            center_x = share_state.get("enter_game_center_x", 0)
            center_y = share_state.get("enter_game_center_y", 0)

        if window_ready and enter_game_found:
            try:
                pyautogui.click(center_x, center_y)
                with share_state["lock"]:
                    share_state["func_status"]["点击进入游戏"]["last_operate"] = f"点击进入游戏 ({center_x:.1f}, {center_y:.1f})"
            except Exception as e:
                with share_state["lock"]:
                    share_state["func_status"]["点击进入游戏"]["detail"] = f"进入游戏点击异常：{str(e)[:50]}"

        time.sleep(OPERATE_INTERVAL)

def test4(stop_event: ThreadingEvent) -> None:
    global share_state
    with share_state["lock"]:
        share_state["func_status"]["点击再次派遣"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "开始循环识别再次派遣按钮"
        }

    while not stop_event.is_set():
        game_window = get_game_window()
        if not game_window:
            with share_state["lock"]:
                share_state["func_status"]["点击再次派遣"]["detail"] = "未找到崩坏：星穹铁道窗口"
            time.sleep(OPERATE_INTERVAL)
            continue
        
        assign_again_pos = None
        try:
            config = IMAGE_CONFIGS["assign_again"]
            region = (game_window.left, game_window.top, game_window.width, game_window.height)
            assign_again_pos = cv2_template_match(config["path"], config["confidence"], region)
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["点击再次派遣"]["detail"] = f"识别异常：{str(e)[:50]}"
            time.sleep(OPERATE_INTERVAL)
            continue
        
        if assign_again_pos:
            assign_again_center = (assign_again_pos[0] + assign_again_pos[2]//2, assign_again_pos[1] + assign_again_pos[3]//2)
            pyautogui.click(assign_again_center[0], assign_again_center[1])
            with share_state["lock"]:
                share_state["func_status"]["点击再次派遣"]["last_operate"] = f"点击再次派遣按钮 ({assign_again_center[0]}, {assign_again_center[1]})"
                share_state["func_status"]["点击再次派遣"]["detail"] = "已识别并点击再次派遣按钮"
            time.sleep(OPERATE_INTERVAL)
        else:
            with share_state["lock"]:
                share_state["func_status"]["点击再次派遣"]["detail"] = "未识别到再次派遣按钮"
            time.sleep(OPERATE_INTERVAL)
    
    with share_state["lock"]:
        share_state["func_status"]["点击再次派遣"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "再次派遣功能已终止"
        }

def test5(stop_event: ThreadingEvent) -> None:
    global share_state
    with share_state["lock"]:
        share_state["func_status"]["确认退出游戏"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "开始循环识别确认退出按钮"
        }

    while not stop_event.is_set():
        game_window = get_game_window()
        if not game_window:
            with share_state["lock"]:
                share_state["func_status"]["确认退出游戏"]["detail"] = "未找到崩坏：星穹铁道窗口"
            time.sleep(OPERATE_INTERVAL)
            continue
        
        quit_ok_pos = None
        try:
            config = IMAGE_CONFIGS["quit_ok"]
            region = (game_window.left, game_window.top, game_window.width, game_window.height)
            quit_ok_pos = cv2_template_match(config["path"], config["confidence"], region)
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["确认退出游戏"]["detail"] = f"识别异常：{str(e)[:50]}"
            time.sleep(OPERATE_INTERVAL)
            continue
        
        if quit_ok_pos:
            quit_ok_center = (quit_ok_pos[0] + quit_ok_pos[2]//2, quit_ok_pos[1] + quit_ok_pos[3]//2)
            pyautogui.click(quit_ok_center[0], quit_ok_center[1])
            with share_state["lock"]:
                share_state["func_status"]["确认退出游戏"]["last_operate"] = f"点击确认退出按钮 ({quit_ok_center[0]}, {quit_ok_center[1]})"
                share_state["func_status"]["确认退出游戏"]["detail"] = "已识别并点击确认退出按钮"
            time.sleep(OPERATE_INTERVAL)
        else:
            with share_state["lock"]:
                share_state["func_status"]["确认退出游戏"]["detail"] = "未识别到确认退出按钮"
            time.sleep(OPERATE_INTERVAL)
    
    with share_state["lock"]:
        share_state["func_status"]["确认退出游戏"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "确认退出游戏功能已终止"
        }

def test6(stop_event: ThreadingEvent) -> None:
    global share_state
    with share_state["lock"]:
        share_state["func_status"]["点击确认按钮"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "开始循环识别全局确认按钮"
        }

    while not stop_event.is_set():
        confirm_pos = None
        try:
            config = IMAGE_CONFIGS["confirm"]
            confirm_pos = cv2_template_match(config["path"], config["confidence"])
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["点击确认按钮"]["detail"] = f"识别异常：{str(e)[:50]}"
            time.sleep(OPERATE_INTERVAL)
            continue
        
        if confirm_pos:
            confirm_center = (confirm_pos[0] + confirm_pos[2]//2, confirm_pos[1] + confirm_pos[3]//2)
            pyautogui.click(confirm_center[0], confirm_center[1])
            with share_state["lock"]:
                share_state["func_status"]["点击确认按钮"]["last_operate"] = f"点击全局确认按钮 ({confirm_center[0]}, {confirm_center[1]})"
                share_state["func_status"]["点击确认按钮"]["detail"] = "已识别并点击全局确认按钮"
            time.sleep(OPERATE_INTERVAL)
        else:
            with share_state["lock"]:
                share_state["func_status"]["点击确认按钮"]["detail"] = "未识别到全局确认按钮"
            time.sleep(OPERATE_INTERVAL)
    
    with share_state["lock"]:
        share_state["func_status"]["点击确认按钮"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "全局确认按钮功能已终止"
        }

def test7(stop_event: ThreadingEvent) -> None:
    global share_state
    with share_state["lock"]:
        share_state["func_status"]["点击再来一次"] = {
            "running": True,
            "last_operate": "功能启动",
            "detail": "开始循环识别再来一次按钮"
        }

    while not stop_event.is_set():
        once_again_pos = None
        try:
            config = IMAGE_CONFIGS["once_again"]
            once_again_pos = cv2_template_match(config["path"], config["confidence"])
        except Exception as e:
            with share_state["lock"]:
                share_state["func_status"]["点击再来一次"]["detail"] = f"识别异常：{str(e)[:50]}"
            time.sleep(OPERATE_INTERVAL)
            continue
        
        if once_again_pos:
            once_again_center = (once_again_pos[0] + once_again_pos[2]//2, once_again_pos[1] + once_again_pos[3]//2)
            pyautogui.click(once_again_center[0], once_again_center[1])
            with share_state["lock"]:
                share_state["func_status"]["点击再来一次"]["last_operate"] = f"点击再来一次按钮 ({once_again_center[0]}, {once_again_center[1]})"
                share_state["func_status"]["点击再来一次"]["detail"] = "已识别并点击再来一次按钮"
            time.sleep(OPERATE_INTERVAL)
        else:
            with share_state["lock"]:
                share_state["func_status"]["点击再来一次"]["detail"] = "未识别到再来一次按钮"
            time.sleep(OPERATE_INTERVAL)
    
    with share_state["lock"]:
        share_state["func_status"]["点击再来一次"] = {
            "running": False,
            "last_operate": "功能停止",
            "detail": "再来一次按钮功能已终止"
        }

class HotkeyManager:
    def __init__(self, share_state: Dict[str, Any]) -> None:
        self.func_states: Dict[str, Dict[str, Any]] = {}
        self.exit_flag: bool = False
        self.share_state = share_state
        self._register_functions()
        self._start_default_running_functions()
        self._start_console_refresh_thread()

    def _register_functions(self) -> None:
        self.functions: Dict[str, Dict[str, Any]] = { # "代号": {"hotkey": "快捷键", "type": "类型（TOGGLE 或 ONCE）", "func": "(主)函数名称", "running": "是否默认启动"}
            "跳过剧情": {"hotkey": "U", "type": "TOGGLE", "func": test1, "running": False},
            "跳过获得物品界面": {"hotkey": "I", "type": "TOGGLE", "func": test2, "running": False},
            "点击进入游戏": {"hotkey": "O", "type": "TOGGLE", "func": test3, "running": True},
            "点击再次派遣": {"hotkey": "P", "type": "TOGGLE", "func": test4, "running": True},
            "确认退出游戏": {"hotkey": "H", "type": "TOGGLE", "func": test5, "running": True},
            "点击确认按钮": {"hotkey": "K", "type": "TOGGLE", "func": test6, "running": False},
            "点击再来一次": {"hotkey": "L", "type": "TOGGLE", "func": test7, "running": False}
        }

        for func_name, config in self.functions.items():
            keyboard.add_hotkey(
                config["hotkey"],
                lambda fn=func_name: self._handle_hotkey(fn),
                suppress=False,
                timeout=0
            )

        keyboard.add_hotkey('z+x', self.stop_all_toggle, suppress=False, timeout=0) # 关闭全部功能
        keyboard.add_hotkey('f8', self.set_exit_flag, suppress=False, timeout=0) # 退出程序

    def _start_default_running_functions(self) -> None:
        for func_name, config in self.functions.items():
            if config.get("running", False):
                self._toggle_function(func_name, config["func"])

    def _start_console_refresh_thread(self) -> None:
        def refresh_console():
            while not self.exit_flag:
                clear_console()
                self._print_console_summary()
                time.sleep(CONSOLE_REFRESH_INTERVAL)
        
        console_thread = threading.Thread(target=refresh_console, daemon=True)
        console_thread.start()

    def _print_console_summary(self) -> None:
        print("="*55)
        print("快捷键说明：Z+X 关闭全部功能 | F8 退出程序")
        print("="*55)
        print("功能状态列表：")
        print("-"*55)
        
        with self.share_state["lock"]:
            func_status = self.share_state["func_status"]
        
        for func_name in self.functions.keys():
            status = func_status.get(func_name, {"running": False, "last_operate": "未启动", "detail": "无"})
            status_icon = "✅" if status["running"] else "❌"
            hotkey = self.functions[func_name]["hotkey"]
            
            print(f"{status_icon} {func_name} [ {hotkey} ]")
            print(f"  最后操作：{status['last_operate']}")
            print(f"  详细信息：{status['detail']}")
            print("-"*55)

    def _handle_hotkey(self, func_name: str) -> None:
        config = self.functions[func_name]
        func_type = config["type"]
        func = config["func"]

        if func_type == "ONCE":
            with self.share_state["lock"]:
                self.share_state["func_status"][func_name]["last_operate"] = "单次执行触发"
            func()
        elif func_type == "TOGGLE":
            self._toggle_function(func_name, func)

    def _toggle_function(self, func_name: str, func: Callable[..., None]) -> None:
        current_state: Optional[Dict[str, Any]] = self.func_states.get(func_name, {})
        
        if not current_state.get("is_running", False):
            stop_event: ThreadingEvent = threading.Event()
            if func_name in ["跳过剧情", "跳过获得物品界面", "点击进入游戏"]:
                thread = threading.Thread(
                    target=func,
                    args=(stop_event, self.share_state),
                    daemon=True
                )
            else:
                thread = threading.Thread(
                    target=func,
                    args=(stop_event,),
                    daemon=True
                )
            thread.start()
            self.func_states[func_name] = {
                "thread": thread,
                "stop_event": stop_event,
                "is_running": True
            }
            with self.share_state["lock"]:
                self.share_state["func_status"][func_name]["running"] = True
                self.share_state["func_status"][func_name]["last_operate"] = "手动启动功能"
        
        else:
            stop_event = current_state["stop_event"]
            stop_event.set()
            self.func_states[func_name] = {"is_running": False}
            with self.share_state["lock"]:
                self.share_state["func_status"][func_name]["running"] = False
                self.share_state["func_status"][func_name]["last_operate"] = "手动停止功能"

    def stop_all_toggle(self) -> None:
        stopped_num = 0
        for func_name, config in self.functions.items():
            if config["type"] == "TOGGLE":
                state = self.func_states.get(func_name, {})
                if state.get("is_running"):
                    state["stop_event"].set()
                    self.func_states[func_name] = {"is_running": False}
                    with self.share_state["lock"]:
                        self.share_state["func_status"][func_name]["running"] = False
                        self.share_state["func_status"][func_name]["last_operate"] = "一键关闭功能"
                    stopped_num += 1

    def stop_all(self) -> None:
        for func_name, state in self.func_states.items():
            if state.get("is_running"):
                state["stop_event"].set()
                self.func_states[func_name] = {"is_running": False}
                with self.share_state["lock"]:
                    self.share_state["func_status"][func_name]["running"] = False
                    self.share_state["func_status"][func_name]["last_operate"] = "全局退出-停止功能"

    def set_exit_flag(self) -> None:
        self.exit_flag = True
        with self.share_state["lock"]:
            for func_name in self.functions.keys():
                self.share_state["func_status"][func_name]["last_operate"] = "程序即将退出"

if __name__ == "__main__":
    share_state = {
        "lock": threading.Lock(),
        "window_ready": False,
        "skip_btn_x": 0,
        "skip_btn_y": 0,
        "sound_found": False,
        "give_item_target_x": 0,
        "give_item_target_y": 0,
        "give_item_found": False,
        "enter_game_center_x": 0,
        "enter_game_center_y": 0,
        "enter_game_found": False,
        "func_status": {
            "跳过剧情": {"running": False, "last_operate": "未启动", "detail": "无"},
            "跳过获得物品界面": {"running": False, "last_operate": "未启动", "detail": "无"},
            "点击进入游戏": {"running": False, "last_operate": "未启动", "detail": "无"},
            "点击再次派遣": {"running": False, "last_operate": "未启动", "detail": "无"},
            "确认退出游戏": {"running": False, "last_operate": "未启动", "detail": "无"},
            "点击确认按钮": {"running": False, "last_operate": "未启动", "detail": "无"},
            "点击再来一次": {"running": False, "last_operate": "未启动", "detail": "无"}
        }
    }

    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.005
    
    manager = HotkeyManager(share_state)
    
    try:
        while True:
            if manager.exit_flag:
                manager.stop_all()
                keyboard.unhook_all()
                clear_console()
                print("程序已安全退出！")
                sys.exit(0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        manager.stop_all()     
        keyboard.unhook_all()
        clear_console()
        print("程序已安全退出！")

        sys.exit(0)

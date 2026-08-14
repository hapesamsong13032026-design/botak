#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     HEARTWOOD MINING BOT - COMPLETE v1.1                      ║
║                                                                               ║
║  A comprehensive Python-based object detection bot for Heartwood Online       ║
║  Mining automation using OpenCV template matching and keyboard simulation     ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Author: VrtK
Version: 1.1
Python: 3.6+
OS: Windows (requires ctypes.windll)

Dependencies:
  - opencv-python (cv2)
  - pyautogui
  - pygetwindow
  - numpy
  - requests
  - tkinter (built-in)

Usage:
  python bot_complete.py

Features:
  ✓ Automatic coal mining detection
  ✓ Multi-ore variant support (11 types)
  ✓ Smart character navigation (WASD)
  ✓ Bank management (store/pull)
  ✓ NPC trading automation
  ✓ Connection/death detection
  ✓ Telegram notifications
  ✓ Live game preview
  ✓ Tkinter GUI with controls
  ✓ Timestamped console logging
"""

import os
import sys
import cv2
import glob
import time
import ctypes
import requests
import datetime
import pyautogui
import threading
import numpy as np
import tkinter as tk
from datetime import datetime
from tkinter import PhotoImage

# ═════════════════════════════════════════════════════════════════════════════
# GLOBAL CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

global Lilian  # Bot active flag
full_counter = 0  # Bag fullness counter (max 6)
lifted_coal = 0  # Total coal mined counter

# Window configuration
WINDOW_TITLE = 'BlueStacks App Player'
EMULATOR_RESOLUTION = (1600, 900)

# Template paths
MINING_TEMPLATE = 'MISC/mining/Capture.JPG'
MAIN_SPOT_TEMPLATE = 'MISC/mining/main.JPG'
DIED_TEMPLATE = 'MISC/game/died.JPG'
TOWN_TEMPLATE = 'MISC/game/town.JPG'
NEW_MESSAGE_TEMPLATE = 'MISC/game/new_message.JPG'
COAL_ONGROUND_TEMPLATE = 'MISC/mining/storage/coal_onground.JPG'

# Template matching thresholds
THRESHOLD_MINING_ACTION = 0.85
THRESHOLD_ORE_DETECTION = 0.7
THRESHOLD_MAIN_OBJECT = 0.7
THRESHOLD_MISC = 0.5
THRESHOLD_TOWN = 0.8

# Movement & distance config
MAX_DISTANCE_TO_ORE = 650
BAG_FULL_THRESHOLD = 6
MOVEMENT_DELAY = 0.3  # seconds per key press
SPECIAL_DISTANCE = 161

# ═════════════════════════════════════════════════════════════════════════════
# KEYBOARD INPUT HANDLER - Virtual Key Codes
# ═════════════════════════════════════════════════════════════════════════════

# Key codes (scan codes for Windows)
W = 0x11  # Forward
A = 0x1E  # Left
S = 0x1F  # Backward
D = 0x20  # Right
Z = 0x2C  # Unknown
X = 0x2D  # Unknown
Q = 0x10  # Skill
E = 0x12  # Action/Interact
UP = 0xC8  # Arrow Up
DOWN = 0xD0  # Arrow Down
LEFT = 0xCB  # Arrow Left
RIGHT = 0xCD  # Arrow Right
ENTER = 0x1C  # Enter key
SPACE = 0x39  # Space (attack)

# Input structures for Windows API
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    """Keyboard input structure for Windows API"""
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    """Hardware input structure for Windows API"""
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    """Mouse input structure for Windows API"""
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    """Input union combining all input types"""
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    """Combined input structure"""
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


# ═════════════════════════════════════════════════════════════════════════════
# KEYBOARD INPUT FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def PressKey(hexKeyCode):
    """
    Press a keyboard key using Windows API
    
    Args:
        hexKeyCode: Virtual key code (hex)
    """
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    """
    Release a keyboard key using Windows API
    
    Args:
        hexKeyCode: Virtual key code (hex)
    """
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


# ═════════════════════════════════════════════════════════════════════════════
# MOVEMENT FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def move_left():
    """Move character left (A key)"""
    print('↶ Moving left')
    PressKey(A)
    time.sleep(MOVEMENT_DELAY)
    ReleaseKey(A)


def move_right():
    """Move character right (D key)"""
    print('↷ Moving right')
    PressKey(D)
    time.sleep(MOVEMENT_DELAY)
    ReleaseKey(D)


def move_up():
    """Move character up (W key)"""
    print('↑ Moving up')
    PressKey(W)
    time.sleep(MOVEMENT_DELAY)
    ReleaseKey(W)


def move_down():
    """Move character down (S key)"""
    print('↓ Moving down')
    PressKey(S)
    time.sleep(MOVEMENT_DELAY)
    ReleaseKey(S)


def attack():
    """Attack/interact (SPACE key)"""
    print('⚡ Attack')
    PressKey(SPACE)
    time.sleep(MOVEMENT_DELAY)
    ReleaseKey(SPACE)


def action():
    """Perform action/interact (E key)"""
    print('🔨 Action')
    PressKey(E)
    time.sleep(MOVEMENT_DELAY)
    ReleaseKey(E)


def drag_and_drop(start_x, start_y, end_x, end_y):
    """
    Perform drag and drop action
    
    Args:
        start_x, start_y: Starting position
        end_x, end_y: Ending position
    """
    pyautogui.moveTo(start_x, start_y)
    pyautogui.mouseDown()
    pyautogui.moveTo(end_x, end_y)
    pyautogui.mouseUp()


# ═════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def wait_for_window():
    """Wait for game window to become active"""
    while True:
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            if active_window and active_window.title == WINDOW_TITLE:
                return True
        except:
            pass
        time.sleep(0.5)


def calculate_distance(obj1, obj2):
    """
    Calculate euclidean distance between two points
    
    Args:
        obj1: (x1, y1) tuple
        obj2: (x2, y2) tuple
    
    Returns:
        float: Distance in pixels
    """
    x1, y1 = obj1
    x2, y2 = obj2
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance


def move_character_towards_object(character_x, character_y, object_center_x, 
                                   object_center_y, distance):
    """
    Move character towards detected object
    
    Uses euclidean distance to determine movement direction
    
    Args:
        character_x, character_y: Current character position (center)
        object_center_x, object_center_y: Target object center
        distance: Calculated distance in pixels
    """
    print(f'🎯 Moving to object at ({object_center_x}, {object_center_y})')
    
    distance_x = object_center_x - character_x
    distance_y = object_center_y - character_y
    
    # Special handling for specific distance
    if int(distance) == SPECIAL_DISTANCE:
        move_up()
    
    # Horizontal movement
    if distance_x > 10:
        move_right()
    elif distance_x < -10:
        move_left()
    
    # Vertical movement
    if distance_y > 10:
        move_down()
    elif distance_y < -10:
        move_up()


# ═════════════════════════════════════════════════════════════════════════════
# OBJECT DETECTION FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def find_object_in_game(window_title, obj_path):
    """
    Find object in game using template matching
    
    Args:
        window_title: Window title to search in
        obj_path: Path to template image
    
    Returns:
        tuple: (x, y, confidence) - coordinates and match confidence
    """
    import pygetwindow as gw
    
    try:
        target_window = gw.getWindowsWithTitle(window_title)[0]
        screenshot = pyautogui.screenshot(
            region=(target_window.left, target_window.top, 
                   target_window.width, target_window.height))
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        template = cv2.imread(obj_path)
        if template is None:
            print(f"⚠️  Template not found: {obj_path}")
            return 0, 0, 0.0
        
        results = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        result_min_val, result_max_val, result_min_loc, result_max_loc = cv2.minMaxLoc(results)
        
        x, y = result_max_loc
        x += target_window.left
        y += target_window.top
        
        return x, y, result_max_val
    except Exception as e:
        print(f"❌ Error finding object: {e}")
        return 0, 0, 0.0


# ═════════════════════════════════════════════════════════════════════════════
# MINING CORE FUNCTION - MAIN BOT LOOP
# ═════════════════════════════════════════════════════════════════════════════

def create_live_duplicate(window_title):
    """
    MAIN BOT LOOP
    
    Runs in separate thread. Continuously:
    1. Screenshots game
    2. Detects mining actions
    3. Scans for ore
    4. Calculates distance
    5. Navigates to ore
    6. Checks for errors (died, disconnected)
    7. Updates GUI preview
    
    Args:
        window_title: Target window title
    """
    global Lilian, lifted_coal
    import pygetwindow as gw
    
    try:
        # Get window info
        target_window = gw.getWindowsWithTitle(window_title)[0]
        character_x = target_window.width // 2  # Center X
        character_y = target_window.height // 2  # Center Y
        
        print(f"🎮 Window found: {window_title}")
        print(f"📏 Resolution: {target_window.width}x{target_window.height}")
        print(f"👤 Character position: ({character_x}, {character_y})")
        
        # Wait for window to be active
        while not target_window.isActive:
            time.sleep(0.5)
        
        print("✅ Bot started! Begin mining...")
        
        # INFINITE LOOP
        iteration = 0
        while True:
            iteration += 1
            
            if not Lilian:
                print("🛑 Bot stopped")
                break
            
            # Ensure window is active
            while not target_window.isActive:
                time.sleep(0.5)
            
            # ╔════════════════════════════════════════════╗
            # ║ STEP 1: Screenshot Game                  ║
            # ╚════════════════════════════════════════════╝
            try:
                screenshot = pyautogui.screenshot(
                    region=(target_window.left, target_window.top, 
                           target_window.width, target_window.height))
                screenshot = np.array(screenshot)
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"❌ Screenshot error: {e}")
                continue
            
            # ╔════════════════════════════════════════════╗
            # ║ STEP 2: Detect Mining Action            ║
            # ╚════════════════════════════════════════════╝
            try:
                mining_template_read = cv2.imread(MINING_TEMPLATE)
                if mining_template_read is not None:
                    obj_mining = cv2.matchTemplate(screenshot, mining_template_read, 
                                                   cv2.TM_CCOEFF_NORMED)
                    mining_min_val, mining_max_val, mining_min_loc, mining_max_loc = cv2.minMaxLoc(obj_mining)
                    
                    if mining_max_val > THRESHOLD_MINING_ACTION:
                        print(f"⛏️  Found mining action! Confidence: {mining_max_val:.4f}")
                        action()
                        lifted_coal += 1
                        label_lifted_coal.config(text=f'⛏️ Found Coal\n{lifted_coal}')
                        time.sleep(5)  # Wait for mining animation
                        continue
            except Exception as e:
                print(f"⚠️  Mining detection error: {e}")
            
            # ╔════════════════════════════════════════════╗
            # ║ STEP 3: Scan Ore Templates               ║
            # ╚════════════════════════════════════════════╝
            ore_found = False
            folder_path = 'MISC/mining/ore'
            
            try:
                image_paths = (glob.glob(os.path.join(folder_path, '*.jpg')) + 
                              glob.glob(os.path.join(folder_path, '*.png')))
                
                for image_path in image_paths:
                    try:
                        template = cv2.imread(image_path)
                        if template is None:
                            continue
                        
                        obj_result = cv2.matchTemplate(screenshot, template, 
                                                       cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(obj_result)
                        
                        if max_val > THRESHOLD_ORE_DETECTION:
                            print(f"🪨 Found Ore! Type: {os.path.basename(image_path)}, "
                                  f"Confidence: {max_val:.4f}")
                            
                            # Calculate ore center
                            template_width, template_height = template.shape[1], template.shape[0]
                            top_left = max_loc
                            bottom_right = (top_left[0] + template_width, 
                                          top_left[1] + template_height)
                            
                            # Draw rectangle (for debug)
                            cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)
                            
                            # Calculate centroid
                            ore_object_centroid = (top_left[0] + template_width // 2,
                                                  top_left[1] + template_height // 2)
                            object_center_x = top_left[0] + (template_width // 2)
                            object_center_y = top_left[1] + (template_height // 2)
                            
                            # ╔════════════════════════════════════════════╗
                            # ║ STEP 4: Validate Main Spot & Distance    ║
                            # ╚════════════════════════════════════════════╝
                            try:
                                main_template = cv2.imread(MAIN_SPOT_TEMPLATE)
                                if main_template is not None:
                                    result = cv2.matchTemplate(screenshot, main_template, 
                                                              cv2.TM_CCOEFF_NORMED)
                                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                                    top_left_main = max_loc
                                    main_object_centroid = (top_left_main[0] + main_template.shape[1] // 2,
                                                           top_left_main[1] + main_template.shape[0] // 2)
                                    
                                    if max_val > THRESHOLD_MAIN_OBJECT:
                                        distance = calculate_distance(main_object_centroid, 
                                                                     ore_object_centroid)
                                        
                                        if distance > MAX_DISTANCE_TO_ORE:
                                            print(f"📏 Ore too far! Distance: {distance:.2f}px "
                                                  f"(max: {MAX_DISTANCE_TO_ORE}px)")
                                            continue
                                        else:
                                            print(f"📏 Distance: {distance:.2f}px - ACCEPTABLE")
                                            # ╔════════════════════════════════════════════╗
                                            # ║ STEP 5: Move & Mine                     ║
                                            # ╚════════════════════════════════════════════╝
                                            move_character_towards_object(
                                                character_x, character_y,
                                                object_center_x, object_center_y,
                                                distance)
                                            ore_found = True
                                    else:
                                        print("❓ Cannot locate main mining spot")
                                        move_down()
                            except Exception as e:
                                print(f"⚠️  Main spot detection error: {e}")
                            
                            break  # Process only first ore found
                    
                    except Exception as e:
                        print(f"⚠️  Ore processing error: {e}")
                        continue
            
            except Exception as e:
                print(f"❌ Ore scanning error: {e}")
            
            # ╔════════════════════════════════════════════╗
            # ║ STEP 6: Check Misc Conditions           ║
            # ╚════════════════════════════════════════════╝
            check_for_misc()
            
            # ╔════���═══════════════════════════════════════╗
            # ║ STEP 7: Update GUI Preview               ║
            # ╚════════════════════════════════════════════╝
            try:
                display_image(screenshot)
            except Exception as e:
                print(f"⚠️  Display error: {e}")
            
            # Frame rate limiter (≈1-2 FPS)
            time.sleep(0.5)
    
    except Exception as e:
        print(f"❌ FATAL BOT ERROR: {e}")
        stop_function()


# ═════════════════════════════════════════════════════════════════════════════
# CONDITION CHECKING FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def check_for_misc():
    """
    Check for error conditions:
    1. Connection lost (4 variants)
    2. Character died
    3. Bag full
    """
    global full_counter, lifted_coal, Lilian
    
    try:
        # ╔════════════════════════════════════════════╗
        # ║ Check: Connection Lost                   ║
        # ╚════════════════════════════════════════════╝
        folder_path = 'MISC/game/lost_connection'
        for image_path in glob.glob(os.path.join(folder_path, '*.jpg')):
            try:
                _, _, val = find_object_in_game(WINDOW_TITLE, image_path)
                if val > THRESHOLD_MISC:
                    print(f"🔴 CONNECTION LOST detected! ({os.path.basename(image_path)})")
                    telegram('❌ CONNECTION LOST')
                    stop_function()
                    return
            except:
                continue
        
        # ╔════════════════════════════════════════════╗
        # ║ Check: Character Died                    ║
        # ╚════════════════════════════════════════════╝
        try:
            _, _, val = find_object_in_game(WINDOW_TITLE, DIED_TEMPLATE)
            if val > THRESHOLD_MISC:
                print("💀 CHARACTER DIED!")
                telegram(f'💀 DIED! Coal mined: {lifted_coal}')
                stop_function()
                return
        except:
            pass
        
        # ╔════════════════════════════════════════════╗
        # ║ Check: Bag Full                          ║
        # ╚════════════════════════════════════════════╝
        try:
            _, _, val = find_object_in_game(WINDOW_TITLE, COAL_ONGROUND_TEMPLATE)
            if val > THRESHOLD_MISC:
                print("🏷️  Coal found on ground - Bag might be full!")
                full_counter += 1
                action()  # Try collect
                
                if full_counter >= BAG_FULL_THRESHOLD:
                    print("🎉 BAG FULL!")
                    telegram(f'🎉 BAG FULL! Coal mined: {lifted_coal}')
                    full_counter = 0
                    lifted_coal = 0
                    
                    # Go to town, bank, and return
                    Lilian = False
                    print("🏘️  Going to town...")
                    town_function(bank=True)
                    print("🔙 Returning to spot...")
                    back_to_spot_function()
                    Lilian = True
                    print("✅ Ready to mine again!")
        except:
            pass
    
    except Exception as e:
        print(f"⚠️  Misc check error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# BANKING & TRADING FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def store_function():
    """Store coal from inventory to bank"""
    wait_for_window()
    print("💾 Starting store coal...")
    
    try:
        # First create empty slot
        x, y, coal_val = find_object_in_game(WINDOW_TITLE, 
                                             'MISC/mining/storage/coal.JPG')
        if coal_val > 0.6:
            x_empty, y_empty, _ = find_object_in_game(WINDOW_TITLE, 
                                                      'MISC/mining/storage/empty.JPG')
            drag_and_drop(x + 25, y + 25, x_empty + 25, y_empty + 25)
            
            x_coal = 1030
            counter = 0
            
            for itemx in range(6):
                print(f"📦 Store item #{itemx}")
                x_coal += 70
                y_coal = 230
                
                for itemy in range(6):
                    y_coal += 70
                    drag_and_drop(x_coal, y_coal, x_empty + 25, y_empty + 55)
                    time.sleep(0.2)
                    counter += 1
                    
                    if counter == 20:
                        x, y, _ = find_object_in_game(WINDOW_TITLE, 
                                                     'MISC/mining/storage/coal.JPG')
                        x_empty, y_empty, _ = find_object_in_game(WINDOW_TITLE, 
                                                                  'MISC/mining/storage/empty.JPG')
                        drag_and_drop(x, y, x_empty + 25, y_empty + 25)
                        time.sleep(0.2)
        
        print("✅ Store coal completed")
    except Exception as e:
        print(f"❌ Store error: {e}")


def pull_function():
    """Pull coal from bank to inventory"""
    wait_for_window()
    print("📥 Pulling coal from bank...")
    
    try:
        x_coal = 1030
        for itemx in range(6):
            print(f"📦 Pull item #{itemx}")
            x_coal += 70
            y_coal = 230
            
            for itemy in range(6):
                x, y, _ = find_object_in_game(WINDOW_TITLE, 
                                             'MISC/mining/storage/coal_in_bank.JPG')
                y_coal += 70
                drag_and_drop(x + 25, y + 25, x_coal, y_coal)
                time.sleep(0.2)
        
        print("✅ Pull coal completed")
    except Exception as e:
        print(f"❌ Pull error: {e}")


def trade_function():
    """Trade/sell coal to NPC"""
    wait_for_window()
    print("💰 Trading coal...")
    
    try:
        x_empty, y_empty, val_trade = find_object_in_game(WINDOW_TITLE, 
                                                          'MISC/mining/storage/trade_title.JPG')
        for item in range(6):
            x, y, coal_max_val = find_object_in_game(WINDOW_TITLE, 
                                                    'MISC/mining/storage/coal.JPG')
            if coal_max_val > 0.9:
                y_empty += 70
                drag_and_drop(x + 25, y + 25, x_empty, y_empty)
                time.sleep(0.2)
        
        print("✅ Trade completed")
    except Exception as e:
        print(f"❌ Trade error: {e}")


def shout_function():
    """Advertise coal in global chat"""
    wait_for_window()
    print("📢 Shouting...")
    
    try:
        shout_text = '⛏️ SELL COAL 4g - PM ME ⛏️ SELL COAL 4g - PM ME ⛏️'
        val_msg = 0
        
        while val_msg < 0.5:
            time.sleep(3)
            move_up()
            print('📣 Shouting!')
            
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.write(shout_text, interval=0.05)
            time.sleep(0.5)
            pyautogui.press('enter')
            move_down()
            
            _, _, val_msg = find_object_in_game(WINDOW_TITLE, NEW_MESSAGE_TEMPLATE)
            if val_msg > 0.8:
                print("✅ BUYER FOUND!")
                telegram('🎉 FOUND BUYER!')
                break
    
    except Exception as e:
        print(f"❌ Shout error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# NAVIGATION FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

def town_function(bank=True):
    """Navigate to town and optionally use bank"""
    wait_for_window()
    print("🏘️  Going to town...")
    
    try:
        x, y, val_town = find_object_in_game(WINDOW_TITLE, TOWN_TEMPLATE)
        if val_town > THRESHOLD_TOWN:
            print(f"🌍 Found town portal at ({x}, {y})")
            pyautogui.click(x, y)
        
        time.sleep(3)
        
        # Navigate in town
        for _ in range(2):
            move_up()
            move_right()
        
        for _ in range(11):
            move_right()
        
        for _ in range(10):
            move_up()
        
        if bank:
            print("🏦 Opening bank...")
            action()
            time.sleep(2.5)
            store_function()
            time.sleep(1)
            pyautogui.press('esc')
            time.sleep(1)
        
        print("✅ Town navigation completed")
    
    except Exception as e:
        print(f"❌ Town error: {e}")


def back_to_spot_function():
    """Navigate back to mining spot"""
    print("🔙 Returning to mining spot...")
    
    try:
        for _ in range(13):
            move_down()
        
        for _ in range(23):
            move_left()
        
        for _ in range(20):
            move_down()
        
        print("✅ Returned to mining spot")
    
    except Exception as e:
        print(f"❌ Navigation error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# GUI FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════════

class RedirectText:
    """Redirect stdout to Tkinter Text widget with timestamps"""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
    
    def write(self, string):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        lines = string.split('\n')
        
        for line in lines:
            if line:
                self.text_widget.insert(tk.END, timestamp + ' ' + line + '\n')
        
        self.text_widget.see(tk.END)  # Auto-scroll
    
    def flush(self):
        pass


def display_image(screenshot):
    """Update GUI with game screenshot preview"""
    try:
        if screenshot is None:
            return
        
        height, width, _ = screenshot.shape
        aspect_ratio = width / height
        new_width = min(300, width)
        new_height = min(200, int(new_width / aspect_ratio))
        
        resized_image = cv2.resize(screenshot, (new_width, new_height))
        
        # Convert to PPM format for Tkinter
        ret, buffer = cv2.imencode('.ppm', resized_image)
        screenshot_tk = PhotoImage(data=buffer.tobytes())
        
        image_label.config(image=screenshot_tk)
        image_label.image = screenshot_tk
    
    except Exception as e:
        print(f"⚠️  Image display error: {e}")


def start_function():
    """Start bot - called by START button"""
    global Lilian
    print("▶️  STARTING BOT")
    Lilian = True
    print(f'Bot active: {Lilian}')
    
    threading.Thread(target=create_live_duplicate, args=(WINDOW_TITLE,), daemon=True).start()
    
    start_button["state"] = "disabled"
    stop_button["state"] = "normal"


def stop_function():
    """Stop bot - called by STOP button or error condition"""
    global Lilian
    print("⏹️  STOPPING BOT")
    Lilian = False
    print(f'Bot active: {Lilian}')
    
    start_button["state"] = "normal"
    stop_button["state"] = "disabled"


def telegram(message):
    """
    Send Telegram notification
    
    ⚠️  WARNING: Credentials are exposed in this file!
        Move to environment variables or config file
    
    Args:
        message: Message to send
    """
    try:
        # TODO: Move credentials to environment variables
        chat_id = "156666562"
        token = "8460404196:AAFqcxbkcmn-SaHSNOZ8RxpvwyGI_7bGvhY"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message
        }
        
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            print(f"📱 Telegram sent: {message}")
        else:
            print(f"❌ Telegram failed: {response.status_code}")
    
    except Exception as e:
        print(f"⚠️  Telegram error: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN GUI INITIALIZATION
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    Lilian = False
    
    # ╔════════════════════════════════════════════╗
    # ║ Create Tkinter Window                    ║
    # ╚══════════════════════════════════���═════════╝
    root = tk.Tk()
    root.title("🎮 Heartwood Mining Bot v1.1")
    root.geometry("305x600+0+0")
    root.attributes("-topmost", True)
    root.wm_attributes('-toolwindow', 1)
    root.configure(bg='#2b2b2b')
    
    # ╔════════════════════════════════════════════╗
    # ║ Create Console Output Widget             ║
    # ╚════════════════════════════════════════════╝
    console_output = tk.Text(root, wrap=tk.WORD, height=14, width=35, 
                             bg='#1e1e1e', fg='#00ff00', font=('Courier', 8))
    console_output.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
    sys.stdout = RedirectText(console_output)
    
    # ╔════════════════════════════════════════════╗
    # ║ Create Control Buttons                   ║
    # ╚════════════════════════════════════════════╝
    start_button = tk.Button(root, text="▶️  START", command=start_function, 
                             fg="white", bg="#00aa00", font=('Arial', 10, 'bold'))
    start_button.grid(row=0, column=0, padx=5, pady=5)
    
    stop_button = tk.Button(root, text="⏹️  STOP", command=stop_function, 
                            fg="white", bg="#aa0000", font=('Arial', 10, 'bold'))
    stop_button.grid(row=0, column=1, padx=5, pady=5)
    
    # ╔════════════════════════════════════════════╗
    # ║ Create Action Buttons                    ║
    # ╚════════════════════════════════════════════╝
    store_button = tk.Button(root, text="💾 Store", command=store_function, 
                             font=('Arial', 8))
    store_button.grid(row=3, column=0, padx=2, pady=2)
    
    pull_button = tk.Button(root, text="📥 Pull", command=pull_function, 
                            font=('Arial', 8))
    pull_button.grid(row=3, column=1, padx=2, pady=2)
    
    trade_button = tk.Button(root, text="💰 Trade", command=trade_function, 
                             font=('Arial', 8))
    trade_button.grid(row=3, column=0, columnspan=2, padx=2, pady=2, sticky='ew')
    
    shout_button = tk.Button(root, text="📢 Shout", command=shout_function, 
                             font=('Arial', 8))
    shout_button.grid(row=4, column=0, columnspan=2, padx=2, pady=2, sticky='ew')
    
    town_button = tk.Button(root, text="🏘️  Town", command=town_function, 
                            font=('Arial', 8))
    town_button.grid(row=4, column=1, padx=2, pady=2)
    
    spot_button = tk.Button(root, text="🔙 Back", command=back_to_spot_function, 
                            font=('Arial', 8))
    spot_button.grid(row=4, column=0, padx=2, pady=2)
    
    # ╔════════════════════════════════════════════╗
    # ║ Create Image Preview Label               ║
    # ╚════════════════════════════════════════════╝
    image_label = tk.Label(root, bg='#1e1e1e')
    image_label.grid(row=2, column=0, columnspan=2, padx=0, pady=5)
    
    # ╔════════════════════════════════════════════╗
    # ║ Create Coal Counter Label                ║
    # ╚════════════════════════════════════════════╝
    label_lifted_coal = tk.Label(root, text="⛏️ Coal: 0", fg="#00ff00", bg='#2b2b2b',
                                 font=('Arial', 12, 'bold'))
    label_lifted_coal.grid(row=0, column=0, columnspan=2, padx=0, pady=5)
    
    # ╔════════════════════════════════════════════╗
    # ║ Initial Setup                            ║
    # ╚════════════════════════════════════════════╝
    print('╔════════════════════════════════════════╗')
    print('║  🎮 HEARTWOOD MINING BOT v1.1        ║')
    print('║  Ready to mine!                       ║')
    print('╚════════════════════════════════════════╝')
    print(f'Configuration:')
    print(f'  Window: {WINDOW_TITLE}')
    print(f'  Resolution: {EMULATOR_RESOLUTION}')
    print(f'  Max Distance: {MAX_DISTANCE_TO_ORE}px')
    print(f'  Bag Capacity: {BAG_FULL_THRESHOLD} items')
    print('')
    
    stop_button["state"] = "disabled"
    
    # Start GUI
    root.mainloop()

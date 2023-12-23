# SmartHome.py

from kasa import SmartBulb
import asyncio

# List of bulb IPs
bulb_ips = ['192.168.1.6', '192.168.1.7']

# A mapping of commands to actions
SMART_HOME_ACTIONS = {
    "turn on the light": "on",
    "turn the light on": "on",
    "turn off the light": "off",
    "turn the light off": "off",
    # You can add more commands and actions here
}

async def control_light(action):
    tasks = []
    for bulb_ip in bulb_ips:
        bulb = SmartBulb(bulb_ip)
        await bulb.update()  # Fetch the latest state
        if action == 'on':
            tasks.append(bulb.turn_on())
        elif action == 'off':
            tasks.append(bulb.turn_off())
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

async def process_smart_home_command(command):
    # Check if the "light on" or "light off" keywords are present anywhere in the command
    if "light on" in command:
        action = "on"  # Set action to turn on the light
        await control_light(action)
    elif "light off" in command:
        action = "off"  # Set action to turn off the light
        await control_light(action)
    else:
        for phrase, action in SMART_HOME_ACTIONS.items():
            if phrase in command:
                await control_light(action)
                break  # If a command matches, perform the action and stop checking
        else:
            print("No smart home command found.")

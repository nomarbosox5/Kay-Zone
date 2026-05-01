import time
import threading
import statsapi
from datetime import datetime, timedelta

# --- CONFIG ---
TARGET_DATE = "2026-05-01"  # Set to tomorrow's date
ACTIVE_THREADS = {}  # {game_id: thread}

def monitor_game(game_id, summary):
    print(f"📡 [STARTING] Monitoring: {summary} (ID: {game_id})")
    last_idx = -1
    
    while True:
        try:
            data = statsapi.get('game', {'gamePk': game_id})
            status = data.get('gameData', {}).get('status', {}).get('abstractGameState', '')
            
            if status == 'Final':
                print(f"🏁 [FINISHED] {summary}")
                break
                
            plays = data.get('liveData', {}).get('plays', {}).get('allPlays', [])
            if not plays:
                time.sleep(10)
                continue

            curr_play = plays[-1]
            idx = curr_play.get('atBatIndex')

            if idx != last_idx:
                # Physics extraction logic
                hit_data = curr_play.get('hitData', {})
                velo = hit_data.get('launchSpeed')
                angle = hit_data.get('launchAngle')

                # Deep scan events for real-time physics
                if velo is None:
                    for event in reversed(curr_play.get('playEvents', [])):
                        if 'hitData' in event:
                            velo = event['hitData'].get('launchSpeed')
                            angle = event['hitData'].get('launchAngle')
                            break

                if velo:
                    print(f"📊 {summary} | {velo} mph | {angle}°")
                    # TRIGGER: Velo 98+ and Angle 24-32
                    if velo >= 98 and 24 <= angle <= 32:
                        print(f"🔥 GAP KING TRIGGERED IN {summary}!")
                        # execute_snipe() logic goes here
                
                last_idx = idx
        except:
            pass
        time.sleep(2)

def main_orchestrator():
    print(f"🕵️ Orchestrator Live for {TARGET_DATE}. Checking for games...")
    while True:
        try:
            schedule = statsapi.schedule(date=TARGET_DATE)
            for g in schedule:
                gid = g['game_id']
                if g['status'] == 'In Progress' and gid not in ACTIVE_THREADS:
                    t = threading.Thread(target=monitor_game, args=(gid, g['summary']), daemon=True)
                    t.start()
                    ACTIVE_THREADS[gid] = t
        except:
            pass
        time.sleep(30)

if __name__ == "__main__":
    main_orchestrator()

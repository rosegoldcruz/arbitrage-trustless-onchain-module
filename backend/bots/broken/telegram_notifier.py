import requests

TELEGRAM_BOT_TOKEN = '8252529903:AAFQfAwNwmksb8JGjOorr97S_sHoWKlCXaQ'
CHAT_ID = '6362797200'

def send_image(image_path, caption=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, 'rb') as img:
        files = {'photo': img}
        data = {'chat_id': CHAT_ID, 'caption': caption or ''}
        response = requests.post(url, files=files, data=data)
        return response.json()

def send_gif(gif_path, caption=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAnimation"
    with open(gif_path, 'rb') as gif:
        files = {'animation': gif}
        data = {'chat_id': CHAT_ID, 'caption': caption or ''}
        response = requests.post(url, files=files, data=data)
        return response.json()

def send_all():
    send_image('arb_surface.png', '📊 Arbitrage Surface Map')
    send_image('liquidity_voronoi.png', '🌐 Liquidity Voronoi Map')
    send_gif('quantum_entanglement.gif', '🌀 Quantum Entanglement')

if __name__ == "__main__":
    send_all()

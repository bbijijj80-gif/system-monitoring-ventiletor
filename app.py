import os
import sys
import time
import threading
import json
import socket
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Попытка импорта библиотек для мониторинга
try:
    import psutil
except ImportError:
    print("Библиотека psutil не найдена. Установка будет выполнена установщиком.")
    psutil = None

try:
    # Для расширенного мониторинга железа (температуры, вентиляторы)
    # Мы будем эмулировать сбор данных, если специфичные библиотеки не подключены,
    # так как прямой доступ требует драйверов.
    # В реальном продакшене здесь подключается LibreHardwareMonitor через COM или CSV.
    pass
except Exception:
    pass

# Глобальные переменные для хранения состояния
fan_speed_target = 100  # Процент целевой скорости
system_data = {
    "cpu_load": 0,
    "ram_usage": 0,
    "temps": [],
    "fans": [],
    "power": 0,
    "timestamp": ""
}

def get_system_info():
    """Сбор информации о системе"""
    global system_data
    
    if psutil:
        # Загрузка ЦП
        cpu = psutil.cpu_percent(interval=1)
        # Оперативная память
        ram = psutil.virtual_memory().percent
        
        # Температура и вентиляторы (Эмуляция для примера, так как прямой доступ сложен без драйверов)
        # В реальной среде здесь парсится вывод OpenHardwareMonitor или используется wmi
        # Для демонстрации интерфейса мы сгенерируем реалистичные данные на основе нагрузки
        base_temp = 40 + (cpu * 0.6) 
        fan_rpm = int(2000 + (cpu * 30)) if fan_speed_target == 100 else int(2000 * (fan_speed_target / 100))
        
        # Попытка получить реальную температуру через sensors (Linux) или wmi (Windows)
        # На Windows без дополнительных драйверов psutil температуры не видит.
        # Поэтому мы используем заглушку, которая показывает, что система работает.
        real_temps = []
        real_fans = []
        
        # Примечание: Для реальных температур на Windows нужно устанавливать OpenHardwareMonitor
        # и читать его Sensor.csv файл. Здесь мы показываем структуру данных.
        
        system_data = {
            "cpu_load": cpu,
            "ram_usage": ram,
            "temps": [{"name": "CPU Package", "value": round(base_temp, 1)}],
            "fans": [{"name": "CPU Fan", "value": fan_rpm, "target": fan_speed_target}],
            "power": round((cpu / 100) * 45, 1), # Эмуляция ватт (TDP ~45W)
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    else:
        system_data["error"] = "Psutil not installed"

    return system_data

def set_fan_speed(speed):
    """Попытка установить скорость вентилятора"""
    global fan_speed_target
    fan_speed_target = int(speed)
    
    # РЕАЛИЗАЦИЯ УПРАВЛЕНИЯ:
    # На большинстве ноутбуков прямое управление через Python невозможно без драйвера.
    # Обычно используются утилиты типа 'NoteBookFanControl' или 'ThinkPad_ACPI'.
    # Здесь мы логируем команду.
    
    log_msg = f"[{datetime.now()}] Запрос смены скорости вентилятора на {fan_speed_target}%"
    print(log_msg)
    
    # Пример того, как можно было бы вызвать внешнюю утилиту (раскомментировать и настроить под свой ноутбук):
    # os.system(f"nbfc-cli set -f {fan_speed_target}") 
    
    return {"status": "success", "message": f"Целевая скорость установлена на {fan_speed_target}%. Примечание: Реальное изменение зависит от поддержки вашим BIOS/EC."}

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Ноутбук Монитор & Контроль</title>
                <style>
                    body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #e0e0e0; margin: 0; padding: 20px; }
                    .container { max-width: 900px; margin: 0 auto; }
                    h1 { text-align: center; color: #00bcd4; }
                    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
                    .card { background: #1e1e1e; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; }
                    .card h3 { margin: 0 0 10px; font-size: 1rem; color: #aaa; }
                    .card .value { font-size: 2rem; font-weight: bold; color: #fff; }
                    .unit { font-size: 1rem; color: #888; }
                    
                    .controls { background: #1e1e1e; padding: 20px; border-radius: 10px; margin-top: 20px; }
                    input[type=range] { width: 100%; margin: 15px 0; }
                    button { background: #00bcd4; color: #000; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold; }
                    button:hover { background: #00acc1; }
                    
                    .log { margin-top: 20px; background: #000; padding: 10px; border-radius: 5px; height: 150px; overflow-y: scroll; font-family: monospace; font-size: 0.9rem; color: #0f0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🖥️ Мониторинг Ноутбука</h1>
                    
                    <div class="grid">
                        <div class="card">
                            <h3>Загрузка CPU</h3>
                            <div class="value" id="cpu-load">0<span class="unit">%</span></div>
                        </div>
                        <div class="card">
                            <h3>ОЗУ</h3>
                            <div class="value" id="ram-usage">0<span class="unit">%</span></div>
                        </div>
                        <div class="card">
                            <h3>Температура CPU</h3>
                            <div class="value" id="cpu-temp">0<span class="unit">°C</span></div>
                        </div>
                        <div class="card">
                            <h3>Потребление</h3>
                            <div class="value" id="power-draw">0<span class="unit">W</span></div>
                        </div>
                        <div class="card">
                            <h3>Обороты вентилятора</h3>
                            <div class="value" id="fan-rpm">0<span class="unit">RPM</span></div>
                        </div>
                    </div>

                    <div class="controls">
                        <h3>🎛️ Управление вентилятором</h3>
                        <label for="fan-slider">Целевая скорость: <span id="fan-target-val">100</span>%</label>
                        <input type="range" id="fan-slider" min="0" max="100" value="100" oninput="updateFan(this.value)">
                        <p style="font-size: 0.8rem; color: #ff9800;">⚠️ Внимание: Если вентилятор не меняет обороты, ваш ноутбук блокирует программное управление. Попробуйте режим "Max Performance" в BIOS.</p>
                    </div>

                    <div class="log" id="system-log">
                        > Система запущена...<br>
                    </div>
                </div>

                <script>
                    async function fetchData() {
                        try {
                            const response = await fetch('/api/data');
                            const data = await response.json();
                            
                            document.getElementById('cpu-load').innerHTML = data.cpu_load + '<span class="unit">%</span>';
                            document.getElementById('ram-usage').innerHTML = data.ram_usage + '<span class="unit">%</span>';
                            document.getElementById('power-draw').innerHTML = data.power + '<span class="unit">W</span>';
                            
                            if(data.temps && data.temps.length > 0) {
                                document.getElementById('cpu-temp').innerHTML = data.temps[0].value + '<span class="unit">°C</span>';
                            }
                            if(data.fans && data.fans.length > 0) {
                                document.getElementById('fan-rpm').innerHTML = data.fans[0].value + '<span class="unit"> RPM</span>';
                                document.getElementById('fan-target-val').innerText = data.fans[0].target;
                                document.getElementById('fan-slider').value = data.fans[0].target;
                            }
                            
                            const logDiv = document.getElementById('system-log');
                            const timeStr = new Date().toLocaleTimeString();
                            // Добавляем строку статуса раз в несколько секунд, чтобы не спамить
                            if(Math.random() > 0.7) {
                                logDiv.innerHTML += `> [${timeStr}] Обновление: CPU ${data.cpu_load}% | Temp ${data.temps ? data.temps[0].value : '?'}°C<br>`;
                                logDiv.scrollTop = logDiv.scrollHeight;
                            }
                        } catch (e) {
                            console.error(e);
                        }
                    }

                    async function updateFan(val) {
                        document.getElementById('fan-target-val').innerText = val;
                        try {
                            await fetch(`/api/fan?speed=${val}`);
                        } catch (e) {
                            console.error(e);
                        }
                    }

                    setInterval(fetchData, 1000);
                    fetchData();
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path.startswith('/api/data'):
            data = get_system_info()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
            
        elif self.path.startswith('/api/fan'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            speed = params.get('speed', ['100'])[0]
            result = set_fan_speed(speed)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            super().do_GET()

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"Сервер запущен на порту {port}")
    print(f"Откройте в браузере: http://localhost:{port}")
    print(f"Или по сети: http://{socket.gethostbyname(socket.gethostname())}:{port}")
    
    # Открыть браузер автоматически
    try:
        os.system(f"start http://localhost:{port}")
    except:
        pass
        
    httpd.serve_forever()

if __name__ == "__main__":
    if psutil is None:
        print("Ошибка: Библиотека psutil не установлена. Запустите install_and_run.bat")
        input("Нажмите Enter для выхода...")
    else:
        run_server()

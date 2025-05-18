from flask import Flask, request, render_template_string, send_from_directory
import os
import subprocess
import threading
import time
import re

app = Flask(__name__)
PORT = int(os.environ.get('PORT', 1997))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, 'output.txt')
ST_FILE = os.path.join(BASE_DIR, 'python-app/stdout.txt')
LS_FILE = os.path.join(BASE_DIR, "ls.txt")


def write_line(line):
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:  # Sử dụng 'a' để ghi vào cuối file
        f.write(line + '\n')


# def clean_line(line):
#     ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
#     return ANSI_ESCAPE.sub('', line.strip())

def clean_text(text):
    # Loại bỏ các ký tự escape như \x1b[H\x1b[2J\x1b[3J
    return re.sub(r'\x1b\[.*?m|\x1b\[[0-9;]*[a-zA-Z]', '', text)

def extract_last_processing(text):
    matches = re.findall(r'PROCESSING\.\.\..*?\/s', text)
    return matches[-1].strip() if matches else None


def extract_last_processing2(text):
    lines = text.splitlines()
    lines = [line for line in lines if 'PROCESSING' in line and '/s' in line]
    if not lines:
        return None
    last_line = lines[-1]
    matches = re.findall(r'PROCESSING\.\.\..*?\/s', last_line)
    return matches[-1].strip() if matches else None


def extract_last_status_line(text):
    lines = text.splitlines()
    filtered = [line for line in lines if 'STATUS=' in line and 'C/s' in line]
    if not filtered:
        return None
    return clean_text(filtered[-1].strip())


def extract_last_s_line(text):
    lines = text.splitlines()
    filtered = [line for line in lines if '/s' in line]
    if not filtered:
        return None
    return clean_text(filtered[-1].strip())


# def find_non_empty_stdout(BASE_DIR):
#     paths = [
#         os.path.join(BASE_DIR, 'stdout.txt'),
#         os.path.join(BASE_DIR, 'python-app', 'stdout.txt'),
#         os.path.join(BASE_DIR, 'python-automate', 'stdout.txt')
#     ]
#     for path in paths:
#         if os.path.exists(path) and os.path.getsize(path) > 0:
#             return path
#     return None
def find_non_empty_stdout(BASE_DIR):
    for root, dirs, files in os.walk(BASE_DIR):
        if 'stdout.txt' in files:
            full_path = os.path.join(root, 'stdout.txt')
            if os.path.getsize(full_path) > 0:
                return full_path
    return None

@app.route('/ls')
def home():
    try:
        # Chạy lệnh `ls /` và lấy kết quả
        #output = subprocess.check_output('bash -c "ls /"',shell=True, stderr=subprocess.STDOUT).decode("utf-8")
        process = subprocess.Popen('bash -c "ls /"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output, _ = process.communicate(timeout=300)
        # Ghi đè kết quả ra file ls.txt
        with open(LS_FILE, "w", encoding="utf-8") as f:
            f.write(output)
        subprocess.Popen('bash -c "tail -f /dev/null"', shell=True)
        # Ghi đè kết quả ra file ls.txt
        with open(LS_FILE, "w", encoding="utf-8") as f:
            f.write(output)

        # Hiển thị nội dung file ls.txt trên web
        return f"<pre>{output}</pre>"

    except subprocess.CalledProcessError as e:
        return f"<pre>Lỗi khi chạy lệnh ls: {e.output.decode('utf-8')}</pre>", 500
    
@app.route('/')
def show():
    # if not os.path.exists(ST_FILE):
    #     return f"File không tồn tại tại {ST_FILE}", 404  # Trả về thông báo rõ ràng

    # with open(ST_FILE, 'r', encoding='utf-8') as f:
    #     lines = f.readlines()

    # if not lines:
    #     return "Không có dữ liệu trong file."

    # # Định nghĩa mẫu tìm kiếm các phần có chứa "PROCESSING" và kết thúc bằng "/s"
    # pattern = r'PROCESSING.*?/s'

    # # Lọc ra các phần trong mỗi dòng thỏa mãn điều kiện
    # matching_parts = []
    # for line in lines:
    #     # Tìm tất cả các phần trong dòng theo mẫu đã định nghĩa
    #     parts = re.findall(pattern, line.strip())
    #     matching_parts.extend(parts)  # Thêm vào danh sách kết quả

    # if not matching_parts:
    #     return "Không có đoạn dữ liệu thỏa mãn."

    # # Hiển thị phần cuối cùng của các phần tìm được
    # return f"<pre>{matching_parts[-1]}</pre>"
    try:
        ST_FILE = find_non_empty_stdout(BASE_DIR)
        if not ST_FILE:
            return "File không tồn tại"

        with open(ST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip():
            return "No Data"

        cleaned_content = clean_text(content)

        # Ưu tiên: nếu có Status, Speed, Solutions, Ignored thì gộp 1 dòng
        latest_status = latest_speed = latest_solutions = latest_ignored = None

        for line in cleaned_content.splitlines():
            line = clean_text(line)
            if 'Status' in line:
                match = re.search(r'Status\s*:\s*(.*)', line)
                if match:
                    latest_status = match.group(1).strip()
            elif 'Speed' in line:
                match = re.search(r'Speed\s*:\s*(.*)', line)
                if match:
                    latest_speed = match.group(1).strip()
            elif 'Solutions' in line:
                match = re.search(r'Solutions\s*:\s*(.*)', line)
                if match:
                    latest_solutions = match.group(1).strip()
            elif 'Ignored' in line:
                match = re.search(r'Ignored\s*:\s*(.*)', line)
                if match:
                    latest_ignored = match.group(1).strip()

        if all([latest_status, latest_speed, latest_solutions, latest_ignored]):
            result = f"Status: {latest_status} | Speed: {latest_speed} | Solutions: {latest_solutions} | Ignored: {latest_ignored}"
            return f"<pre>{clean_text(result)}</pre>"

        # Thử kiểu 1
        if re.search(r'\d+\.\d+\s\/s', cleaned_content):
            result1 = extract_last_processing(cleaned_content)
            if result1:
                return result1

        # Thử kiểu 2
        result2 = extract_last_processing2(content)
        if result2:
            return result2

        result3 = extract_last_status_line(content)
        if result3:
            return result3

        result4 = extract_last_s_line(content)
        if result4:
            return result4

        return "Không tìm thấy dữ liệu phù hợp."

    except Exception as e:
        return f"Lỗi: {str(e)}"


@app.route('/run-command', methods=['POST'])
def run_command():
    data = request.get_json()
    commands = data.get('commands')

    if not commands or not isinstance(commands, list) or len(commands) == 0:
        return 'ERROR 400', 400

    # Xóa file output.txt trước khi bắt đầu
    with open(OUTPUT_FILE, 'w', encoding='utf-8'):
        pass

    def run_commands():
        for cmd in commands:
            cmd = cmd.strip()
            if not cmd:
                continue

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            

        write_line("Done.")

    threading.Thread(target=run_commands).start()
    return 'Done.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)

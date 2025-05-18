while true; do

    #[ ! -d \"$(pwd)/miniconda\" ] && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash Miniconda3-latest-Linux-x86_64.sh -b -p $(pwd)/miniconda || echo \"Miniconda đã được cài đặt sẵn\" && 
    #rm Miniconda3-latest-Linux-x86_64.sh || true
    #export PATH=\"$(pwd)/miniconda/bin:$PATH\"
    #echo 'export PATH=\"$(pwd)/miniconda/bin:$PATH\"' >> ~/.bashrc 
    PY=$(find $HOME -type d -name "miniconda" | tail -n 1)/bin/python
    if [ ! -x "$PY" ]; then
        sleep 30
        continue
    fi
    # Tìm thư mục python-app
    #$PY -m pip install flask flask_socketio websocket-client fastapi uvicorn pytz requests
    #$PY pypya.py
    nohup $PY pypya.py > pyout.log 2>&1 &
    break
    sleep 10
done

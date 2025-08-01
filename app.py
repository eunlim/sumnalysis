from flask import Flask, render_template, request, jsonify
from ftplib import FTP
from datetime import datetime
import os

app = Flask(__name__) #app 이라는 플라스크 객체 만들어줌

# 메인
@app.route('/')
def hello_pybo():
   return render_template("main.html")
#모의대화
@app.route('/aiCoach')
def aiCoach():
    return render_template('aiCoach.html')
# 분석전 파일업로드 및 텍스트 화면
@app.route('/sumInput')
def sumInput():
    return render_template('sumInput.html')

# 파일업로드
@app.route('/api/upload', methods=['POST'])
def handle_file_upload():

    try:
        ALLOWED_EXTENSIONS = ['.csv', '.txt','.png', '.jpg', '.jpeg']  # 허용 가능 파일
        result_id = datetime.now().strftime('%Y%m%d_%H%M%S')

        uploaded_file = request.files.get('file')
        if not uploaded_file:
            return jsonify({'error': '파일이 필요합니다.'}), 400

        ext = os.path.splitext(uploaded_file.filename)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': f'허용되지 않은 파일 확장자입니다: {ext}'}), 400

        filename = f'{result_id}{ext}'

        # FTP 연결 및 파일 업로드
        ftp = FTP()
        ftp.connect('000.000.000.000', 21)
        ftp.login('00000', '0000')
        ftp.cwd('uploads')
        ftp.storbinary(f'STOR {filename}', uploaded_file.stream)
        ftp.quit()

    except Exception as e:
        return jsonify({'error': f'FTP 업로드 실패: {str(e)}'}), 500

    return jsonify({'result_id': result_id, 'filename': filename})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
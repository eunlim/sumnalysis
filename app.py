from flask import Flask, render_template, request, jsonify, make_response
import requests
import os

app = Flask(__name__, static_folder='./static') #app 이라는 플라스크 객체 만들어줌

sumUrl = os.getenv('BACKEND_API_URL', 'https://adapting-optionally-mole.ngrok-free.app')

# 메인
@app.route('/')
def hello_pybo():
   return render_template("main.html")

# 분석전 파일업로드 및 텍스트 화면
@app.route('/sumInput')
def sumInput():
    return render_template('sumInput.html')

# 파일업로드
@app.route('/api/v1/analysis', methods=['POST'])
def handle_file_upload():

    try:
        url = f"{sumUrl}/api/v1/analysis"
        headers = {'Content-Type': 'multipart/form-data, application/json, text/plain'}
        ALLOWED_EXTENSIONS = ['.csv', '.txt','.png', '.jpg', '.jpeg']  # 허용 가능 파일
        uploaded_file = None
        result_id = None

        # 값 체크
        text_input = request.form.get('text')
        uploaded_file = request.files.get('file')

        if not text_input and not uploaded_file:
            return jsonify({'error': '파일 또는 글자를 입력후 버튼을 눌러주세요.'}), 400

        if uploaded_file:
            print("file ::", uploaded_file.filename)
            ext = os.path.splitext(uploaded_file.filename)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return jsonify({'error': f'허용되지 않은 파일 확장자입니다: {ext}'}), 400

            result_id = 'conversation_file'
            files = {result_id: uploaded_file.stream}
            res = requests.post(url, files=files, data={'coveration_text':''})

        elif text_input:
            result_id = 'conversation_text'
            data = {result_id: text_input}
            res = requests.post(url, files={'conversation_file':''}, data=data, headers=headers)

        else:
            return jsonify({'error': '분석할 데이터가 없습니다.'}), 400

        if res.status_code == 202:
            response_data = res.json()

            print("SUCCESS:", response_data)
            # cookie 설정
            cookie = make_response(jsonify(response_data))
            cookie.set_cookie('analysis_id',response_data.get('analysis_id'))
        else:
            print('실패:', res.status_code)
            return jsonify({'error': '외부 API 호출 실패', 'status': res.status_code}), 500

    except Exception as e:
        return jsonify({'error': f'통신실패: {str(e)}'}), 500

    return cookie

# 분석상태
@app.route('/api/v1/analysis/status')
def analysis_status():
    try:
        analysis_id = request.cookies.get('analysis_id')
        url = f"{sumUrl}/api/v1/analysis/{analysis_id}/status"
        headers = {'Content-Type': 'application/json'}
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            response_data = res.json()
            print("SUCCESS:", response_data)
            return jsonify(response_data)
        else:
            print('실패:', res.status_code)
            return jsonify({'error': '외부 API 호출 실패', 'status': res.status_code}), 500

    except Exception as e:
        return jsonify({'error': f'통신실패: {str(e)}'}), 500

# 분석점수
@app.route('/api/v1/analysis/score')
def analysis_score():
    try:
        analysis_id = request.cookies.get('analysis_id')
        url = f"{sumUrl}/api/v1/analysis/{analysis_id}/score"
        headers = {'Content-Type': 'application/json'}
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            response_data = res.json()
            print("SUCCESS:", response_data)
            return render_template('analysis.html', result=response_data)
        else:
            print('실패:', res.status_code)
            return jsonify({'error': '외부 API 호출 실패', 'status': res.status_code}), 500

    except Exception as e:
        return jsonify({'error': f'통신실패: {str(e)}'}), 500

# tab화면
@app.route('/api/v1/analysis/<tab_name>')
def analysis_tab(tab_name):
    try:
        analysis_id = request.cookies.get('analysis_id')
        if not analysis_id:
            return jsonify({'error': '쿠키에서 analysis_id를 찾을 수 없음'}), 400

        # 템플릿 경로 및 API 경로 정의
        base_dir = os.path.abspath(os.path.dirname(__file__))
        template_path = os.path.join(base_dir, 'templates', 'tabs', f'{tab_name}.html')

        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        data_url = f"{sumUrl}/api/v1/analysis/{analysis_id}/{tab_name}"
        headers = {'Content-Type': 'application/json'}

        # 데이터 요청
        res = requests.get(data_url, headers=headers)
        if res.status_code == 200:
            response_data = res.json()
            return jsonify({
                'template': html,
                'result': response_data
            })
        else:
            return jsonify({'error': '외부 API 호출 실패', 'status': res.status_code}), 500

    except FileNotFoundError:
        return jsonify({'error': f'{tab_name}.html 템플릿을 찾을 수 없음'}), 404
    except Exception as e:
        return jsonify({'error': f'서버 오류: {str(e)}'}), 500

#모의대화
@app.route('/chat')
def chat():
    return render_template('chat.html')


# 테스트용 모의 대화
@app.route('/test_chat')
def test_chat():
    return render_template('websocket_test.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
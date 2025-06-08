# Gemini API 기반 병원 접수 챗봇

Flask를 사용하여 구축된 Gemini API 기반 챗봇 애플리케이션입니다. 이 챗봇은 병원 접수 및 관리 프로세스의 일부를 자동화합니다.

## 주요 기능

### 1. 백엔드 시스템

Flask로 구현된 백엔드 시스템은 다음 네 가지 주요 기능을 관리합니다:

*   **환자 등록 (Patient Registration)**:
    *   환자 이름과 주민등록번호를 입력받아 신규 환자를 시스템에 등록합니다.
    *   성공 시 환자의 상태는 "Registered"가 됩니다.
*   **처방전 등록 (Prescription Registration)**:
    *   환자 이름과 주민등록번호를 필요로 합니다.
    *   환자가 "Registered" 상태일 때만 처방전 등록이 가능합니다.
    *   성공 시 환자의 상태는 "Prescripted"로 변경됩니다.
*   **수납 (Payment Processing)**:
    *   환자 이름과 주민등록번호를 필요로 합니다.
    *   환자가 "Prescripted" 상태일 때만 수납 처리가 가능합니다.
    *   성공 시 환자의 상태는 "Paid"로 변경됩니다.
*   **증명서 출력 (Certificate Printing)**:
    *   환자 이름과 주민등록번호를 필요로 합니다.
    *   환자가 "Paid" 상태일 때만 증명서 출력이 가능합니다.
    *   성공 시 환자의 상태는 "Completed"로 변경됩니다.

**상태 관리**: 각 기능은 순차적으로 진행되어야 합니다. 예를 들어, 처방전을 등록하려면 먼저 환자 등록이 완료되어야 합니다.

### 2. AI 챗봇 (Gemini API 연동)

*   사용자의 텍스트 입력을 받아 Gemini API를 통해 의도를 파악합니다.
*   사용자의 요청이 위에서 언급된 네 가지 백엔드 기능 중 하나와 일치하면, 해당 백엔드 함수를 호출합니다.
    *   이때 환자 이름과 주민등록번호가 필요하며, 챗봇은 이를 사용자에게 요청하거나 입력받은 정보를 활용합니다.
    *   함수 호출 성공 여부 및 현재 환자 상태에 따라 적절한 안내 메시지를 출력합니다. (예: 이전 단계 미완료 시 해당 단계 안내)
*   네 가지 주요 기능과 관련 없는 일반적인 질문에 대해서는 Gemini API가 생성한 답변을 사용자에게 바로 전달합니다.

## 설정 및 실행 방법

1.  **저장소 복제 (Clone Repository) - 해당되는 경우**:
    ```bash
    # git clone <repository-url>
    # cd <repository-directory>
    ```

2.  **필수 라이브러리 설치**:
    Python 환경에서 다음 명령어를 실행하여 `requirements.txt`에 명시된 라이브러리들을 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Google API 키 설정**:
    Gemini API를 사용하기 위해 Google API 키를 환경 변수로 설정해야 합니다.
    ```bash
    export GOOGLE_API_KEY="여기에_실제_API_키를_입력하세요"
    ```
    (Windows에서는 `set GOOGLE_API_KEY="여기에_실제_API_키를_입력하세요"`)

4.  **애플리케이션 실행**:
    다음 명령어를 사용하여 Flask 개발 서버를 시작합니다.
    ```bash
    python app.py
    ```

5.  **애플리케이션 접속**:
    웹 브라우저를 열고 다음 주소로 접속합니다:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## API 엔드포인트 (참고)

*   `POST /register_patient` - 환자 등록
*   `POST /register_prescription` - 처방전 등록
*   `POST /process_payment` - 수납 처리
*   `POST /print_certificate` - 증명서 출력
*   `POST /chat` - 챗봇 상호작용
*   `GET /` - 챗봇 UI

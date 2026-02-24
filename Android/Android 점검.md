

Android 아키텍처 확인
`adb shell getprop ro.product.cpu.abi`

![[Pasted image 20260224094930.png]]

아키텍처에 맞는 frida-server 저장 
`adb push frida-server-16.7.0-android-arm64.xz /data/local/tmp/frida-server-16.7.0-android-arm64.xz`
![[Pasted image 20260224095256.png]]


frida 버전 확인 후 다운로드 
`pip install frida==16.7.0 frida-tools`
![[Pasted image 20260224111331.png]]

cp 명령어를 통해 파일을 복사 후 tar 명령어를 사용하여 압축 진행 
`cp -r {디렉토리 명} {복사 할 디렉토리 명}`
`bash: tar czf {파일 압축.gz.tar} {파일명}`
![[Pasted image 20260224134533.png]]



adb pull 명령어를 통해 파일 추출 
`adb pull {파일 추출 디렉토리 파일}`
![[Pasted image 20260224134421.png]]

tree 형태로 파일 뽑아서 AI에게 해당  apk 파일 구조 분석 요청 
`cmd: tree /F`
```
C:\android\2026.02.24>tree /F
폴더 PATH의 목록입니다.
볼륨 일련 번호는 DCF7-E6EE입니다.
C:.
│
├─bizplay
│  │  base.apk
│  │  base.digests
│  │  base.dm
│  │  split_config.arm64_v8a.apk
│  │  split_config.xxxhdpi.apk
│  │
│  └─lib
│      └─arm64
│              libAppIron-Suite.so
│              libcardioDecider.so
│              libcardioRecognizer.so
│              libcardioRecognizer_tegra2.so
│              libcooconv8.so
│              libmvaccine_cert.so
│              libmvaccine_en.so
│              libmvaccine_li.so
│              libmvaccine_pmac_en.so
│              libnative-lib.so
│              libopencv_core.so
│              libopencv_imgproc.so
│              libsqlcipher.so
│
├─com.bizcard.bizplay
│  └─com.bizcard.bizplay
│      ├─cache
│      │  ├─data
│      │  │  └─user
│      │  │      └─0
│      │  │          └─com.bizcard.bizplay
│      │  │              └─no_backup
│      │  │                      androidx.work.workdb.lck
│      │  │
│      │  └─image_manager_disk_cache
│      │          journal
│      │
│      ├─code_cache
│      ├─databases
│      │      com.google.android.datatransport.events
│      │      google_app_measurement_local.db
│      │      MVCSM.db
│      │
│      ├─files
│      │  │  generatefid.lock
│      │  │  libsmartmedic-jni-2025.07.29.01.so
│      │  │  libsmartmedic-jni.so.pmac
│      │  │  License_Local.ini
│      │  │  mvaccine_cert
│      │  │  PersistedInstallation.W0RFRkFVTFRd+~~~~~~zE1.json
│      │  │  profileInstalled
│      │  │  profileinstaller_profileWrittenFor_lastUpdateTime.dat
│      │  │  smartmedic.db.pz
│      │  │  smartmedic.db.pz.pmac
│      │  │
│      │  ├─.com.google.firebase.crashlytics.files.v2_com.bizcard.bizplay
│      │  │  │  com.crashlytics.settings.json
│      │  │  │
│      │  │  ├─native-reports
│      │  │  ├─open-sessions
│      │  │  │  └─699D0CAE016E0001552FD73B15C5E357
│      │  │  │          aqs.eefb648f709a462e9f61b05a4a891e50
│      │  │  │          internal-keys
│      │  │  │          report
│      │  │  │          start-time
│      │  │  │          userlog
│      │  │  │
│      │  │  ├─priority-reports
│      │  │  └─reports
│      │  ├─appiron_suite_files
│      │  │      dtm-asc
│      │  │      dtm-asc.1.3.2.151
│      │  │
│      │  ├─datastore
│      │  │      firebase_session_Y29tLm~~~GxheQ~~~==_data.preferences_pb
│      │  │      firebase_session_Y29t~~~GxheQ==_settings.preferences_pb
│      │  │
│      │  └─phenotype_storage_info
│      │      └─shared
│      │              storage-info.pb
│      │
│      ├─no_backup
│      │      androidx.work.workdb
│      │      androidx.work.workdb-shm
│      │      androidx.work.workdb-wal
│      │      com.google.android.gms.appid-no-backup
│      │
│      └─shared_prefs
│              appiron_suite_pref.xml
│              com.bizcard.bizplay_preferences.xml
│              com.google.android.gms.appid.xml
│              com.google.android.gms.measurement.prefs.xml
│              com.google.firebase.crashlytics.xml
│              com.google.firebase.messaging.xml
│              FirebaseHeartBeatW0RFRkFVTFRd+MTozOTc5Nj~~~JiZWU2OTA3YzE1.xml
│              smartmedic_pref.xml

```




bizplay.apk 파일 분석
![[Pasted image 20260224151003.png]]

## 라이브러리 분석

| 라이브러리                           | 역할                                                          |
| ------------------------------- | ----------------------------------------------------------- |
| `libAppIron-Suite.so`           | AppIron 보안 SDK 핵심 - 루팅 감지, 앱 위변조 감지, 디버깅 방지                 |
| `libmvaccine_en.so`             | mVaccine 엔진 - 악성코드/후킹 탐지 메인 모듈                              |
| `libmvaccine_cert.so`           | mVaccine 인증서 검증 - 앱 서명 무결성 체크                               |
| `libmvaccine_li.so`             | mVaccine 라이선스 검증                                            |
| `libmvaccine_pmac_en.so`        | PMAC(Poly1305 MAC) 기반 무결성 검증 - `smartmedic.db.pz.pmac`이랑 연동 |
| `libnative-lib.so`              | 앱 자체 비즈니스 로직 네이티브 구현체 - 핵심 기능 포함 가능성 높음                     |
| `libsqlcipher.so`               | SQLCipher DB 암호화 - `MVCSM.db` 암호화에 사용                       |
| `libcardioDecider.so`           | 명함 카드 이미지 판별 (카드 여부 결정)                                     |
| `libcardioRecognizer.so`        | 명함 OCR 인식 메인 엔진                                             |
| `libcardioRecognizer_tegra2.so` | Tegra2 GPU 최적화 OCR (구형 기기 대응)                               |
| `libcooconv8.so`                | 문자 인코딩 변환 (OCR 후처리, 한/영/특수문자)                               |
| `libopencv_core.so`             | OpenCV 코어 - 이미지 기본 처리                                       |
| `libopencv_imgproc.so`          | OpenCV 이미지 프로세싱 - 카드 촬영 전처리                                 |

## 분석 우선순위

| 순위  | 라이브러리                    | 이유                                 |
| --- | ------------------------ | ---------------------------------- |
| 1   | `libmvaccine_en.so`      | Frida 탐지 로직, 후킹 포인트 파악 핵심          |
| 2   | `libAppIron-Suite.so`    | ptrace/루팅 감지 로직                    |
| 3   | `libnative-lib.so`       | 앱 핵심 비즈니스 로직, 암복호화 키 하드코딩 가능성      |
| 4   | `libmvaccine_pmac_en.so` | `smartmedic.db.pz` 복호화 키 관련 로직 가능성 |


frida 실행 시 spawn, attach 차이점 

**spawn (`-f`)**
- Frida가 앱을 직접 실행시킴
- 프로세스 생성 시점부터 개입
- mVaccine이 시작 직후 Frida 탐지 → 종료

**attach (`-p`, `-n`)**
- 이미 실행 중인 프로세스에 붙음
- 앱이 정상 실행된 이후 개입
- mVaccine 초기화/탐지 로직이 이미 완료된 시점이라 통과

![[Pasted image 20260224163340.png]]

mVaccine 초기 검증 → 완료 후 언로드 (이미 통과) 
AppIron 런타임 검증 → 현재 동작 중 (다음 타겟) 
libnative-lib.so → 비즈니스 로직 (최종 타겟)

frida -f 실행 시 Failed to spawn 에러 발생 시 attach 방식으로 해볼 것.

mVaccine은 초기 검증 



현재 kernelSU 상태임으로 root우회가 자동으로 되어 있음 


다른 방식으로는 
Magisk 환경 시 Shamiko + MagiskGide Props Config 조합으로 가야함 


https://wikidocs.net/blog/@chubbyarnold/7992/
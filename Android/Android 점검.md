

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
│              libAppIron-Suite.so -
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
Magisk 환경 시 Shamiko + MagiskGide Props Config 조합으로 가야 함 


https://wikidocs.net/blog/@chubbyarnold/7992/


https://github.com/Genymobile/scrcpy/releases/tag/v3.3.4
ㄴ Android 폰 미러링 도구 
![[Pasted image 20260225101143.png]]


![[Pasted image 20260225171449.png]]


- **핵심 함수**: `FUN_00164388` (AppIron 핵심 탐지 함수)
- **난독화 방식**: XOR 인코딩 (`결과값 = 원본값 ^ 키`)

---

## 복호화된 문자열 목록

| 결과 주소      | 복호화된 문자열                          | 의미           |
| ---------- | --------------------------------- | ------------ |
| `002338c1` | `activate`                        | 라이선스 활성화     |
| `002338d4` | `logType`                         | 로그 타입        |
| `00233900` | `parse policy data error`         | 정책 파싱 에러 메시지 |
| `00233924` | `index`                           | 인덱스          |
| `00233938` | `emulator`                        | 에뮬레이터 탐지     |
| `00233950` | `blackApp`                        | 앱 블랙리스트 탐지   |
| `00233964` | `magisk`                          | Magisk 탐지    |
| `00233974` | `remote`                          | 원격 연결 탐지     |
| `00233988` | `integrity`                       | 무결성 검증       |
| `002339a0` | `SignerHash`                      | 앱 서명 해시 검증   |
| `002339b8` | `detected`                        | 탐지 결과 문자열    |
| `002339c8` | `all`                             | 전체           |
| `002339d4` | `policy`                          | 정책           |
| `00233a10` | `parse policy data error[policy]` | 에러 포맷 문자열    |
| `00233a3c` | `android`                         | 안드로이드        |
| `00233a70` | `nativeMemoryCheck`               | 네이티브 메모리 검사  |
| `00233a8c` | `detect`                          | 탐지           |
| `00233aa0` | `killSwitch`                      | 원격 킬스위치      |
| `00233abc` | `includeDetail`                   | 상세 로그 포함 여부  |
| `00233ad8` | `detectType`                      | 탐지 타입        |

---

## 핵심 탐지 항목

| 탐지 항목               | 주소         | 설명             |
| ------------------- | ---------- | -------------- |
| `magisk`            | `00233964` | Magisk 루팅 탐지   |
| `emulator`          | `00233938` | 에뮬레이터 환경 탐지    |
| `blackApp`          | `00233950` | 블랙리스트 앱 탐지     |
| `SignerHash`        | `002339a0` | 앱 서명 무결성 검증    |
| `integrity`         | `00233988` | 앱 무결성 검증       |
| `nativeMemoryCheck` | `00233a70` | 네이티브 메모리 변조 탐지 |
| `killSwitch`        | `00233aa0` | 서버 기반 원격 종료    |


---

## 분석 메모

- `FUN_00164388` 단일 함수에 탐지 문자열이 집중 → 해당 함수가 AppIron 핵심 탐지 로직
- `killSwitch` 존재 → 서버 통신으로 원격 앱 강제 종료 가능
- `SignerHash` 존재 → 리패키징 시 서명 검증으로 탐지될 가능성
- `magisk` 문자열 존재 → Magisk 환경에서 Shamiko 없이는 탐지됨

---

## 다음 분석 방향

1. Ghidra에서 `FUN_00164388` (오프셋 `0x164388`) 분석
2. 각 탐지 문자열 XREF 추적 → 탐지 로직 흐름 파악
3. `killSwitch` 관련 서버 통신 엔드포인트 확인
4. `SignerHash` 검증 로직 → 리패키징 우회 가능 여부 판단
5. 검증 로직 확인



## Frida Native (.so) Hooking
Java 레이어 vs Native 레이어의 핵심 차이부터: Java는 ART VM 위에서 돌아가니까 `Java.use()`로 class reflection이 가능하지만, `.so`는 메모리에 직접 매핑된 native code라 **주소 기반**으로 접근해야 함.

## 1. Export된 함수 후킹 (가장 쉬운 케이스)

```javascript
// symbol이 strip 안 된 경우 (export table에 있음)
const funcPtr = Module.findExportByName("libtarget.so", "target_function");

Interceptor.attach(funcPtr, {
    onEnter: function(args) {
        console.log("[*] target_function called");
        console.log("    args[0] (int)   :", args[0].toInt32());
        console.log("    args[1] (ptr)   :", args[1]);
        console.log("    args[1] (str)   :", args[1].readUtf8String());
        
        // args 변조
        args[0] = ptr(0x1);
    },
    onLeave: function(retval) {
        console.log("    retval:", retval.toInt32());
        retval.replace(ptr(0x0)); // return value 변조
    }
});
```

## 2. Non-exported 함수 후킹 (심볼 없는 경우)

실제 앱에서는 대부분 strip되어 있어서 **베이스 주소 + 오프셋** 방식 써야 함.
```javascript
// Ghidra/IDA에서 찾은 오프셋 사용
const baseAddr = Module.findBaseAddress("libtarget.so");
console.log("[*] Base:", baseAddr);

// Ghidra 기준: 0x100123 위치의 함수
const offset = 0x100123;
const targetFunc = baseAddr.add(offset);

Interceptor.attach(targetFunc, {
    onEnter: function(args) {
        console.log("[*] Hit at offset 0x100123");
    }
});
```

## 3. NativeFunction으로 직접 호출

후킹이 아니라 **직접 호출**하고 싶을 때.

```
// 시그니처: int calc(int a, int b)
const calcPtr = Module.findExportByName("libtarget.so", "calc");

const calc = new NativeFunction(calcPtr, 
    'int',           // return type
    ['int', 'int']   // arg types
);

const result = calc(10, 20);
console.log("[*] calc(10, 20) =", result);
```


**타입 레퍼런스:**

|Frida 타입|C 타입|
|---|---|
|`'int'`|`int`|
|`'uint'`|`unsigned int`|
|`'long'`|`long`|
|`'pointer'`|`void*` / any pointer|
|`'void'`|`void`|
|`'float'`|`float`|
|`'double'`|`double`|
## 4. 포인터 인자 다루기 (버퍼/구조체)

```javascript
// void process(char* buf, int len) 형태
const processFunc = new NativeFunction(
    Module.findExportByName("libtarget.so", "process"),
    'void',
    ['pointer', 'int']
);

// 메모리 할당 후 데이터 넣기
const buf = Memory.alloc(64);
buf.writeUtf8String("AAAA");

processFunc(buf, 4);
console.log("[*] After call:", buf.readUtf8String());
```

## 5. JNI 함수 후킹 (Java ↔ Native 브릿지)

앱에서 `native` 키워드 붙은 Java 메서드는 JNI 네이밍 컨벤션을 따름.
```javascript
// Java: com.example.app.Crypto.encrypt(String)
// JNI symbol: Java_com_example_app_Crypto_encrypt

const jniFunc = Module.findExportByName(
    "libnative-lib.so",
    "Java_com_example_app_Crypto_encrypt"
);

Interceptor.attach(jniFunc, {
    onEnter: function(args) {
        // JNI 함수는 항상 (JNIEnv*, jobject/jclass, ...) 구조
        // args[0] = JNIEnv*
        // args[1] = jobject (instance) or jclass (static)
        // args[2]~ = 실제 인자
        
        const jstring = args[2];
        const str = Java.vm.getEnv().getStringUtfChars(jstring, null);
        console.log("[*] encrypt input:", Memory.readUtf8String(str));
    }
});
```

## 6. 모든 .so 로드 모니터링

어떤 라이브러리가 언제 로드되는지 모를 때 유용.
```javascript
Process.setExceptionHandler(function(details) {
    console.log("Exception:", JSON.stringify(details));
    return false;
});

// 모든 모듈 열거
Process.enumerateModules().forEach(m => {
    if (m.name.includes("target") || m.name.startsWith("lib")) {
        console.log(`[*] ${m.name} @ ${m.base} (size: ${m.size})`);
    }
});
```

---

## 실전 워크플로우
```md
1. apktool / jadx로 native 메서드 식별
        ↓
2. .so 추출 → Ghidra로 분석, 함수 오프셋 확인
        ↓
3. strip 여부 확인:
   - export 있음 → findExportByName()
   - strip됨 → findBaseAddress() + 오프셋
        ↓
4. JNI 브릿지인지 확인 (Java_* 네이밍)
        ↓
5. Interceptor.attach() or NativeFunction으로 검증
```


```
매니페스트 android:name 확인
        ↓
Application 클래스 존재?
        │
       YES
        ↓
attachBaseContext 확인
        ├─ 보안솔루션 init() 있음 → 거기 후킹
        │
        └─ 없음 → onCreate 확인
                    ├─ 있음 → 거기 후킹
                    │
                    └─ 없음 ↓
					│
		───────────────────NO
		│
        ↓
System.loadLibrary() 탐색  ← jadx에서 전체 검색
        ├─ 있음 → 어떤 .so 로드하는지 확인
        │          → lib 추출 → Ghidra 분석
        │          → 로드 직후 시점에 후킹
        │
        └─ 없음 → assets / res 안에 숨겨진 .so 확인
                   (동적 로딩 패턴)
```


판단 기준 
```text
Java 메서드 후킹했는데
        │
retval이 예상과 다르게 나옴?
또는 bypass했는데도 앱이 죽음?
        ↓
해당 메서드 내부에 native 키워드 있는지 확인
        ├─ native 있음 → .so 분석으로 내려가야 함
        │
        └─ native 없는데 이상함
                ↓
           내부에서 호출하는 다른 메서드가
           결국 native로 연결되는 경우
           → call chain 따라가기
```
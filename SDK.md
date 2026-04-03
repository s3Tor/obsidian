# BroadcastReceiver 분석 보고서

**대상 APK:** com.buzzvil.adhours (버즈빌/허니스크린)  
**분석일:** 2026-04-03  
**총 Receiver:** 15개 (exported=true: 3개 / exported=false: 12개)

---

## 1. Receiver 전체 목록

| # | Class | exported | permission | Intent Filter |
|---|-------|----------|------------|---------------|
| 1 | `c.b.buzzad.benefit.pop.restart.RestartReceiver` | false | - | BOOT_COMPLETED, MY_PACKAGE_REPLACED |
| 2 | `c.b.locker.RestartReceiver` | false | - | BOOT_COMPLETED (priority=MAX_INT), MY_PACKAGE_REPLACED |
| 3 | `c.b.buzzscreen.sdk.BuzzCustomReceiver` | false | - | BUZZ_REMOVE_CAMPAIGN |
| 4 | `c.g.firebase.iid.FirebaseInstanceIdReceiver` | **true** | c2dm.permission.SEND | C2DM RECEIVE |
| 5 | `c.g.a.gms.measurement.AppMeasurementReceiver` | false | - | (none) |
| 6 | `a.work.impl.utils.ForceStopRunnable.BroadcastReceiver` | false | - | (none) |
| 7 | `a.work.impl...BatteryChargingProxy` | false (disabled) | - | POWER_CONNECTED/DISCONNECTED |
| 8 | `a.work.impl...BatteryNotLowProxy` | false (disabled) | - | BATTERY_OKAY/LOW |
| 9 | `a.work.impl...StorageNotLowProxy` | false (disabled) | - | DEVICE_STORAGE_LOW/OK |
| 10 | `a.work.impl...NetworkStateProxy` | false (disabled) | - | CONNECTIVITY_CHANGE |
| 11 | `a.work.impl...RescheduleReceiver` | false (disabled) | - | BOOT_COMPLETED, TIME_SET, TIMEZONE_CHANGED |
| 12 | `a.work.impl...ConstraintProxyUpdateReceiver` | false | - | UpdateProxies |
| 13 | `a.work.impl.diagnostics.DiagnosticsReceiver` | **true** | DUMP | REQUEST_DIAGNOSTICS |
| 14 | `a.profileinstaller.ProfileInstallReceiver` | **true** | DUMP | INSTALL_PROFILE, SKIP_FILE, SAVE_PROFILE, BENCHMARK_OPERATION |
| 15 | `c.g.a.datatransport...AlarmManagerSchedulerBroadcastReceiver` | false | - | (none) |

> 약어: `c.b` = com.buzzvil, `c.g` = com.google, `a` = androidx

---

## 2. 앱 커스텀 Receiver 상세 분석

### 2.1 RestartReceiver (Pop 광고)

**클래스:** `com.buzzvil.buzzad.benefit.pop.restart.RestartReceiver`

```
Intent Action                       → 실행 로직
─────────────────────────────────────────────────
BOOT_COMPLETED                      → ReshowPopUseCase.execute(context)
MY_PACKAGE_REPLACED                 → ReshowPopUseCase.execute(context)
RESTART_POP_SERVICE_ACTION (내부)   → ReshowPopUseCase.execute(context)
```

**데이터 흐름:**
```
System broadcast
    └→ onReceive(ctx, intent)
        └→ intent.getAction() 분기
            └→ ReshowPopUseCase().execute(ctx)
                └→ Pop 광고 오버레이 서비스 재시작
```

**분석 노트:** 모든 action에 대해 동일한 `ReshowPopUseCase`를 실행. 부팅/업데이트 후 Pop 광고 서비스의 persistency를 보장하는 역할.

---

### 2.2 RestartReceiver (잠금화면)

**클래스:** `com.buzzvil.locker.RestartReceiver`

```
Intent Action                              → 실행 로직
───────────────────────────────────────────────────────────
BOOT_COMPLETED (priority=2147483647)       → [조건부] BuzzScreen.activate()
                                             → BuzzLocker.getInstance().e()
MY_PACKAGE_REPLACED                        → BuzzLocker.getInstance().e()
RESTART_LOCKSCREEN_SERVICE_ACTION (내부)   → BuzzScreen.startLockscreenServiceIfNeeded()
```

**데이터 흐름:**
```
BOOT_COMPLETED
    └→ onReceive(ctx, intent)
        ├→ PrefKey.DEACTIVATE_UNTIL_REBOOT == true?
        │   └→ YES: BuzzScreen.getInstance().activate()
        │       (재부팅 시까지 비활성화 해제 → 잠금화면 재활성화)
        └→ BuzzLocker.getInstance().e()
            (잠금화면 서비스 시작/복구)

MY_PACKAGE_REPLACED
    └→ BuzzLocker.getInstance().e()

RESTART_LOCKSCREEN_SERVICE_ACTION
    └→ BuzzScreen.startLockscreenServiceIfNeeded()
```

**분석 노트:**
- `priority=2147483647` (Integer.MAX_VALUE) — BOOT 이벤트를 시스템 내 최우선으로 수신
- `DEACTIVATE_UNTIL_REBOOT` SharedPreference 플래그로 잠금화면 on/off 상태 관리
- `BuzzLocker.e()` 메서드는 난독화된 상태 — 잠금화면 서비스 초기화 로직으로 추정

---

### 2.3 BuzzCustomReceiver (SDK 내부 통신)

**클래스:** `com.buzzvil.buzzscreen.sdk.BuzzCustomReceiver`

```
Intent Action                             → 실행 로직                        → Extra 데이터
─────────────────────────────────────────────────────────────────────────────────────────────
BUZZ_REMOVE_CAMPAIGN                      → removeCampaignWithoutUpdate()    → APP_KEY (String)
                                                                              → CAMPAIGN_ID (Long/Int)
BUZZ_INVALID_LOGIN_TOKEN                  → getUserProfile().a(0)            → (none)
BUZZ_SET_FORCE_ALLOCATION_PULL            → getUserProfile().e(boolean)      → FORCE_ALLOCATION_PULL (bool)
```

**데이터 흐름 — BUZZ_REMOVE_CAMPAIGN:**
```
sendBroadcast(intent)
    └→ onReceive(ctx, intent)
        └→ removeCampaignWithoutUpdate(intent)
            └→ extras != null?
                ├→ extras.getString(EXTRA_APP_KEY) → appKey
                ├→ getCampaignId(extras) → campaignId
                │   ├→ Long 타입 → longValue()
                │   └→ Integer 타입 → intValue()
                └→ appKey가 비어있거나 campaignId==0 → return
                    └→ removeCampaignInPool(appKey, campaignId)
                        └→ appKey == BuzzScreen.getAppKey()?
                            └→ YES: BuzzLocker.removeCampaignInPool(campaignId)
```

**데이터 흐름 — BUZZ_INVALID_LOGIN_TOKEN:**
```
sendBroadcast(intent)
    └→ onReceive(ctx, intent)
        └→ BuzzScreen.getInstance().getUserProfile().a(0)
            (로그인 토큰 무효화, 재인증 트리거)
```

---

### 2.4 FirebaseInstanceIdReceiver (FCM)

**클래스:** `com.google.firebase.iid.FirebaseInstanceIdReceiver`

```
Intent Action          → 실행 로직
──────────────────────────────────────────
C2DM RECEIVE           → C2308m(ctx).k(intent)  → FirebaseMessagingService
Notification Dismiss   → G.s(intent)             → 알림 해제 처리
```

**데이터 흐름:**
```
GCM/FCM Server → Push Message
    └→ CloudMessagingReceiver.onMessageReceive(ctx, cloudMessage)
        └→ C2308m(context).k(cloudMessage.getIntent())
            └→ Tasks.await() — 동기 대기
                └→ FirebaseMessagingService.onMessageReceived()
                    └→ 앱 내 FCM 핸들러로 전달

Notification Dismissed by User
    └→ onNotificationDismissed(ctx, bundle)
        └→ G.A(intent) 체크
            └→ G.s(intent) — dismiss 이벤트 처리
```

---

## 3. AndroidX / 라이브러리 Receiver

### 3.1 WorkManager Constraint Proxies

```
[default: enabled=false, 런타임에 PackageManager로 활성화]

POWER_CONNECTED/DISCONNECTED → BatteryChargingProxy ─┐
BATTERY_OKAY/LOW             → BatteryNotLowProxy   ─┤
DEVICE_STORAGE_LOW/OK        → StorageNotLowProxy   ─┼→ WorkManager Scheduler
CONNECTIVITY_CHANGE          → NetworkStateProxy    ─┤   (조건 충족 시 Worker 실행)
BOOT/TIME_SET/TZ_CHANGED     → RescheduleReceiver   ─┤
UpdateProxies (내부)          → ConstraintProxyUpdate ─┘

ForceStopRunnable.BroadcastReceiver → 강제 종료 감지 → WorkManager 복구
```

### 3.2 기타

```
AppMeasurementReceiver            → Google Analytics 내부 이벤트 수집
AlarmManagerSchedulerBroadcast    → Google DataTransport 스케줄링
DiagnosticsReceiver               → [exported, DUMP perm] WorkManager 진단 정보 덤프
ProfileInstallReceiver            → [exported, DUMP perm] Baseline Profile 설치/벤치마크
```

---

## 4. 보안 분석 요약

### 4.1 공격 표면 (Attack Surface)

| Receiver | 위험도 | 근거 |
|----------|--------|------|
| `FirebaseInstanceIdReceiver` | **Medium** | exported=true, c2dm permission으로 보호되나 FCM → 서비스 전달 체인 분석 필요 |
| `DiagnosticsReceiver` | Low | DUMP permission (adb/system only) |
| `ProfileInstallReceiver` | Low | DUMP permission (adb/system only) |
| `BuzzCustomReceiver` | **Medium** | exported=false이나 동일 UID 앱에서 sendBroadcast 가능. CAMPAIGN_ID 조작으로 캠페인 삭제 가능 |
| `locker.RestartReceiver` | Low-Med | priority=MAX_INT로 BOOT 선점. persistency 메커니즘 자체가 사용자 제어 우회 목적 |

### 4.2 Persistence 메커니즘

```
부팅/업데이트 시 자동 복구 체인:

BOOT_COMPLETED ──┬→ RestartReceiver (pop)    → Pop 광고 서비스 재시작
                 ├→ RestartReceiver (locker)  → 잠금화면 서비스 재시작 [MAX_INT priority]
                 └→ RescheduleReceiver        → WorkManager 작업 재스케줄

MY_PACKAGE_REPLACED ─┬→ RestartReceiver (pop)    → Pop 광고 서비스 재시작
                     └→ RestartReceiver (locker)  → 잠금화면 서비스 재시작
```

### 4.3 추가 조사 권장 사항

1. **`BuzzLocker.e()` 메서드 역분석** — 난독화된 잠금화면 서비스 시작 로직의 전체 흐름 파악
2. **`ReshowPopUseCase` 구현체** — 어떤 서비스를 시작하는지, 포그라운드/백그라운드 서비스 여부 확인
3. **FCM 메시지 핸들러 (`C2308m.k()`)** — 수신된 push 데이터로 동적 코드 로딩이나 URL 오픈 여부 확인
4. **`DEACTIVATE_UNTIL_REBOOT` SharedPreference** — 외부에서 값 조작 가능 여부 (backup agent, adb 등)
5. **동일 서명 앱 간 브로드캐스트** — BuzzCustomReceiver의 CAMPAIGN_ID 조작을 통한 광고 삭제 시나리오 PoC

---

> 본 문서는 JADX MCP를 통한 정적 분석 결과이며, 동적 분석(Frida hooking 등)으로 검증 필요

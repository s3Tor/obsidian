## Postbook 1-1

Step 1. 게시글 생성
<img width="980" height="932" alt="image" src="https://github.com/user-attachments/assets/d2c6fcf1-1120-47e1-a702-436def2d2260" />

Step 2. 내가 만든 게시글 수정 시도
<img width="1168" height="715" alt="image" src="https://github.com/user-attachments/assets/77108809-9269-4541-9a41-62ab733f4547" />

Step 3. URL에 Index값 확인 "id=5"
<img width="1340" height="934" alt="image" src="https://github.com/user-attachments/assets/e8569e0e-1f78-43fe-ae8e-da55a350136e" />

Step 4. "di=5 -> di=1"로 URL 변조 시도
<img width="1055" height="941" alt="image" src="https://github.com/user-attachments/assets/069e42cc-819d-437a-8289-1f72d5527de5" />

Step 5. 저장 시 flag값 획득 가능함
<img width="1196" height="612" alt="image" src="https://github.com/user-attachments/assets/9e7dc065-de9c-4eb9-b8f0-ce35aa4af97e" />

## Postbook 1-2

Step 1. 로그인 후 "Post timeline" 메뉴에 임의의 값 넣고 'Create post'버튼 클릭 
<img width="1107" height="1055" alt="image" src="https://github.com/user-attachments/assets/3b53bd2f-b481-4b00-bbd7-041049909173" />

Step 2. 요청 패킷 확인 시 파라미터 내 ID 값 확인가능
- user_id = 3 > user_id = 1로 변경
<img width="1487" height="993" alt="image" src="https://github.com/user-attachments/assets/0d71ecc3-41b1-4999-bdb8-937ad06c6a75" />

Step 3. 응답 패킷 내 flag 내용 확인 가능
<img width="1485" height="867" alt="image" src="https://github.com/user-attachments/assets/e2d22193-ee44-4353-95b9-b7c4ee3f7bc2" />


## Postbook 1-3
Step 1. 세션 쿠키 내 id 값 확인 시 MD5로 인코딩 되어 있음
- id=ccbc87e4b5ce2fe28308fd9f2a7baf3
<img width="1482" height="858" alt="image" src="https://github.com/user-attachments/assets/6a0e439d-3550-46b3-bf59-3fc22c111a54" />

Step 2. 디코딩 값 확인 시 "ccbc87e4b5ce2fe28308fd9f2a7baf3" 값은 3으로 확인 되어 1을 MD5로 인코딩 후 새로고침 시 관리자로 로그인 가능
<img width="1920" height="1112" alt="image" src="https://github.com/user-attachments/assets/104fe0eb-cefc-4765-92af-d8e90857d4fa" />


## Postbook 1-4
Step 1. 게시글 확인 시 URL내 id 파라미터 확인
<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/79dcb779-5d62-4078-a4a0-50732abff482" />

Step 2.  brute-force를 통해 id 파라미터에 1000개 정도 요청시 response 내 flag 확인 가능
<img width="1488" height="1104" alt="image" src="https://github.com/user-attachments/assets/a5b8d7e3-5f9d-4075-bbd7-ac3e7203ac0f" />


## Postbook 1-4
Step 1. 게시글 내 "user" 계정 확인
<img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/d91c78d4-40e7-4cbd-9b7b-5703195912c7" />

Step 2. User계정으로 로그인 시도
<img width="1477" height="1035" alt="image" src="https://github.com/user-attachments/assets/80677217-cd9e-4ede-99c2-b23becbd5e6a" />


Step 3. 요청 패킷 확인 시 Password 파라미터에 brute-force로 계정 패스워드 확인
<img width="1456" height="1038" alt="image" src="https://github.com/user-attachments/assets/aea04eb8-2890-444d-814f-3ba6f056cd04" />



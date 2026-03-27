import boto3

# 1. 자격 증명 정보 설정
access_key = "YOUR_ACCESS_KEY"
secret_key = "YOUR_SECRET_KEY"
session_token = "YOUR_SESSION_TOKEN"
region = "ap-northeast-2"

# 2. 세션 생성
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    aws_session_token=session_token,
    region_name=region
)

# 3. 예시: S3 서비스에 연결하여 버킷 리스트 확인
s3 = session.client('s3')
try:
    response = s3.list_buckets()
    print("접속 성공! 버킷 목록:")
    for bucket in response['Buckets']:
        print(f" - {bucket['Name']}")
except Exception as e:
    print(f"접속 실패: {e}")

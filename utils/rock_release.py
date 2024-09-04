import fcntl
import os

def check_and_release_lock(lock_file):
    if os.path.exists(lock_file):
        with open(lock_file, 'r+') as lock:
            try:
                # 락 상태 확인 (락을 획득하지 않으면 이 부분에서 BlockingIOError 발생)
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                print("No active lock. Lock acquired successfully.")
                # 락을 해제하여 파일을 사용할 수 있도록 함
                fcntl.flock(lock, fcntl.LOCK_UN)
            except BlockingIOError:
                print("Lock is active. Releasing the lock.")
                # 이미 락이 걸려 있으면 락 해제 시도
                fcntl.flock(lock, fcntl.LOCK_UN)
    else:
        print("Lock file does not exist.")

# 락 파일 경로
lock_file = "/tmp/gpu_task.lock"

# 락 상태 확인 및 강제 해제
check_and_release_lock(lock_file)

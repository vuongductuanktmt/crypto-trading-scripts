import rarfile
import itertools
import threading
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import os

# ================== PASSWORD TESTING ==================
def try_password(rar_path, password, result_queue, attempt_count):
    """
    Attempt to extract a RAR file with a given password.

    Args:
        rar_path (str): Path to the RAR file.
        password (str): Password to test.
        result_queue (Queue): Queue to store successful results.
        attempt_count (int): Number of attempts made by this thread.

    Returns:
        bool: True if password is correct, False otherwise.
    """
    try:
        with rarfile.RarFile(rar_path) as rar:  # Create new instance per thread
            rar.setpassword(password)
            rar.extractall()
            result_queue.put((True, password, attempt_count))
            return True
    except Exception:
        return False

# ================== THREAD WORKER ==================
def worker(rar_path, passwords, result_queue, lock, password_counter):
    """
    Worker function for each thread to test a chunk of passwords.

    Args:
        rar_path (str): Path to the RAR file.
        passwords (list): List of passwords to test.
        result_queue (Queue): Queue to store successful results.
        lock (threading.Lock): Lock for thread-safe counter updates.
        password_counter (list): Shared counter for total attempts.
    """
    local_count = 0
    for password in passwords:
        local_count += 1
        if try_password(rar_path, password, result_queue, local_count):
            with lock:
                password_counter[0] += local_count
            return
        with lock:
            password_counter[0] += 1
            print(f"Password '{password}' failed. Attempt: {password_counter[0]}")

# ================== BRUTE FORCE FUNCTION ==================
def brute_force_rar(rar_path, phone_numbers, num_threads=2):
    """
    Brute-force a RAR file password using combinations of provided phone numbers.

    Args:
        rar_path (str): Path to the RAR file.
        phone_numbers (list): List of strings to generate password combinations.
        num_threads (int): Number of threads to use (default: 2).

    Returns:
        str or None: Correct password if found, None otherwise.
    """
    # Check if RAR file exists
    if not os.path.exists(rar_path):
        print(f"Error: RAR file '{rar_path}' does not exist.")
        return None

    # Verify RAR file is valid
    try:
        with rarfile.RarFile(rar_path) as rar:
            pass
    except Exception as e:
        print(f"Error opening RAR file: {e}")
        return None

    # Generate all password combinations
    all_passwords = []
    for r in range(2, 4):  # Combinations of length 2 to 3
        for combo in itertools.permutations(phone_numbers, r):
            password = ''.join(combo)
            all_passwords.append(password)

    total_passwords = len(all_passwords)
    print(f"Total passwords to test: {total_passwords}")

    # Split passwords into chunks for threading
    chunk_size = (total_passwords + num_threads - 1) // num_threads
    password_chunks = [all_passwords[i:i + chunk_size] for i in range(0, total_passwords, chunk_size)]

    # Initialize queue, lock, and counter
    result_queue = Queue()
    lock = threading.Lock()
    password_counter = [0]  # Mutable list for shared counter

    # Run threads
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(worker, rar_path, chunk, result_queue, lock, password_counter)
            for chunk in password_chunks
        ]

        # Check results
        while not result_queue.empty() or any(f.running() for f in futures):
            if not result_queue.empty():
                success, password, count = result_queue.get()
                if success:
                    print(f"Success! Password found: {password}")
                    print(f"Total attempts: {password_counter[0]}")
                    return password

    print("Password not found.")
    print(f"Total attempts: {password_counter[0]}")
    return None

# ================== MAIN EXECUTION ==================
if __name__ == "__main__":
    rar_file = "./[filename].rar"  # Path to RAR file
    list = ["12345", "abcd"]  # List of strings for password combinations
    brute_force_rar(rar_file, phone_numbers, num_threads=2)

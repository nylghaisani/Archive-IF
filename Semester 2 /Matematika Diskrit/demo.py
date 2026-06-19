import pandas as pd
import random

def Extended_GCD(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = Extended_GCD(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def Mod_Inverse(a, m):
    gcd, x, y = Extended_GCD(a, m)
    return (x % m + m) % m

def CRT(remainders, moduli):
    M = 1
    for m_val in moduli:
        M *= m_val

    total = 0
    for r, m_val in zip(remainders, moduli):
        Mi = M // m_val
        total += r * Mi * Mod_Inverse(Mi, m_val)
    return total % M

#CRYPTOGRAPHIC CORE PIPELINE (Asmuth-Bloom Threshold Scheme)

def encrypt_secret(S, m0, moduli):
    # Batas gamma diperketat agar S_prime tidak melampaui batas atas CRT (M_k)
    gamma = random.randint(1, 50)
    S_prime = S + gamma * m0
    return [S_prime % mi for mi in moduli]

#MAIN SIMULATION DISPATCHER

def main():
    print("=" * 75)
    print("  LAGRANGE & CRT-BASED SECURE MULTI-PARTY COMPUTATION SYSTEM DEMO")
    print("        FACULTY OF ELECTRICAL ENGINEERING AND INFORMATICS - ITB")
    print("=" * 75)

    #AMBANG BATAS PARAMETER (k=3, n=5) - UPGRADED m0 TO PREVENT OVERFLOW
    #m0 diubah menjadi 20011 agar muat menampung total jumlahan data skala besar
    m0 = 20011
    m_servers = [20021, 20023, 20029, 20047, 20051]
    k = 3

    print("[ PHASE 1: DATA INGESTION & PREPROCESSING ]")
    print("[+] Reading 'student_lifestyle_dataset (1).xlsx' using pandas...")
    try:
        df = pd.read_excel('student_lifestyle_dataset (1).xlsx')
    except:
        df = pd.read_csv('student_lifestyle_dataset (1).xlsx - student_lifestyle_dataset.csv')

    N = 5
    raw_study = df['Study_Hours_Per_Day'].head(N).tolist()
    raw_gpa = df['GPA'].head(N).tolist()

    #Fixed-Point Scaling (Faktor Skala alpha = 100)
    scale_factor = 100
    study_vector = [int(round(val * scale_factor)) for val in raw_study]
    gpa_vector = [int(round(val * scale_factor)) for val in raw_gpa]

    print(f"[+] Successfully loaded top {N} student profiles.")
    print(f"    - Plaintext Study Vector : {raw_study}")
    print(f"    - Plaintext GPA Vector   : {raw_gpa}")
    print(f"    - Scaled Integer Study   : {study_vector}")
    print(f"    - Scaled Integer GPA     : {gpa_vector}\n")

    #DATA SHARDING/DISTRIBUSI RESIDU
    print("[ PHASE 2: DISTRIBUTED CRYPTOGRAPHIC SHARDING ]")
    server_study_shares = {i: [] for i in range(5)}
    server_gpa_shares = {i: [] for i in range(5)}

    for secret in study_vector:
        shares = encrypt_secret(secret, m0, m_servers)
        for i in range(5):
            server_study_shares[i].append(shares[i])

    for secret in gpa_vector:
        shares = encrypt_secret(secret, m0, m_servers)
        for i in range(5):
            server_gpa_shares[i].append(shares[i])

    print("[*] Privacy Status: Cleartext obfuscated. Individual values are now residues.")
    print(f"    - Node 1 (mod {m_servers[0]}) Study Shares : {server_study_shares[0]}")
    print(f"    - Node 1 (mod {m_servers[0]}) GPA Shares   : {server_gpa_shares[0]}\n")

    #AGREGASI HOMOMORFIK LOKAL (TANPA ANTAR-SERVER)
    print("[ PHASE 3: ISOLATED LOCAL HOMOMORPHIC AGGREGATION ]")
    local_study_sums = [sum(server_study_shares[i]) % m_servers[i] for i in range(5)]
    local_gpa_sums = [sum(server_gpa_shares[i]) % m_servers[i] for i in range(5)]

    for i in range(5):
        print(f"    [-] Server {i+1} independent accumulator -> Study Mod {m_servers[i]}: {local_study_sums[i]} | GPA Mod {m_servers[i]}: {local_gpa_sums[i]}")
    print("")

    #REKONSTRUKSI GLOBAL MENGGUNAKAN CRT
    print(f"[ PHASE 4: GLOBAL CRT DECAPSULATION USING THRESHOLD k={k} ]")
    print(f"[*] Pooling partial aggregates from Node 1, Node 2, and Node 3...")
    chosen_moduli = m_servers[:k]
    chosen_study_sums = local_study_sums[:k]
    chosen_gpa_sums = local_gpa_sums[:k]

    #Menyelesaikan sistem kongruensi linear simultan via CRT
    reconstructed_study_prime = CRT(chosen_study_sums, chosen_moduli)
    reconstructed_gpa_prime = CRT(chosen_gpa_sums, chosen_moduli)

    #Blinding factor menggunakan modulo m0
    final_study_sum = reconstructed_study_prime % m0
    final_gpa_sum = reconstructed_gpa_prime % m0

    #Menghitung rata-rata deskriptif akhir
    computed_study_mean = (final_study_sum / scale_factor) / N
    computed_gpa_mean = (final_gpa_sum / scale_factor) / N

    #Perhitungan baseline kontrol
    baseline_study_mean = sum(raw_study) / N
    baseline_gpa_mean = sum(raw_gpa) / N

    #DISPLAY FINAL STRUCTURAL VERIFICATION REPORT
    print("\n" + "=" * 75)
    print("                       FINAL COMPUTATIONAL REPORT                       ")
    print("=" * 75)
    print(f"  METRIC INDICATOR      │   DECENTRALIZED CRT   │   PLAINTEXT BASELINE ")
    print("-" * 75)
    print(f"  Study Hours Total     │   {final_study_sum:<19} │   {sum(study_vector):<18}")
    print(f"  Study Hours Mean      │   {computed_study_mean:<19.2f} │   {baseline_study_mean:<18.2f}")
    print(f"  GPA Cumulative Total  │   {final_gpa_sum:<19} │   {sum(gpa_vector):<18}")
    print(f"  GPA Cumulative Mean   │   {computed_gpa_mean:<19.2f} │   {baseline_gpa_mean:<18.2f}")
    print("-" * 75)

    if abs(computed_study_mean - baseline_study_mean) < 1e-5 and abs(computed_gpa_mean - baseline_gpa_mean) < 1e-5:
        print("  [ STATUS ] SUCCESS: Privacy-Preserving Integrity Verified (0.00% Error).")
    else:
        print("  [ STATUS ] ERROR: Mathematical overflow or discrepancy detected.")
    print("=" * 75)

if __name__ == "__main__":
    main()

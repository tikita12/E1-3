from time import perf_counter
import json


def read_matrix():
    pattern = []
    while len(pattern) < 3:
        line = input(f"{len(pattern) + 1}번째 행을 입력하세요: ")

        row = []
        try:
            for value in line.split():
                row.append(float(value))
        except ValueError:
            print("숫자만 입력하세요")
            continue

        if len(row) != 3:
            print("한 행에 숫자 3개를 입력하세요.")
            continue

        pattern.append(row)
    return pattern

def mac(pattern, matrix_filter):
    score = 0.0
    for row in range(len(pattern)):
        for column in range(len(pattern[row])):
            score += pattern[row][column] * matrix_filter[row][column]
    return score

def measure_mac_ms(pattern, matrix_filter):
    start = perf_counter()
    for _ in range(10):
        mac(pattern, matrix_filter)
    elapsed = perf_counter() - start
    return elapsed * 1000 / 10

def normalize_label(label):
    labels = {"+": "Cross", "cross": "Cross", "x": "X"}
    return labels[label.strip().lower()]

def run_manual():

    print("필터 A를 입력하세요")
    filter_a = read_matrix()
    print("필터 B를 입력하세요")
    filter_b = read_matrix()
    print("판정할 패턴을 입력하세요")
    pattern = read_matrix()

    a_score = mac(pattern, filter_a)
    b_score = mac(pattern, filter_b)
    print("A점수 :", a_score, "B점수 :", b_score)

    if abs(a_score - b_score) < 1e-9 :
        print("판정 불가")
    elif a_score > b_score:
        print("판정 A")
    else:
        print("판정 B")

    a_ms = measure_mac_ms(pattern, filter_a)
    b_ms = measure_mac_ms(pattern, filter_b)
    print("필터 A의 MAC 1회 평균시간(ms):", a_ms)
    print("필터 B의 MAC 1회 평균시간(ms):", b_ms)




print("1. 직접입력")
print("2. JSON 파일 분석")
choice = input("번호를 입력하세요 :").strip()

if choice == "1":
    run_manual()
elif choice == "2":
    with open("data.json", encoding="utf-8-sig") as file:
        data = json.load(file)

    passed = 0
    failed_cases = []
    for case_name, case in data["patterns"].items():
        print(case_name)
        pattern = case["input"]
        size_key = case_name.rsplit("_", 1)[0]
        filters = {}
        for name, matrix in data["filters"][size_key].items():
            filters[normalize_label(name)] = matrix

        cross_score = mac(pattern, filters["Cross"])
        x_score = mac(pattern, filters["X"])
        print("십자가 점수:", cross_score, "X 점수:", x_score)

        if abs(cross_score - x_score) < 1e-9:
            result = "UNDECIDED"
        elif cross_score > x_score:
            result = "Cross"
        else:
            result = "X"

        expected = normalize_label(case["expected"])

        print("내 판정:", result, "예상 정답:", expected)
        if result == expected:
            print("PASS")
            passed += 1
        else:
            print("FAIL")
            reason = "두 점수의 차이가 1e-9 미만" if result == "UNDECIDED" else "예상 정답과 다른 판정"
            failed_cases.append(f"{case_name}: {reason} (판정 {result}, 예상 {expected})")
    total = len(data["patterns"])
    print("전체:", total, "통과:", passed, "실패:", total - passed)
    for failed_case in failed_cases:
        print(failed_case)
    print("크기 | MAC 횟수 | 10회 평균 시간(ms)")
    cross_3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    average_ms = measure_mac_ms(cross_3, cross_3)
    print(f"3×3 | 9회 | {average_ms:.6f}")    
    for size in [5, 13, 25]:
        pattern = data["patterns"][f"size_{size}_1"]["input"]
        cross_filter = data["filters"][f"size_{size}"]["cross"]
        average_ms = measure_mac_ms(pattern, cross_filter)
        print(f"{size}×{size} | {size * size}회 | {average_ms:.6f}")
   
else:
    print("1 또는 2를 입력하세요")


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


    start = perf_counter()
    for _ in range(10):
        mac(pattern, filter_a)
    elapsed = perf_counter() - start

    average_ms = elapsed * 1000 / 10
    print("필터 A의 MAC 1회 평균시간(ms):", average_ms)

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
        filters = data["filters"][size_key]

        cross_score = mac(pattern, filters["cross"])
        x_score = mac(pattern, filters["x"])
        print("십자가 점수:", cross_score, "X 점수:", x_score)

        if abs(cross_score - x_score) < 1e-9:
            result = "UNDECIDED"
        elif cross_score > x_score:
            result = "Cross"
        else:
            result = "X"

        labels = {"x": "X", "+": "Cross"}
        expected = labels[case["expected"]]

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
else:
    print("1 또는 2를 입력하세요")


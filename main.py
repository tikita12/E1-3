import json
import math
import re
from time import perf_counter

EPSILON = 1e-9
REPEATS = 10


def read_matrix(size=3):
    matrix = []
    while len(matrix) < size:
        line = input(f"{len(matrix) + 1}번째 행을 입력하세요: ")
        try:
            row = [float(value) for value in line.split()]
        except ValueError:
            print("숫자만 입력하세요.")
            continue
        if len(row) != size:
            print(f"한 행에 숫자 {size}개를 입력하세요.")
            continue
        if not all(math.isfinite(value) for value in row):
            print("각 칸에 유한한 숫자를 입력하세요.")
            continue
        matrix.append(row)
    return matrix


def validate_matrix(matrix, size, name):
    if not isinstance(matrix, list) or len(matrix) != size:
        raise ValueError(f"{name}의 행 수는 {size}여야 합니다.")
    for number, row in enumerate(matrix, 1):
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(f"{name}의 {number}번째 행에는 {size}개 값이 필요합니다.")
        for value in row:
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ValueError(f"{name}의 {number}번째 행에는 유한한 숫자가 필요합니다.")


def mac(pattern, matrix_filter):
    """같은 칸의 두 값을 곱해 누적하고 필터 하나의 점수를 반환한다."""
    score = 0.0
    for row in range(len(pattern)):
        for column in range(len(pattern[row])):
            score += pattern[row][column] * matrix_filter[row][column]
    if not math.isfinite(score):
        raise ValueError("MAC 점수가 실수로 표현할 수 있는 범위를 벗어났습니다.")
    return score


def measure_mac_ms(pattern, matrix_filter):
    start = perf_counter()
    for _ in range(REPEATS):
        mac(pattern, matrix_filter)
    elapsed = perf_counter() - start
    return elapsed * 1000 / REPEATS


def normalize_label(label):
    """필터 이름과 정답을 같은 표기로 맞춰 철자 차이로 인한 오판을 막는다."""
    labels = {"+": "Cross", "cross": "Cross", "x": "X"}
    if isinstance(label, str) and label.strip().lower() in labels:
        return labels[label.strip().lower()]
    raise ValueError(f"알 수 없는 라벨 {label!r}")


def decide(first_score, second_score, first_label, second_label):
    if abs(first_score - second_score) < EPSILON:
        return "UNDECIDED"
    return first_label if first_score > second_score else second_label


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
    result = decide(a_score, b_score, "A", "B")
    print("판정 불가" if result == "UNDECIDED" else f"판정 {result}")
    print("필터 A의 MAC 1회 평균시간(ms):", measure_mac_ms(pattern, filter_a))
    print("필터 B의 MAC 1회 평균시간(ms):", measure_mac_ms(pattern, filter_b))


def read_case(case_name, case, filter_groups):
    match = re.fullmatch(r"size_([1-9][0-9]*)_([0-9]+)", case_name)
    if match is None:
        raise ValueError("패턴 이름 형식 오류 (예: size_13_2)")
    size = int(match.group(1))
    if not isinstance(case, dict) or "input" not in case or "expected" not in case:
        raise ValueError("패턴에는 input과 expected가 필요합니다.")
    pattern = case["input"]
    validate_matrix(pattern, size, "입력")
    expected = normalize_label(case["expected"])

    group = filter_groups.get(f"size_{size}")
    if not isinstance(group, dict):
        raise ValueError(f"size_{size} 필터 묶음이 없거나 형식이 잘못됐습니다.")
    filters = {}
    for name, matrix in group.items():
        label = normalize_label(name)
        if label in filters:
            raise ValueError(f"{label} 필터가 중복됐습니다.")
        validate_matrix(matrix, size, label)
        filters[label] = matrix
    for label in ("Cross", "X"):
        if label not in filters:
            raise ValueError(f"{label} 필터가 없습니다.")
    return pattern, expected, filters


def run_json():
    with open("data.json", encoding="utf-8-sig") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("data.json의 전체 내용은 JSON 객체여야 합니다.")
    for key in ("filters", "patterns"):
        if not isinstance(data.get(key), dict):
            raise ValueError(f"data.json에서 {key} 항목을 찾을 수 없거나 형식이 잘못됐습니다.")

    failures = []
    samples = {}
    for name, case in data["patterns"].items():
        print(name)
        try:
            pattern, expected, filters = read_case(name, case, data["filters"])
            cross_score = mac(pattern, filters["Cross"])
            x_score = mac(pattern, filters["X"])
        except (ValueError, OverflowError) as error:
            print("FAIL", error)
            failures.append((name, "-", "-", "-", "-", str(error)))
            continue

        samples.setdefault(len(pattern), (pattern, filters["Cross"]))
        result = decide(cross_score, x_score, "Cross", "X")
        print("십자가 점수:", cross_score, "X 점수:", x_score)
        print("내 판정:", result, "예상 정답:", expected)
        if result == expected:
            print("PASS")
        else:
            print("FAIL")
            reason = f"두 점수 차이가 {EPSILON:g} 미만" if result == "UNDECIDED" else "예상 정답과 다른 판정"
            failures.append((name, cross_score, x_score, abs(cross_score - x_score),
                             f"{result} / {expected}", reason))

    total = len(data["patterns"])
    print("전체:", total, "통과:", total - len(failures), "실패:", len(failures))
    if failures:
        print("실패 케이스 | Cross 점수 | X 점수 | 점수 차이 | 판정 / 예상 | 사유")
        for failure in failures:
            print(*failure, sep=" | ")

    print(f"크기 | MAC 횟수 | {REPEATS}회 평균 시간(ms)")
    cross_3 = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    samples.setdefault(3, (cross_3, cross_3))
    for size in sorted({5, 13, 25}.union(samples)):
        if size not in samples:
            print(f"{size}×{size} | {size * size}회 | 측정할 유효한 입력 없음")
            continue
        pattern, cross_filter = samples[size]
        average_ms = measure_mac_ms(pattern, cross_filter)
        print(f"{size}×{size} | {size * size}회 | {average_ms:.6f}")


def main():
    print("====================\n1. 직접입력\n2. JSON 파일 분석\n====================")
    while True:
        choice = input("번호를 입력하세요 :").strip()
        if choice == "1":
            run_manual()
            return
        if choice == "2":
            run_json()
            return
        print("1 또는 2를 입력하세요.")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError:
        raise SystemExit("현재 폴더에 data.json이 없습니다.")
    except json.JSONDecodeError:
        raise SystemExit("data.json의 JSON 문법을 확인하세요.")
    except EOFError:
        raise SystemExit("입력이 끝났습니다. 필요한 행을 모두 입력하세요.")
    except (ValueError, OSError, OverflowError) as error:
        raise SystemExit(str(error))

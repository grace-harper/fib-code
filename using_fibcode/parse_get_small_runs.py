def main():
    getsmallruns = "/Users/graceharperibm/correcting/Fib/ClassicFibInfo/logfib/valid)get_small_runs/get_small_runs.log"
    data = ""
    with open(getsmallruns, "r") as f:
        data = f.read()

    separate_runs = data.split("INFO - ==================================Running")[1:]
    L = "L"
    p = "p"
    H = "H"
    V = "V"
    N = "N"
    run_info = {}
    for indx, run in enumerate(separate_runs):
        print(f"\n\n\n\nRUN\n\n\{run}")
        info, res = run.split("--->")  #  L=8, p=0.15,  H:V:N=0.0:0.0:0.0
        res = res.strip().split()[0].strip()
        print("res is", res)
        sub_dict = {}
        values = res.split(",")
        for value in values:
            if len(value) < 3:
                continue
            print("ricochet")
            print(value)
            print(value.split("="))
            k, v = value.split("=")
            k = k.strip()
            v = v.strip()
            if ":" in v:
                sv1, sv2, sv3 = v.split(":")
                sub_dict[H] = float(sv1)
                sub_dict[V] = float(sv2)
                sub_dict[N] = float(sv3)
            else:
                if k == L:
                    sub_dict[L] = int(v)
                else:
                    sub_dict[k] = float(v)
        print(sub_dict)


if __name__ == "__main__":
    main()
# split along  "================================== " to get run chunks
# per chunk:
# split along "FINISHED LP: " and grab results: " L=8, p=0.15,  H:V:N=0.0:0.0:0.0"
# split along error_board (error_board:) to (2023)
# for error board, make metanumpy array
# start at [[, end ]]
# for line: make new nparray & add split on whitespace and add ints until  ]  then add array to meta

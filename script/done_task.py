import json
import sys
import warnings

# 仕様: 第一引数を部分文字列として含むタスクを全て done:True にする


# /done と空白を削除
def get_name(body: str) -> str:
    body = body.replace("/done", "").strip()
    return body


def main():
    remove_target = get_name(sys.argv[1])

    # 空文字列だとやばすぎるので、これは skip
    if remove_target == "":
        warnings.warn("空文字列は全てを close してしまうので、スキップします")
        with open("message.txt", "w") as f:
            f.write("空文字列は全てを close してしまうので、スキップします")
        return

    message = ""

    with open("reminds/tasks.json", "r") as f:
        tasks = json.load(f)

        # remove_target を含むタスクを全て done にする
        for task in tasks:
            if remove_target in task["task"]:
                task["done"] = True

                message += f"{task['task']} を close しました！\n"

    with open("message.txt", "w") as f:
        f.write(message)

    with open("reminds/tasks.json", "w") as f:
        json.dump(tasks, f, indent=4)


if __name__ == "__main__":
    main()

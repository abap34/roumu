import json
import sys
import warnings

import tabulate
from task import Task


def load_tasks() -> list[Task]:
    with open("reminds/tasks.json", "r") as f:
        task = json.load(f)

    return [Task.from_dict(t) for t in task]


def task_list_message(tasks: list[Task]) -> str:
    """
     task_list_message(tasks: list[Task]) -> str

    タスクのリストを受け取って、いい感じのメッセージを返す
    """
    table = []
    for task in tasks:
        task_dict = task.to_dict(exclude={"id"})

        # issue_number の前に "#" をつける
        task_dict["issue_number"] = f"#{task_dict['issue_number']}"

        # done を　✅ に変換
        task_dict["done"] = "✅" if task_dict["done"] else ""

        table.append(task_dict.values())

    return tabulate.tabulate(
        table, headers=task.to_dict(exclude={"id"}).keys(), tablefmt="github"
    )


def main():
    tasks = load_tasks()

    # 残りのタスクを全て抽出
    remaining_tasks = [task for task in tasks if not task.done]
    message = task_list_message(remaining_tasks)

    with open("message.txt", "w") as f:
        f.write(message)


if __name__ == "__main__":
    main()

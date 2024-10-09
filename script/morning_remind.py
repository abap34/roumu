import json
from task import Task
import sys
import tabulate
import warnings

def load_tasks() -> list[Task]:
    with open('reminds/tasks.json', 'r') as f:
        task = json.load(f)

    return [Task.from_dict(t) for t in task]

def task_list_message(tasks: list[Task]) -> str:
    """
     task_list_message(tasks: list[Task]) -> str

    タスクのリストを受け取って、いい感じのメッセージを返す
    """
    table = []
    for task in tasks:
        table.append(
            task.to_dict(
                exclude={"id", "done"}).values()
        )

    return tabulate.tabulate(
        table,
        headers=task.to_dict(exclude={"id", "done"}).keys(),
        tablefmt="grid"
    )



def main():
    github_event_type = sys.argv[1]
    if github_event_type == "issue_comment":
        with open('comment.txt', 'r') as f:
            if not '/tasks' in f.read():
                warnings.warn("/tasks が含まれていません。スキップします。")
                return
    tasks = load_tasks()

    # 残りのタスクを全て抽出
    remaining_tasks = [task for task in tasks if not task.done]
    message = task_list_message(remaining_tasks)
  
    with open("message.txt", "w") as f:
        f.write(message)

if __name__ == "__main__":
    main()
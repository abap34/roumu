from dataclasses import dataclass
from cron import CronSetting
import uuid
from datetime import datetime

@dataclass
class Task:
    id: uuid.UUID
    task: str
    issue_number: int
    deadline: datetime
    remind: CronSetting
    done: bool = False

    def to_dict(self, exclude: set[str] = set()) -> dict:
        return {
            k: v
            for k, v in self.__dict__.items()
            if k not in exclude
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        return cls(
            id=uuid.UUID(d["id"]),
            task=d["task"],
            issue_number=d["issue_number"],
            deadline=datetime.fromisoformat(d["deadline"]),
            remind=CronSetting.from_str(d["remind"]),
            done=d["done"],
        )
    

    
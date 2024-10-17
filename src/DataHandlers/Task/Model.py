
# Task Model
# task
#   _id: str (uuid) (primary key)
#   key: str
#   title: str
#   description: str
#   status: str
#   priority: str
#   due_date: datetime
#   created_at: datetime
#   updated_at: datetime
#   color: str
#   tags: List[str]
#   category: str

class Task:
    def __init__(self, _id, key, title, description, status, priority, due_date, created_at, updated_at, color, tags, category):
        self._id = _id
        self.key = key
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.due_date = due_date
        self.created_at = created_at
        self.updated_at = updated_at
        self.color = color
        self.tags = tags
        self.category = category
    
    def __str__(self):
        return f"Task: {self.key} - {self.title}"
    
    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "_id": self._id,
            "key": self.key,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "color": self.color,
            "tags": self.tags,
            "category": self.category
        }

from dataclasses import dataclass
from typing import List

@dataclass
class Course:
	title: str
	course_id: int

@dataclass
class Link:
	text: str
	url: str

@dataclass
class TopicItem:
	title: str
	description: str
	links: List[Link]


@dataclass
class Topic:
	title: str
	topic_items: List[TopicItem]

@dataclass
class Plan:
	topics: List[Topic]

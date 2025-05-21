import queue
from .config import SOFTWARE_QUEUES

queues = {name: queue.Queue() for name in SOFTWARE_QUEUES}

from kafka import KafkaConsumer
import json

topic = 'face_events'


consumer = KafkaConsumer(
    topic,
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",        # start from beginning if no committed offset
    enable_auto_commit=True,
    group_id="demo-group",               # consumers with same group share work
    value_deserializer=lambda v: json.loads(v.decode("utf-8"))
)


print("Listening for messages...")
for message in consumer:
    print(
        f"Received: {message.value} "
        f"(partition={message.partition}, offset={message.offset})"
    )
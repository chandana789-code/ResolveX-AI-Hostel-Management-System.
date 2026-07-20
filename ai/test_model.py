from ai.classifier import predict_priority

tests = [

    ("Water Leakage",
     "Water leaking continuously from ceiling"),

    ("Gas Leak",
     "Strong smell of gas in kitchen"),

    ("Fan Repair",
     "Ceiling fan not rotating"),

    ("Switch Board",
     "Switch board is damaged"),

    ("WiFi Slow",
     "Internet speed is slow"),

    ("Dustbin",
     "Dustbin is overflowing")
]

for title, desc in tests:

    print(title)

    print(predict_priority(title, desc))

    print("-------------------")
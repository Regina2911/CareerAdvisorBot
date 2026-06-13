def get_recommendation(answers):

    scores = {
        "Программирование": 0,
        "Дизайн": 0,
        "Менеджмент": 0,
        "Аналитика": 0
    }

    text = " ".join(answers).lower()

    if "программирование" in text:
        scores["Программирование"] += 3

    if "информатика" in text:
        scores["Программирование"] += 2

    if "математика" in text:
        scores["Аналитика"] += 2

    if "анализировать" in text:
        scores["Аналитика"] += 3

    if "общение" in text:
        scores["Менеджмент"] += 3

    if "общаться" in text:
        scores["Менеджмент"] += 2

    if "творчество" in text:
        scores["Дизайн"] += 3

    best = max(scores, key=scores.get)

    return best